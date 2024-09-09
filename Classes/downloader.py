from Classes.utils.helpers import (
    is_arabic_only,
    is_english_only,
    is_mix_only,
    cut_audio,
)
from pydub import AudioSegment
from pytubefix import YouTube
from pathlib import Path
from Classes.video import Video
from Classes.playlist import Playlist
from Classes.channel import Channel
from tqdm import tqdm
import pandas as pd


class Downloader:

    def __init__(
        self,
        link_type,
        audio_type,
        output_dir,
        caption_type,
        urls_file,
        caption_lang,
    ):
        self.__link_type = link_type
        self.__audio_type = audio_type
        self.__output_dir = Path(output_dir)
        self.__caption_type = caption_type
        self.__urls_file = urls_file
        self.__caption_lang = caption_lang
        self.__df = pd.DataFrame(columns=["file_name", "sentence"])

        self.__output_dir.mkdir(exist_ok=True, parents=True)

        self.__main_audio_output_path = self.__output_dir / "mainAudioFiles"
        self.__main_audio_output_path.mkdir(exist_ok=True, parents=True)

        self.__metadata_path = self.__output_dir / "metadata"
        self.__metadata_path.mkdir(exist_ok=True, parents=True)

        self.__garbage_chunk_path = self.__output_dir / "garbage"
        self.__garbage_chunk_path.mkdir(exist_ok=True, parents=True)

        self.__garbage_metadata_path = self.__metadata_path / "garbage.jsonl"

        self.handelfiles()

    def start_download(self):
        match self.__link_type:
            case "video":
                for url in tqdm(self.get_urls()):
                    self.download_audio(url)
            case "playlist":
                for url in self.get_urls():
                    bulk = Playlist(url, self.__caption_lang, self.__caption_type)
                    self.download_audio_bulk(bulk)
            case "channel":
                for url in self.get_urls():
                    bulk = Channel(url, self.__caption_lang, self.__caption_type)
                    self.download_audio_bulk(bulk)

    def get_urls(self):
        with open(self.__urls_file, "r") as file:
            urls = [line.strip() for line in file]
            return list(set(urls))

    def download_audio(self, url):
        try:
            yt = YouTube(url)
            video = Video(
                yt.video_id,
                self.__caption_lang,
                self.__caption_type,
            )
            subtitles = (
                video.get_caption()
                if self.__audio_type == "all_mix"
                else (
                    video.get_arabic_only_from_caption()
                    if self.__audio_type == "ar_only"
                    else (
                        video.get_english_only_from_caption()
                        if self.__audio_type == "en_only"
                        else (
                            video.get_mix_only_from_caption()
                            if self.__audio_type == "mix_only"
                            else None
                        )
                    )
                )
            )
            if subtitles:
                self.audio_downloader_handler(yt, subtitles)
            else:
                print("No subtitle found.")

        except Exception as e:
            print(f"Failed with {yt.video_id}: {e}")

    def download_audio_bulk(self, bulk):
        for video in tqdm(bulk.videos):
            subtitles = (
                video.get_caption()
                if self.__audio_type == "all_mix"
                else (
                    video.get_arabic_only_from_caption()
                    if self.__audio_type == "ar_only"
                    else (
                        video.get_english_only_from_caption()
                        if self.__audio_type == "en_only"
                        else (
                            video.get_mix_only_from_caption()
                            if self.__audio_type == "mix_only"
                            else None
                        )
                    )
                )
            )
            if subtitles:
                try:
                    yt = YouTube(f"https://www.youtube.com/watch?v={video.video_id()}")
                    self.audio_downloader_handler(yt, subtitles)
                except Exception as e:
                    print(f"Failed with {yt.video_id}: {e}")

            else:
                print("No subtitle found.")

    def audio_downloader_handler(self, yt, subtitles):
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
        audio_stream = yt.streams.filter(only_audio=True, abr=audio_abrs[-1]).first()
        audio_path = audio_stream.download(
            output_path=str(self.__main_audio_output_path),
            filename=f"{yt.video_id}.{audio_stream.subtype}",
        )
        # Cut audio into chunks
        audio_chunks = cut_audio(audio_path, subtitles)
        if self.__audio_type == "all_mix":
            self.save_all_meta_data(audio_chunks, subtitles, yt.video_id)
        else:
            self.save_meta_data(audio_chunks, subtitles, yt.video_id)

        print(f"Downloaded {len(audio_chunks)} audio chunks for {yt.video_id}")

    def save_all_meta_data(self, audio_chunks, subtitles, video_id):
        # Save audio chunks to disk and update DataFrame
        for chunk, caption in zip(audio_chunks, subtitles):

            sentence = caption["text"].strip().strip('"').strip("'")

            file_path, metadata_path = self.get_file_path(sentence)

            output_filename = f"{file_path}/{video_id}_{caption['start']}.wav"

            chunk.export(output_filename, format="wav")
            self.__df = self.__df._append(
                {
                    "file_name": f"{output_filename}",
                    "sentence": sentence,
                },
                ignore_index=True,
            )

            json_records = self.__df.to_json(
                orient="records",
                lines=True,
                force_ascii=False,
            )

            self.__df = pd.DataFrame(columns=["file_name", "sentence"])

            # Append to the existing file, or create it if it doesn't exist
            with open(metadata_path, "a", encoding="utf-8") as f:
                f.write(json_records)

    def save_meta_data(self, audio_chunks, subtitles, video_id):
        # Save audio chunks to disk and update DataFrame
        for chunk, caption in zip(audio_chunks, subtitles):

            sentence = caption["text"].strip().strip('"').strip("'")

            output_filename = (
                f"{self.__chunk_output_path}/{video_id}_{caption['start']}.wav"
            )

            chunk.export(output_filename, format="wav")
            self.__df = self.__df._append(
                {
                    "file_name": f"{output_filename}",
                    "sentence": sentence,
                },
                ignore_index=True,
            )

            json_records = self.__df.to_json(
                orient="records",
                lines=True,
                force_ascii=False,
            )

        self.__df = pd.DataFrame(columns=["file_name", "sentence"])

        # Append to the existing file, or create it if it doesn't exist
        with open(self.__metadata_path, "a", encoding="utf-8") as f:
            f.write(json_records)

    def get_file_path(self, sentence):
        match self.__caption_type:
            case "m":
                if is_arabic_only(sentence):
                    return (
                        f"{self.__manual_arabic_chunk_path}",
                        f"{self.__manual_arabic_metadata_path}",
                    )
                elif is_english_only(sentence):
                    return (
                        f"{self.__manual_english_chunk_path}",
                        f"{self.__manual_english_metadata_path}",
                    )
                elif is_mix_only(sentence):
                    return (
                        f"{self.__manual_mix_chunk_path}",
                        f"{self.__manual_mix_metadata_path}",
                    )

            case "a":
                if is_arabic_only(sentence):
                    return (
                        f"{self.__auto_arabic_chunk_path}",
                        f"{self.__auto_arabic_metadata_path}",
                    )
                elif is_english_only(sentence):
                    return (
                        f"{self.__auto_english_chunk_path}",
                        f"{self.__auto_english_metadata_path}",
                    )
                elif is_mix_only(sentence):
                    return (
                        f"{self.__auto_mix_chunk_path}",
                        f"{self.__auto_mix_metadata_path}",
                    )

        return (
            f"{self.__garbage_chunk_path}",
            f"{self.__garbage_metadata_path}",
        )

    def handelfiles(self):
        match self.__audio_type:
            case "ar_only":
                if self.__caption_type == "a":
                    self.__metadata_path = (
                        self.__output_dir / "metadata/auto_ar_only_metadata.jsonl"
                    )
                    self.__chunk_output_path = (
                        self.__output_dir / "audio chunks/auto_arabic_only"
                    )
                    self.__chunk_output_path.mkdir(exist_ok=True, parents=True)
                elif self.__caption_type == "m":
                    self.__metadata_path = (
                        self.__output_dir / "metadata/manual_ar_only_metadata.jsonl"
                    )
                    self.__chunk_output_path = (
                        self.__output_dir / "audio chunks/manual_arabic_only"
                    )
                    self.__chunk_output_path.mkdir(exist_ok=True, parents=True)
            case "en_only":
                if self.__caption_type == "a":
                    self.__metadata_path = (
                        self.__output_dir / "metadata/auto_en_only_metadata.jsonl"
                    )
                    self.__chunk_output_path = (
                        self.__output_dir / "audio chunks/auto_english_only"
                    )
                    self.__chunk_output_path.mkdir(exist_ok=True, parents=True)
                elif self.__caption_type == "m":
                    self.__metadata_path = (
                        self.__output_dir / "metadata/manual_en_only_metadata.jsonl"
                    )
                    self.__chunk_output_path = (
                        self.__output_dir / "audio chunks/manual_english_only"
                    )
                    self.__chunk_output_path.mkdir(exist_ok=True, parents=True)
            case "mix_only":
                if self.__caption_type == "a":
                    self.__metadata_path = (
                        self.__output_dir / "metadata/auto_mix_only_metadata.jsonl"
                    )
                    self.__chunk_output_path = (
                        self.__output_dir / "audio chunks/auto_mix_only"
                    )
                    self.__chunk_output_path.mkdir(exist_ok=True, parents=True)
                elif self.__caption_type == "m":
                    self.__metadata_path = (
                        self.__output_dir / "metadata/manual_mix_only_metadata.jsonl"
                    )
                    self.__chunk_output_path = (
                        self.__output_dir / "audio chunks/manual_mix_only"
                    )
                    self.__chunk_output_path.mkdir(exist_ok=True, parents=True)
            case "all_mix":
                if self.__caption_type == "a":
                    # arabic only
                    self.__auto_arabic_metadata_path = (
                        self.__output_dir / "metadata/auto_ar_only_metadata.jsonl"
                    )
                    self.__auto_arabic_chunk_path = (
                        self.__output_dir / "audio chunks/auto_arabic_only"
                    )
                    self.__auto_arabic_chunk_path.mkdir(exist_ok=True, parents=True)

                    # english only
                    self.__auto_english_metadata_path = (
                        self.__output_dir / "metadata/auto_en_only_metadata.jsonl"
                    )
                    self.__auto_english_chunk_path = (
                        self.__output_dir / "audio chunks/auto_english_only"
                    )
                    self.__auto_english_chunk_path.mkdir(exist_ok=True, parents=True)

                    # mix only
                    self.__auto_mix_metadata_path = (
                        self.__output_dir / "metadata/auto_mix_only_metadata.jsonl"
                    )
                    self.__auto_mix_chunk_path = (
                        self.__output_dir / "audio chunks/auto_mix_only"
                    )
                    self.__auto_mix_chunk_path.mkdir(exist_ok=True, parents=True)
                elif self.__caption_type == "m":
                    # arabic only
                    self.__manual_arabic_metadata_path = (
                        self.__output_dir / "metadata/manual_ar_only_metadata.jsonl"
                    )
                    self.__manual_arabic_chunk_path = (
                        self.__output_dir / "audio chunks/manual_arabic_only"
                    )
                    self.__manual_arabic_chunk_path.mkdir(exist_ok=True, parents=True)

                    # english only
                    self.__manual_english_metadata_path = (
                        self.__output_dir / "metadata/manual_en_only_metadata.jsonl"
                    )
                    self.__manual_english_chunk_path = (
                        self.__output_dir / "audio chunks/manual_english_only"
                    )
                    self.__manual_english_chunk_path.mkdir(exist_ok=True, parents=True)

                    # mix only
                    self.__manual_mix_metadata_path = (
                        self.__output_dir / "metadata/manual_mix_only_metadata.jsonl"
                    )
                    self.__manual_mix_chunk_path = (
                        self.__output_dir / "audio chunks/manual_mix_only"
                    )
                    self.__manual_mix_chunk_path.mkdir(exist_ok=True, parents=True)
