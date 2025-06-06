import argparse
import yaml
from data.dataset import AudioDataset
from torch.utils.data import DataLoader
import torchaudio
import torch
from model import AudioTransformer
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Args:
    config: str
    learning_rate: float
    batch_size: int
    train_audio_dir: str
    val_audio_dir: str
    shuffle: bool
    num_epochs: int
    model_dir: str
    device: str
    input_dim: int
    num_heads: int
    num_layers: int
    forward_expansion: int
    dropout: float
    output_dim: int


# 读取 YAML 配置文件
def load_config(config_file: str) -> dict:
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


# 设置命令行参数解析
def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Train a deep learning model.")
    parser.add_argument(
        "-config",
        type=str,
        default="config.yaml",
        help="Path to the config file",
    )
    parser.add_argument("-learning_rate", type=float, help="Learning rate for training")
    parser.add_argument("-batch_size", type=int, help="Batch size for training")
    parser.add_argument(
        "-train_audio_dir", type=str, help="Path to the train audio directory"
    )
    parser.add_argument(
        "-val_audio_dir", type=str, help="Path to the val audio directory"
    )
    parser.add_argument("-shuffle", type=bool, help="Whether to shuffle the data")
    parser.add_argument("-num_epochs", type=int, help="Number of training epochs")
    parser.add_argument("-model_dir", type=str, help="Path of model")
    parser.add_argument(
        "-device",
        type=str,
        default="cpu",
        help="Device to run the training on (e.g., 'cpu' or 'cuda')",
    )
    parser.add_argument("-input_dim", type=int, default=16, help="Input dimension")
    parser.add_argument(
        "-num_heads", type=int, default=8, help="Number of attention heads"
    )
    parser.add_argument(
        "-num_layers", type=int, default=6, help="Number of transformer layers"
    )
    parser.add_argument(
        "-forward_expansion", type=int, default=4, help="Forward expansion factor"
    )
    parser.add_argument("-dropout", type=float, default=0.1, help="Dropout rate")
    parser.add_argument("-output_dim", type=int, default=10, help="Output dimension")
    args = parser.parse_args()

    return Args(
        config=args.config,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        train_audio_dir=args.train_audio_dir,
        val_audio_dir=args.val_audio_dir,
        shuffle=args.shuffle,
        num_epochs=args.num_epochs,
        model_dir=args.model_dir,
        device=args.device,
        input_dim=args.input_dim,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        forward_expansion=args.forward_expansion,
        dropout=args.dropout,
        output_dim=args.output_dim,
    )


# 定义训练函数
def train_one_epoch(
    model: torch.nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: torch.nn.Module,
    device: str,
) -> float:
    model.train()
    total_loss = 0.0
    for batch in dataloader:
        (anchor, positive, negative), (anchor_mask, positive_mask, negative_mask) = (
            batch
        )
        anchor, positive, negative = (
            anchor.to(device),
            positive.to(device),
            negative.to(device),
        )
        anchor_mask, positive_mask, negative_mask = (
            anchor_mask.to(device),
            positive_mask.to(device),
            negative_mask.to(device),
        )

        optimizer.zero_grad()
        anchor_out = model(anchor, anchor_mask)
        positive_out = model(positive, positive_mask)
        negative_out = model(negative, negative_mask)

        loss = criterion(anchor_out, positive_out, negative_out)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
    return total_loss / len(dataloader)


# 定义验证函数
def validate(
    model: torch.nn.Module,
    dataloader: DataLoader,
    criterion: torch.nn.Module,
    device: str,
) -> float:
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for batch in dataloader:
            (anchor, positive, negative), (
                anchor_mask,
                positive_mask,
                negative_mask,
            ) = batch
        anchor, positive, negative = (
            anchor.to(device),
            positive.to(device),
            negative.to(device),
        )
        anchor_mask, positive_mask, negative_mask = (
            anchor_mask.to(device),
            positive_mask.to(device),
            negative_mask.to(device),
        )
        anchor_out = model(anchor, anchor_mask)
        positive_out = model(positive, positive_mask)
        negative_out = model(negative, negative_mask)
        loss = criterion(anchor_out, positive_out, negative_out)

        total_loss += loss.item()
    return total_loss / len(dataloader)


def load_datasets(
    train_audio_dir: str, val_audio_dir: str, batch_size: int, shuffle: bool
) -> Tuple[DataLoader, DataLoader]:
    train_dataset = AudioDataset(audio_dir=train_audio_dir)
    train_dataloader = DataLoader(
        dataset=train_dataset, batch_size=batch_size, shuffle=shuffle
    )
    val_dataset = AudioDataset(audio_dir=val_audio_dir)
    val_dataloader = DataLoader(
        dataset=val_dataset, batch_size=batch_size, shuffle=shuffle
    )
    return train_dataloader, val_dataloader


def initialize_model(
    device: str,
    input_dim: int,
    num_heads: int,
    num_layers: int,
    forward_expansion: int,
    dropout: float,
    output_dim: int,
) -> torch.nn.Module:
    model = AudioTransformer(
        input_dim=input_dim,
        num_heads=num_heads,
        num_layers=num_layers,
        forward_expansion=forward_expansion,
        dropout=dropout,
        output_dim=output_dim,
    ).to(device)
    return model


def train_and_validate(
    model: torch.nn.Module,
    train_dataloader: DataLoader,
    val_dataloader: DataLoader,
    criterion: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
    num_epochs: int,
) -> None:
    for epoch in range(num_epochs):
        train_loss = train_one_epoch(
            model, train_dataloader, optimizer, criterion, device
        )
        val_loss = validate(model, val_dataloader, criterion, device)

        print(
            f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}"
        )


# 主函数
def main() -> None:
    args = parse_args()

    # 加载配置文件
    config = load_config(args.config)
    # 将配置文件中的内容更新到 args 中
    for key, value in config.items():
        setattr(args, key, value)

    train_dataloader, val_dataloader = load_datasets(
        args.train_audio_dir, args.val_audio_dir, args.batch_size, args.shuffle
    )
    device = args.device
    model = initialize_model(
        device,
        args.input_dim,
        args.num_heads,
        args.num_layers,
        args.forward_expansion,
        args.dropout,
        args.output_dim,
    )

    # 定义损失函数和优化器
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    # 训练和验证循环
    train_and_validate(
        model,
        train_dataloader,
        val_dataloader,
        criterion,
        optimizer,
        device,
        args.num_epochs,
    )

    # 保存模型
    torch.save(model.state_dict(), args.model_dir)


if __name__ == "__main__":
    main()
