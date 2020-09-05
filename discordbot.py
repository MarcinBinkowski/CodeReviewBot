import discord
from reviewbot.githubconnector import GithubConnector, CONFIG


def create_pr(username, repository):
    repository_name = f"{username}/{repository}"
    github_connector = GithubConnector()
    pull_request = github_connector.run(repository_name, "master", "empty", "review")
    return f"{pull_request.html_url}/files"


client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await message.channel.send(f"Hi {message.author.mention}! Creating Pull Request for your Code Review...")
    if message.content.startswith('!CodeReview'):
        repository_link = message.content.replace('!CodeReview', '')
        link_contents = repository_link.split("/")
        user, repository = [
            item for item in link_contents if "github.com" not in item and "https" not in item and item != ""
        ]
        created_pr_link = create_pr(user, repository)
        await message.channel.send(CONFIG.default_discord_message(created_pr_link))

client.run(CONFIG.discord_token)
