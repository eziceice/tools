#!/usr/publish/env python3

import argparse
import json
from pathlib import Path
from common import Git, Bitbucket
from utility import *

parser = argparse.ArgumentParser()
parser.add_argument(
    "jira_id",
    metavar="jira-id",
    help="JIRA ticket ID for the relevant card (e.g. IP-123)",
)
parser.add_argument(
    "description",
    help='description of the change being made (e.g. "bump plugin version")',
)
parser.add_argument(
    "--repos-folder",
    default=".",
    help="path to the folder containing the service repos",
)
parser.add_argument(
    "--include",
    default=[],
    help="services not listed in services.json to apply the change to (e.g. --include interestrate screening serviceability)",
)
parser.add_argument(
    "--exclude",
    default=[],
    help="services listed in services.json to not apply the chance to (e.g. --exclude interestrate screening serviceability)",
)
parser.add_argument(
    "--checkout",
    default=[],
    help="files or directory that could be updated from template default is updating plugin version for gradle.properties",
)
args = parser.parse_args()

source_parent = os.path.dirname(os.path.abspath(__file__))
with open(f"{source_parent}/services.json") as f:
    services = json.load(f)

services = set(services).union(args.include).difference(args.exclude)

for service in services:
    print("Applying change to " + service)
    repo_path = Path(args.repos_folder) / f"{service}"
    repo = Git(str(repo_path))

    """
    # perform the cross-cutting change
    """
    kebab_description = args.description.lower().replace(" ", "-")
    current = repo.create_branch(f"feature/{args.jira_id}-{kebab_description}")
    current.checkout()

    print("Adding template service as a remote stream " + constant.TEMPLATE_URL)
    repo.create_remote(constant.TEMPLATE_URL)
    print("Fetching template service latest changes")
    repo.fetch()

    if not args.checkout:
        file = "gradle.properties"
        # Checkout the latest plugin version from template
        print("Reading latest plugin version from template")
        repo.checkout(file, "upstream/master")
        new_plugin_version = read_plugin_version(file, repo_path)
        # Revert the gradle.properties file to the master one
        repo.checkout(file)
        # checkout the file which contains the version
        print("Updating plugin version for " + service)
        update_plugin_version(file, new_plugin_version, repo_path)
    else:
        for file in args.checkout:
            print(f"Pulling {file} from template service")
            repo.checkout(file, "upstream/master")

    repo.add()
    repo.commit(f"feature({args.jira_id}): {args.description}")
    repo.push(current)

bitbucket = Bitbucket()
for service in services:
    bitbucket.open_pr(
        f"{service}",
        f"feature/{args.jira_id}-{kebab_description}",
        f"Crosscut ({args.jira_id}): {args.description}",
    )
    print(f"PR has been created successfully for {service}")
