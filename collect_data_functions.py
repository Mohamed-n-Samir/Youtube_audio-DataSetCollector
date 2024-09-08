from youtube_transcript_api import YouTubeTranscriptApi
from pytubefix import YouTube, Channel, Playlist
import re
from tqdm import tqdm
from pydub import AudioSegment
from pathlib import Path
import argparse
import pandas as pd


caption_lang = "ar"


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
    parser.add_argument("--urls_file", type=str, help="File containing YouTube URLs")
    parser.add_argument(
        "--caption_type",
        type=str,
        help="'a' for auto caption ('Ai caption') 'm' for manual caption ('people writen caption')",
        default="m",
    )

    return parser.parse_args()


def get_manual_captions(video_id, audio_type):
    try:
        # Fetch the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Get the manually created transcript
        transcript = transcript_list.find_manually_created_transcript(
            [f"{caption_lang}"]
        )

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
        if audio_type == "all":
            arabic_and_english_captions.append(caption)
        elif audio_type == "mix_only":
            if arabic_pattern.search(text) and english_pattern.search(text):
                arabic_and_english_captions.append(caption)

    if len(arabic_and_english_captions) > 0:
        return arabic_and_english_captions
    else:
        return None


def get_auto_captions(video_id, audio_type):
    try:
        # Fetch the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Get the automatically created transcript
        transcript = transcript_list.find_generated_transcript([f"{caption_lang}"])

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
        if audio_type == "all":
            arabic_and_english_captions.append(caption)
        elif audio_type == "mix_only":
            if arabic_pattern.search(text) and english_pattern.search(text):
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


def videos_downloader(urls, audio_type, output_path, metadata_path, caption_type):
    for url in urls:

        df = pd.DataFrame(columns=["file_name", "sentence"])
        video = YouTube(url)
        subtitles = None
        match caption_type:
            case "m":
                subtitles = get_manual_captions(video.video_id, audio_type)
            case "a":
                subtitles = get_auto_captions(video.video_id, audio_type)
        if subtitles:
            try:
                # Download audio
                yt = YouTube(f"https://www.youtube.com/watch?v={video.video_id}")
                audio_abrs = list(
                    set(
                        [
                            stream.abr
                            for stream in yt.streams.filter(only_audio=True)
                            if stream.abr is not None
                        ]
                    )
                )
                audio_abrs = sorted([int(abr.strip("kbps")) for abr in set(audio_abrs)])
                audio_abrs = [f"{abr}kbps" for abr in audio_abrs]
                audio_stream = yt.streams.filter(
                    only_audio=True, abr=audio_abrs[-1]
                ).first()
                audio_path = audio_stream.download(
                    output_path=str(output_path),
                    filename=f"{video.video_id}.{audio_stream.subtype}",
                )

                # Cut audio into chunks
                audio_chunks = cut_audio(audio_path, subtitles)
                print(
                    f"Downloaded {len(audio_chunks)} audio chunks for {video.video_id}"
                )
            except Exception as e:
                print(f"Failed with {video.video_id}: {e}")
                Path(audio_path).unlink()
                continue

            # Save audio chunks to disk and update DataFrame
            for chunk, caption in zip(audio_chunks, subtitles):
                output_filename = (
                    f"{output_path}/{video.video_id}_{caption['start']}.wav"
                )
                chunk.export(output_filename, format="wav")
                df = df._append(
                    {
                        "file_name": f"{video.video_id}_{caption['start']}.wav",
                        "sentence": caption["text"].strip().strip('"').strip("'"),
                    },
                    ignore_index=True,
                )
                # json_records = df.to_json(
                #     metadata_path,
                #     orient="records",
                #     lines=True,
                #     force_ascii=False,
                # ).splitlines()

                # with open(metadata_path, "a", encoding="utf-8") as f:
                #     for record in json_records:
                #         f.write(record + "\n")
            json_records = df.to_json(
                orient="records",
                lines=True,
                force_ascii=False,
            )
            # Append to the existing file, or create it if it doesn't exist
            with open(metadata_path, "a", encoding="utf-8") as f:
                f.write(json_records)

            Path(audio_path).unlink()
        else:
            print("No subtitle found.")


def bulk_downloader(
    urls, audio_type, output_path, metadata_path, link_type, caption_type
):
    my_audio_list = ""

    for url in tqdm(urls):
        if link_type == "channel":
            my_audio_list = Channel(url)
        elif link_type == "playlist":
            my_audio_list = Playlist(url)
        for video in tqdm(my_audio_list.videos, leave=False):

            df = pd.DataFrame(columns=["file_name", "sentence"])
            subtitles = None
            match caption_type:
                case "m":
                    subtitles = get_manual_captions(video.video_id, audio_type)
                case "a":
                    subtitles = get_auto_captions(video.video_id, audio_type)
            if subtitles:
                try:
                    # Download audio
                    yt = YouTube(f"https://www.youtube.com/watch?v={video.video_id}")
                    audio_abrs = list(
                        set(
                            [
                                stream.abr
                                for stream in yt.streams.filter(only_audio=True)
                                if stream.abr is not None
                            ]
                        )
                    )
                    audio_abrs = sorted(
                        [int(abr.strip("kbps")) for abr in set(audio_abrs)]
                    )
                    audio_abrs = [f"{abr}kbps" for abr in audio_abrs]
                    audio_stream = yt.streams.filter(
                        only_audio=True, abr=audio_abrs[-1]
                    ).first()
                    audio_path = audio_stream.download(
                        output_path=str(output_path),
                        filename=f"{video.video_id}.{audio_stream.subtype}",
                    )

                    # Cut audio into chunks
                    audio_chunks = cut_audio(audio_path, subtitles)
                    print(
                        f"Downloaded {len(audio_chunks)} audio chunks for {video.video_id}"
                    )
                except Exception as e:
                    print(f"Failed with {video.video_id}: {e}")
                    Path(audio_path).unlink()
                    continue

                # Save audio chunks to disk and update DataFrame
                for chunk, caption in zip(audio_chunks, subtitles):
                    output_filename = (
                        f"{output_path}/{video.video_id}_{caption['start']}.wav"
                    )
                    chunk.export(output_filename, format="wav")
                    df = df._append(
                        {
                            "file_name": f"{video.video_id}_{caption['start']}.wav",
                            "sentence": caption["text"].strip().strip('"').strip("'"),
                        },
                        ignore_index=True,
                    )
                json_records = df.to_json(
                    orient="records",
                    lines=True,
                    force_ascii=False,
                )
                # Append to the existing file, or create it if it doesn't exist
                with open(metadata_path, "a", encoding="utf-8") as f:
                    f.write(json_records)

                Path(audio_path).unlink()
            else:
                print("No subtitle found.")
