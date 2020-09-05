import os
import logging
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s :: %(levelname)s :: %(message)s')
LOGGER = logging.getLogger("__main__")


class SingletonMeta(type):
    """
    The Singleton metaclass.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Return existing instance if user wants to create the new one.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Configuration(metaclass=SingletonMeta):

    @property
    def github_token(self):
        return os.environ.get("GITHUB_KEY")

    @property
    def default_pull_request_title(self):
        return "Code Review"

    @property
    def default_review_branch_name(self):
        return "review"

    @property
    def default_empty_branch_name(self):
        return "empty"

    @property
    def default_base_branch_name(self):
        return "master"

    @staticmethod
    def default_commit_message(file_name):
        return f"Remove file <{file_name}>"

    @property
    def discord_token(self):
        return os.environ.get("DISCORD_TOKEN")

    @property
    def discord_command(self):
        return os.environ.get("!CodeReview")

    @staticmethod
    def default_discord_message(pull_request_link):
        return f"Link to created Pull Request: {pull_request_link}"

CONFIG = Configuration()
