from Classes.utils.helpers import parse_arguments
from Classes.youtube_audio_dataset_collector import YoutubeAudioDatasetCollector

args = parse_arguments()

ydc = YoutubeAudioDatasetCollector(args.link_type,args.audio_type,args.output_dir,args.urls_file,args.caption_type,args.caption_lang)

ydc.handle_args_start_downloading()


