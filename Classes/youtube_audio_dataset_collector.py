from Classes.downloader import Downloader
from sys import exit 


class YoutubeAudioDatasetCollector:
    
    def __init__(self,link_type,audio_type,output_dir,urls_file,caption_type,caption_lang):
        self.__link_type = link_type
        self.__audio_type = audio_type
        self.__output_dir = output_dir
        self.__urls_file = urls_file
        self.__caption_type = caption_type
        self.__caption_lang = caption_lang
        self.__downloader = None

        

    def handle_args_start_downloading(self):
        
        if self.__link_type not in ['video','playlist','channel']:
            print("--link_type must be on of the following 'video'|'playlist'|'channel'")
            exit()
        if self.__audio_type not in ['ar_only','en_only','mix_only','all_mix']:
            print("--audio_type must be on of the following 'ar_only'|'en_only'|'mix_only'|'all_mix'")
            exit()
        if self.__caption_type not in ['a','m']:
            print("--__caption_type must be on of the following 'a'|'m' a -> auto generated caption , m -> manual generated caption ")
            exit()
        if self.__caption_lang not in ['ar','en']:
            print("--caption_lang must be on of the following 'ar'|'en'")
            exit()

        self.__downloader = Downloader(self.__link_type,self.__audio_type,self.__output_dir,self.__caption_type,self.__urls_file,self.__caption_lang) 
        self.__downloader.start_download()


        