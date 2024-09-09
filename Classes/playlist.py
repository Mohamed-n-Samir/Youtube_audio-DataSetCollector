from Classes.video import Video
from tqdm import tqdm
from pytubefix import Playlist as pl


class Playlist:

    def __init__(self, url, caption_lang, caption_type):
        self.videos = [Video(video.video_id,caption_lang,caption_type) for video in pl(url).videos]
        
        
# https://www.youtube.com/watch?v=3OA8C6RMcWE&list=PL4_bo90i-4GLcriVuJvJmAGroh3NX3azT
# https://www.youtube.com/watch?v=uAspBDR7TN0&list=PL4_bo90i-4GITOqdamSufNVj-UvaJz9eK
# https://www.youtube.com/watch?v=_6i-5VngAqk&list=PL4_bo90i-4GKkfCZV50RwmhfKdAk53hzR
# https://www.youtube.com/watch?v=jRnBwscF9OU&list=PL4_bo90i-4GIAlH-vGZO35vbj7lVrcnLv
# https://www.youtube.com/watch?v=YiBzJGYclRo&list=PL4_bo90i-4GJh6DY-uFXdFTwnzRvYagLs
# https://www.youtube.com/watch?v=tLUqvthSY6s&list=PL4_bo90i-4GItp18iodTK2cv-Mzn0k1es
