from collect_data_functions import parse_arguments, videos_downloader, bulk_downloader
from pathlib import Path

args = parse_arguments()

output_path = Path(args.output_dir)
output_path.mkdir(exist_ok=True, parents=True)
metadata_path = output_path / "metadata.jsonl"

with open(args.urls_file, "r") as file:
    urls = [line.strip() for line in file]
urls = list(set(urls))


match args.link_type:
    case "video":
        videos_downloader(
            urls, args.audio_type, output_path, metadata_path, args.caption_type
        )
    case "channel" | "playlist":
        bulk_downloader(
            urls,
            args.audio_type,
            output_path,
            metadata_path,
            args.link_type,
            args.caption_type,
        )
