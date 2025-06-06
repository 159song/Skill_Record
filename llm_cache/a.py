import time
import os
from dotenv import load_dotenv
from get_history import history

load_dotenv()


def response_text(openai_resp):
    return openai_resp["choices"][0]["message"]["content"]


from gptcache import cache
from gptcache.adapter import openai
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

print("Cache loading.....")

onnx = Onnx()
data_manager = get_data_manager(
    CacheBase("sqlite"),
    VectorBase("faiss", dimension=onnx.dimension),
    data_path="./sqlite.db",
)
cache.init(
    embedding_func=onnx.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
)
# cache.import_data(questions=["my phone number is 4158887963."],answers=["you phone number is 4158887963,correct?"])
cache.set_openai_key()

conversation_history = history

while True:
    # Get user input from the keyboard
    question = input("Enter your question (or type 'q' to quit): ")

    # Exit the loop if the user types 'exit'
    if question.lower() == "q":
        break

    start_time = time.time()

    # Append the new question to the conversation history
    conversation_history.append({"role": "user", "content": question})

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=conversation_history,  # Use the accumulated conversation history
    )
    # Append the response to the conversation history
    conversation_history.append(
        {"role": "assistant", "content": response_text(response)}
    )

    print(f"Question: {question}")
    if "gptcache" in response.keys():
        print("Cache hit Time consuming: {:.2f}s".format(time.time() - start_time))
    else:
        print("Cache not hit Time consuming: {:.2f}s".format(time.time() - start_time))
    print(f"Answer: {response_text(response)}\\n")
