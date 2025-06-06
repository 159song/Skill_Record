import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Optional


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, embed_size: int, num_heads: int) -> None:
        super(MultiHeadSelfAttention, self).__init__()
        assert (
            embed_size % num_heads == 0
        ), "Embedding size must be divisible by num_heads"

        self.embed_size: int = embed_size
        self.num_heads: int = num_heads
        self.head_dim: int = embed_size // num_heads

        self.values: nn.Linear = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.keys: nn.Linear = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.queries: nn.Linear = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.fc_out: nn.Linear = nn.Linear(embed_size, embed_size)

    def forward(
        self, values: Tensor, keys: Tensor, query: Tensor, mask: Optional[Tensor]
    ) -> Tensor:
        N: int = query.shape[0]
        value_len: int = values.shape[1]
        key_len: int = keys.shape[1]
        query_len: int = query.shape[1]

        # Split embedding into self.num_heads pieces
        values = values.reshape(N, value_len, self.num_heads, self.head_dim)
        keys = keys.reshape(N, key_len, self.num_heads, self.head_dim)
        queries = query.reshape(N, query_len, self.num_heads, self.head_dim)

        values = self.values(values)
        keys = self.keys(keys)
        queries = self.queries(queries)

        energy = torch.einsum("nqhd,nkhd->nhqk", [queries, keys])
        if mask is not None:
            energy = energy.masked_fill(mask == 0, float("-1e20"))

        attention = torch.softmax(energy / (self.embed_size ** (1 / 2)), dim=3)

        out = torch.einsum("nhql,nlhd->nqhd", [attention, values]).reshape(
            N, query_len, self.embed_size
        )

        out = self.fc_out(out)
        return out


class TransformerBlock(nn.Module):
    def __init__(
        self, embed_size: int, num_heads: int, dropout: float, forward_expansion: int
    ) -> None:
        super(TransformerBlock, self).__init__()
        self.attention: MultiHeadSelfAttention = MultiHeadSelfAttention(
            embed_size, num_heads
        )
        self.norm1: nn.LayerNorm = nn.LayerNorm(embed_size)
        self.norm2: nn.LayerNorm = nn.LayerNorm(embed_size)
        self.feed_forward: nn.Sequential = nn.Sequential(
            nn.Linear(embed_size, forward_expansion * embed_size),
            nn.ReLU(),
            nn.Linear(forward_expansion * embed_size, embed_size),
        )
        self.dropout: nn.Dropout = nn.Dropout(dropout)

    def forward(
        self, value: Tensor, key: Tensor, query: Tensor, mask: Optional[Tensor]
    ) -> Tensor:
        attention = self.attention(value, key, query, mask)
        x = self.dropout(self.norm1(attention + query))
        forward = self.feed_forward(x)
        out = self.dropout(self.norm2(forward + x))
        return out


class AudioTransformer(nn.Module):
    def __init__(
        self,
        input_dim: int,
        num_heads: int,
        num_layers: int,
        forward_expansion: int,
        dropout: float,
        output_dim: int,
    ) -> None:
        super(AudioTransformer, self).__init__()
        self.embed_size: int = input_dim
        self.layers: nn.ModuleList = nn.ModuleList(
            [
                TransformerBlock(
                    input_dim,
                    num_heads,
                    dropout=dropout,
                    forward_expansion=forward_expansion,
                )
                for _ in range(num_layers)
            ]
        )
        self.fc_out: nn.Linear = nn.Linear(input_dim, output_dim)
        self.dropout: nn.Dropout = nn.Dropout(dropout)

    def forward(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        for layer in self.layers:
            x = layer(x, x, x, mask)
        x = self.fc_out(x[:, 0, :])  # Use the first token for classification
        return x
