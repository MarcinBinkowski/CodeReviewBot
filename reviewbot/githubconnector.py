from github import Github
from github.Repository import Repository
from github.Branch import Branch
from github.ContentFile import ContentFile
from github.PullRequest import PullRequest
from reviewbot.config import *
from typing import List, Union


class GithubConnector:
    """Class containing all of the methods related to the github operations used by this module"""
    def __init__(self):
        self.github_client = Github(CONFIG.github_token)
        self.user = self.github_client.get_user()

    def run(
            self,
            repository_name,
            base_branch_name: str,
            empty_branch_name: str,
            review_branch_name: str) -> PullRequest:
        """
        Start of the PR creation process.
        :param repository_name: Name of the repository user wants to create PR for.
        :param base_branch_name: Repository branch which user wants to create PR for.
        :param empty_branch_name: Name of the branch with no files which will be the target branch of the PR.
        :param review_branch_name: Name of the branch which will be source branch of The PR.
        It is copy of the base branch.
        :return: None
        """
        LOGGER.info("Start of the PR creation process.")
        forked_repository = self.fork_repository(repository_name)
        empty_branch = self.create_empty_branch(forked_repository, base_branch_name, empty_branch_name)
        review_branch = self.create_branch_if_not_exist(forked_repository, base_branch_name, review_branch_name)
        pull_request = self.get_pull_request(forked_repository, review_branch, empty_branch)
        if not pull_request:
            LOGGER.info("Pull Request does not exist. Creating new one...")
            return self.create_pull_request(
                forked_repository, review_branch, empty_branch, CONFIG.default_pull_request_title)
        else:
            LOGGER.info("Pull Request Exists. Returning existing one.")
            return pull_request

    def fork_repository(self, repository_name: str) -> Repository:
        """
        Fork the repository for which user wants to create PR.
        :return: Forked repository on DiscordCodeReviewBot account.
        """
        repository = self.github_client.get_repo(repository_name)
        LOGGER.info("Create fork of the <%s> repository.", repository_name)
        return self.user.create_fork(repository)

    def create_empty_branch(
            self,
            repository: Repository,
            source_branch_name,
            target_branch_name) -> Branch:
        """
        Create branch which does not contain any files or folders.
        :return: Branch with no files.
        """
        LOGGER.info("Start creation of the empty branch.")
        empty_branch = self.create_branch_if_not_exist(repository, source_branch_name, target_branch_name)
        LOGGER.info("Get all files' paths of the repository ")
        files = self.get_all_files_in_the_repository(repository, empty_branch)
        for file in files:
            LOGGER.debug("Deleting file <%s>", file.path)
            repository.delete_file(
                file.path, CONFIG.get_default_commit_message(file.name), file.sha, branch=target_branch_name)
        return empty_branch

    def create_branch_if_not_exist(self, repository: Repository, source_branch_name, target_branch_name) -> Branch:
        """
        If branch does not exist in the forked repository then create it.
        :return: Created/Fetched branch.
        """
        LOGGER.info("Checking if the branch <%s> exists in the repository <%s>", target_branch_name, repository.name)
        if not self.check_if_branch_exists(repository, target_branch_name):
            LOGGER.info("Branch does not exist. Creating new one...")
            branch = self.create_branch(repository, source_branch_name, target_branch_name)
        else:
            branch = repository.get_branch(target_branch_name)
            LOGGER.info("Branch exists. Returning existing one <%s>.", branch.name)
        return branch

    def get_all_files_in_the_repository(
            self, repository: Repository, branch: Branch, directory="") -> List[ContentFile]:
        """
        Get list of paths of all files in the repository on given branch.
        :param repository: Forked repository
        :param branch: Name of the branch.
        :param directory: Starting directory.
        :return: List of all files' paths.
        """
        LOGGER.info("Looking for files in <%s> repository in <%s> branch in <%s> directory.",
                    repository.name,
                    branch.name,
                    directory)
        all_contents = []
        main_dir_contents = repository.get_contents(directory, ref=branch.name)
        while main_dir_contents:
            file_content = main_dir_contents.pop(0)
            if file_content.type == "dir":
                directory_contents = self.get_all_files_in_the_repository(
                    repository, branch, file_content.path,)
                all_contents.extend(directory_contents)
            else:
                all_contents.append(file_content)
        LOGGER.info("Files found in the <%s> directory <%s>.",
                    directory,
                    ", ".join([str(file) for file in all_contents]))
        return all_contents

    @staticmethod
    def get_pull_request(
            repository: Repository, base_branch: Branch, target_branch: Branch) -> Union[None, PullRequest]:
        """
        Check if pull request already exists in forked repository.
        :return: Empty list if PR is not found, fetched PR otherwise.
        """
        LOGGER.info("Checking if Pull Request with base branch <%s> and target branch <%s> exists",
                    base_branch.name,
                    target_branch.name)
        existing_pull_requests = list(repository.get_pulls())
        LOGGER.info("Fetched Pull Requests <%s>", ', '.join([pr.title for pr in existing_pull_requests]))
        base_branch_check = base_branch.name in [pr.base.ref for pr in existing_pull_requests]
        target_branch_check = target_branch.name in [pr.head.ref for pr in existing_pull_requests]
        if base_branch_check and target_branch_check:
            return [pr for pr in existing_pull_requests
                    if pr.base.ref == base_branch.name and pr.head.ref == target_branch.name][0]
        else:
            return None

    @staticmethod
    def check_if_branch_exists(repository: Repository, branch_name) -> bool:
        """
        Check if branch with given name exists in the forked repository.
        :param repository: Forked repository.
        :param branch_name: Name of the branch.
        :return: True if branch already exists in the repository, False otherwise.
        """
        return branch_name in [branch.name for branch in list(repository.get_branches())]

    @staticmethod
    def create_branch(repository: Repository, source_branch_name: str, target_branch_name: str) -> Branch:
        """
        Create branch in the forked repository.
        :param repository: Forked repository.
        :param source_branch_name: Name of the base branch from which target branch is created.
        :param target_branch_name: Target name of the new branch.
        :return: Created branch.
        """
        source_branch = repository.get_branch(source_branch_name)
        repository.create_git_ref(
            ref='refs/heads/' + target_branch_name, sha=source_branch.commit.sha)
        return repository.get_branch(target_branch_name)

    @staticmethod
    def create_pull_request(
            repository: Repository,
            base_branch: Branch,
            head_branch: Branch,
            title: str,
            body: str = "") -> PullRequest:
        """
        Create Pull Request in the forked repository
        :param repository: Forked Repository.
        :param base_branch: Base branch of the PR.
        :param head_branch: Target branch of the PR.
        :param title: Title of the PR.
        :param body: Content of the PR. like Summary etc.
        :return: Created Pull Request.
        """
        LOGGER.info("Creating Pull Request...")
        pull_request = repository.create_pull(
            title=title, body=body, base=base_branch.name, head=head_branch.name)
        LOGGER.info("Created Pull Request <%s>.", pull_request.title)
        return pull_request

    @staticmethod
    def delete_repository(repository: Repository) -> None:
        """
        Delete repository after the Code review is finished.
        :param repository: Repository user wants to delete.
        :return: None
        """
        LOGGER.info("Deleting repository <%s>.", repository.name)
        return repository.delete()
