import git
import requests
from getpass import getpass
from git import GitCommandError


class Git:
    def __init__(self, repo_location):
        self.repo = git.Repo(repo_location)

    def create_branch(self, branch_name):
        return self.repo.create_head(branch_name)

    def add(self, file="--all"):
        self.repo.git.add(file)

    def commit(self, commit_msg):
        self.repo.index.commit(commit_msg)

    def fetch(self):
        self.repo.remotes.upstream.fetch()

    def checkout(self, directory_or_file_path, stream="master"):
        self.repo.git.checkout(stream, directory_or_file_path)

    def create_remote(self, upstream_url):
        try:
            self.repo.create_remote("upstream", upstream_url)
        except GitCommandError as e:
            print("Remote upstream has been created already")

    # TODO: this should be async
    def push(self, branch):
        self.repo.git.push("origin", branch)


class Bitbucket:
    def __init__(self, username=None, password=None):
        self._username = username
        self._password = password
        self._my_id = None

    def get_creds(self):
        while self._username is None or self._password is None:
            username = self._username or input("Bitbucket username: ")
            password = self._password or getpass("Bitbucket password: ")

            creds_valid = (
                requests.get(
                    "https://api.bitbucket.org/2.0/user",
                    auth=(username, password),
                ).status_code
                == 200
            )

            if creds_valid:
                self._username = username
                self._password = password
            else:
                print("invalid credentials, try again")

        return (self._username, self._password)

    # TODO: this can be made redundant by setting _my_id in get_creds
    def get_my_id(self):
        if self._my_id is None:
            self._my_id = requests.get(
                "https://api.bitbucket.org/2.0/user", auth=self.get_creds()
            ).json()["uuid"]

        return self._my_id

    # TODO: this should be async
    def get_default_reviewers(self, repo_slug, attribute=None):
        url = f"path to the repository"
        reviewers = []

        # consume pages
        while url is not None:
            response = requests.get(url, auth=self.get_creds()).json()
            reviewers += response["values"]
            url = response.get("next")

        # filter out the author
        reviewers = [
            person
            for person in reviewers
            if person["uuid"] != self.get_my_id()
        ]

        # return a particular attribute (for use in another request you want the 'uuid')
        if attribute:
            reviewers = [
                {attribute: person[attribute]} for person in reviewers
            ]

        return reviewers

    # TODO: this should be async
    def open_pr(self, repo_slug, branch, title, reviewers=None):
        url = f"https://api.bitbucket.org/2.0/repositories/{repo_slug}/pullrequests"
        if reviewers is None:
            reviewers = self.get_default_reviewers(repo_slug, attribute="uuid")

        payload = {
            "title": title,
            "source": {"branch": {"name": branch}},
            "reviewers": reviewers,
        }

        response = requests.post(url, json=payload, auth=self.get_creds())

        if response.status_code != 201:
            raise ValueError(f"couldn't create PR: {response.text}")
