from Classes.video import Video
from tqdm import tqdm
from pytubefix import Channel as ch


class Channel:

    def __init__(self, url, caption_lang, caption_type):
        self.videos = [
            Video(video.video_id, caption_lang, caption_type)
            for video in ch(url).videos
        ]
