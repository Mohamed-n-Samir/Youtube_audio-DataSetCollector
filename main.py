from collect_data_functions import parse_arguments, cut_audio, get_manual_captions
from pytubefix import YouTube, Channel, Playlist
from tqdm import tqdm
from pathlib import Path
import pandas as pd

args = parse_arguments()

output_path = Path(args.output_dir)
output_path.mkdir(exist_ok=True, parents=True)
metadata_path = output_path / "metadata.jsonl"

with open(args.urls_file, "r") as file:
    urls = [line.strip() for line in file]
urls = list(set(urls))


def main_function():
    df = pd.DataFrame(columns=["file_name", "sentence"])
    match args.link_type:
        case "video":
            for url in urls:
                video = YouTube(url)
                subtitles = get_manual_captions(video.video_id, args.audio_type)
                if subtitles:
                    try:
                        # Download audio
                        yt = YouTube(
                            f"https://www.youtube.com/watch?v={video.video_id}"
                        )
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
                                "sentence": caption["text"]
                                .strip()
                                .strip('"')
                                .strip("'"),
                            },
                            ignore_index=True,
                        )
                        df.to_json(
                            metadata_path,
                            orient="records",
                            lines=True,
                            force_ascii=False,
                        )
                    Path(audio_path).unlink()
                else:
                    print("No subtitle found.")

        case "channel" | "playlist":

            my_audio_list = ''

            for url in tqdm(urls):
                if(args.link_type == "channel"):
                    my_audio_list = Channel(url)
                elif(args.link_type == "playlist"):
                    my_audio_list = Playlist(url)
                for video in tqdm(my_audio_list.videos, leave=False):
                    subtitles = get_manual_captions(video.video_id, args.audio_type)
                    if subtitles:
                        try:
                            # Download audio
                            yt = YouTube(
                                f"https://www.youtube.com/watch?v={video.video_id}"
                            )
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
                                    "sentence": caption["text"]
                                    .strip()
                                    .strip('"')
                                    .strip("'"),
                                },
                                ignore_index=True,
                            )
                            df.to_json(
                                metadata_path,
                                orient="records",
                                lines=True,
                                force_ascii=False,
                            )
                        Path(audio_path).unlink()
                    else:
                        print("No subtitle found.")

main_function()
