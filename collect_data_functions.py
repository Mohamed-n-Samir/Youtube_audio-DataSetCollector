from youtube_transcript_api import YouTubeTranscriptApi
import re
from pydub import AudioSegment
import argparse


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
        default="mix_only",
        help="all | mix_only",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="audio",
        help="Output directory for audio files",
    )
    parser.add_argument(
        "--urls_file", type=str, help="File containing YouTube URLs"
    )

    return parser.parse_args()



def get_manual_captions(video_id, audio_type):
    try:
        # Fetch the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Get the manually created transcript
        transcript = transcript_list.find_manually_created_transcript(["ar"])

        # Fetch the transcript data
        caption_data = transcript.fetch()

    except Exception as e:
        return None

    # Arabic Unicode range
    arabic_pattern = re.compile(r"[\u0600-\u06FF]+")

    # English pattern (simple a-z or A-Z)
    english_pattern = re.compile(r"[a-zA-Z]+")

    arabic_and_english_captions = []
    for caption in caption_data:
        text = caption["text"]
        if(audio_type == "all"):
            arabic_and_english_captions.append(caption)
        elif(audio_type == "mix_only"):
            if  arabic_pattern.search(text) and english_pattern.search(text):
                arabic_and_english_captions.append(caption)

    if len(arabic_and_english_captions) > 0:
        return arabic_and_english_captions
    else:
        return None


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


