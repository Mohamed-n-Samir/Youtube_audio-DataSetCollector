import re
from pydub import AudioSegment
import argparse

arabic_pattern = re.compile(r"[\u0600-\u06FF]+")
english_pattern = re.compile(r"[a-zA-Z]+")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process YouTube channels for audio and captions."
    )
    parser.add_argument(
        "--link_type",
        type=str,
        default="video",
        help="video | channel | playlist => make sure that the channel or playlist isn't more than 200 vids",
    )
    parser.add_argument(
        "--audio_type",
        type=str,
        default="all_mix",
        help="ar_only | en_only | all_mix | mix_only",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Output directory for audio files",
    )
    parser.add_argument(
        "--urls_file",
        type=str,
        help="File containing YouTube URLs",
        default="youLinks.txt",
    )
    parser.add_argument(
        "--caption_type",
        type=str,
        help="'a' for auto caption ('Ai caption') 'm' for manual caption ('people writen caption')",
        default="m",
    )
    parser.add_argument(
        "--caption_lang",
        type=str,
        help="now there are 2 lang only ['ar','en'] Arabic, English",
        default="ar",
    )

    return parser.parse_args()


def cut_audio(audio_path, captions):
    audio = AudioSegment.from_file(audio_path)
    audio_chunks = []
    for caption in captions:
        start = caption["start"]
        duration = caption["duration"]
        end = start + duration
        audio_chunk = audio[start * 1000 : end * 1000]
        audio_chunks.append(audio_chunk)
    return audio_chunks


def is_arabic_only(text):

    return arabic_pattern.search(text) and not english_pattern.search(text)


def is_english_only(text):

    return english_pattern.search(text) and not arabic_pattern.search(text)


def is_mix_only(text):

    return english_pattern.search(text) and arabic_pattern.search(text)
