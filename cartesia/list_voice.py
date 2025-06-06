import requests
import os
from collections import defaultdict
import requests


def get_group_voice():
    url = "https://api.cartesia.ai/voices/"

    headers = {
        "Cartesia-Version": "2024-06-10",
        "X-API-Key": os.getenv("CARTESIA_API_KEY"),
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    for item in data:
        if "embedding" in item:
            del item["embedding"]

    name_mapping = {
        "Pleasant Man": "PleasantMan_English",
        "Ananya": "Ananya_English",
        "Harry": "Harry_English",
        "Lena": "Lena_English",
        "American Voiceover Man": "American_Voice_Over_English",
        "Southern Woman": "Southern_Woman_English",
        "Sarah Curious": "Sarah_Curious_English",
        "Jordan": "Jordan_English",
        "Sophie": "Sophie_English",
        "Sarah": "Sarah_English",
        "Benedict": "Benedict_English",
    }

    # Preprocess data to update names
    for item in data:
        if item.get("name") in name_mapping:
            item["name"] = name_mapping[item["name"]]

    # Filter data to keep only items with names in the list
    names_to_keep = {
        "Sarah_English": "en",
        "Sarah_Spanish": "es",
        "Sarah_Chinese": "zh",
        "Sarah_Korean": "ko",
        "PleasantMan_English": "en",
        "PleasantMan_Spanish": "es",
        "PleasantMan_Chinese": "zh",
        "PleasantMan_Korean": "ko",
        "French_Conversational_Lady_English": "en",
        "French_Conversational_Lady_Chinese": "zh",
        "French_Conversational_Lady_Spanish": "es",
        "French_Conversational_Lady_Korean": "ko",
        "Ananya_English": "hi",
        "Ananya_Chinese": "zh",
        "Ananya_Spanish": "es",
        "Ananya_Korean": "ko",
        "Harry_English": "en",
        "Harry_Chinese": "zh",
        "Harry_Korean": "ko",
        "Harry_Spanish": "es",
        "Benedict_English": "en",
        "Benedict_Chinese": "zh",
        "Benedict_Spanish": "es",
        "Benedict_Korean": "ko",
        "Lena_English": "en",
        "Lena_Chinese": "zh",
        "Lena_Spanish": "es",
        "Lena_Korean": "ko",
        "American_Voice_Over_English": "en",
        "American_Voice_Over_Chinese": "zh",
        "American_Voice_Over_Spanish": "es",
        "American_Voice_Over_Korean": "ko",
        "Southern_Woman_English": "en",
        "Southern_Woman_Chinese": "zh",
        "Southern_Woman_Spanish": "es",
        "Southern_Woman_Korean": "ko",
        "Sarah_Curious_English": "en",
        "Sarah_Curious_Chinese": "zh",
        "Sarah_Curious_Spanish": "es",
        "Sarah_Curious_Korean": "ko",
        "Jordan_English": "en",
        "Jordan_Chinese": "zh",
        "Jordan_Spanish": "es",
        "Jordan_Korean": "ko",
        "Sophie_English": "en",
        "Sophie_Chinese": "zh",
        "Sophie_Spanish": "es",
        "Sophie_Korean": "ko",
    }
    # Filter data to keep only items with names and corresponding languages in the list
    filtered_data = [
        {key: item[key] for key in ("id", "name", "language")}
        for item in data
        if item.get("name") in names_to_keep
        and item.get("language") == names_to_keep[item.get("name")]
    ]

    # Group data by the prefix of the name before the last '_'
    grouped_data = defaultdict(list)
    for item in filtered_data:
        name_prefix = item["name"].rsplit("_", 1)[0]
        grouped_data[name_prefix].append(item)

    # Print grouped data
    # for prefix, items in grouped_data.items():
    #     print(f"{prefix}:")
    #     for item in items:
    #         print(f"  {item}")
    return grouped_data


if __name__ == "__main__":
    # print(get_group_voice())

    # Text to Speech (Bytes) (POST /tts/bytes)
    response = requests.post(
        "https://api.cartesia.ai/tts/bytes",
        headers={
            "X-API-Key": os.getenv("CARTESIA_API_KEY"),
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json",
        },
        json={
            "model_id": "sonic-2",
            "transcript": "Hello, world!",
            "voice": {"mode": "id", "id": "bf0a246a-8642-498a-9950-80c35e9276b5"},
            "output_format": {
                "container": "wav",
                "sample_rate": 24000,
                "encoding": "pcm_s16le",
            },
            "language": "en",
        },
    )
    a = 1
