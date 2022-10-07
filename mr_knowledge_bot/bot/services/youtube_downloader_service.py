import os
import logging
from pytube import YouTube

logger = logging.getLogger(__name__)


class YouTubeVideoDownloader:
    """
    Downloads a YouTube video and deletes it once it has been used. Must be used as a context manager.
    """
    def __init__(self, url):
        try:
            self.__youtube_video = YouTube(url)
        except Exception:
            error_msg = f'invalid YouTube video URL {url}'
            logger.error(error_msg)
            raise ValueError(error_msg)
        self.__path = None

    def __enter__(self):
        # returns a file object that the video was downloaded into.
        try:
            self.__path = self.__youtube_video.streams.get_highest_resolution().download()
            return open(self.__path, 'rb')
        except Exception as e:
            logger.error(f'Could not download youtube video {self.__youtube_video.watch_url}. Error:\n{e}')
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.__path):
            os.remove(self.__path)
