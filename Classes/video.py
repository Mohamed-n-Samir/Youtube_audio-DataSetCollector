from Classes.utils.helpers import is_arabic_only, is_english_only, is_mix_only
from youtube_transcript_api import YouTubeTranscriptApi
from pytubefix import YouTube


class Video:

    def __init__(self, id, caption_lang, caption_type):
        self.__id = id
        self.__caption_lang = caption_lang
        self.__caption_type = caption_type

    def video_id(self):
        return self.__id

    def get_caption(self):

        try:
            # Fetch the available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.__id)

            # Get the manually created transcript
            transcript = None

            match self.__caption_type:
                case "m":
                    transcript = transcript_list.find_manually_created_transcript(
                        [f"{self.__caption_lang}"]
                    )
                case "a":
                    transcript = transcript_list.find_generated_transcript(
                        [f"{self.__caption_lang}"]
                    )

            # Fetch the transcript data
            return transcript.fetch()

        except Exception as e:
            return None

    def get_arabic_only_from_caption(self):

        captions = []
        for caption in self.get_caption():
            text = caption["text"]
            if is_arabic_only(text):
                captions.append(caption)

        if len(captions) > 0:
            return captions
        else:
            return None

    def get_english_only_from_caption(self):

        captions = []
        for caption in self.get_caption():
            text = caption["text"]
            if is_english_only(text):
                captions.append(caption)

        if len(captions) > 0:
            return captions
        else:
            return None

    def get_mix_only_from_caption(self):

        captions = []
        for caption in self.get_caption():
            text = caption["text"]
            if is_mix_only(text):
                captions.append(caption)

        if len(captions) > 0:
            return captions
        else:
            return None
