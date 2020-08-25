from .githubconnector import GithubConnector
from .config import *
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "To create PR add repository name after '/' for example '/DiscordCodeReviewBot/TestRepo'"


@app.route('/<username>/<repository>', methods=['GET'])
def create_pr(username, repository):
    repository_name = f"{username}/{repository}"
    github_connector = GithubConnector()
    pull_request = github_connector.run(repository_name, "master", "empty", "review")
    return f"Twoj PR: <a href='{pull_request.html_url}/files'>Link</a>"

