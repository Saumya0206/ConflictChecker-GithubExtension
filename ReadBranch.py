import requests
import os

# Load GitHub token from environment variable
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'Saumya0206'
REPO_NAME = 'VideoCall-and-Chat'
USERNAME = 'Saumya0206'
BASE_BRANCH = 'master'


# Helper function to make GitHub API requests
def github_api_request(url):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {url}: {response.status_code}")
        return None


# Get list of branches in the repository
def get_branches():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/branches"
    return github_api_request(url)


# Get the commits for a specific branch
def get_branch_commits(branch_name):
    commits_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?sha={branch_name}&per_page=5"
    return github_api_request(commits_url)


# Get files modified between base branch and working branch
def get_branch_files(branch_name):
    compare_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/compare/{BASE_BRANCH}...{branch_name}"
    comparison_data = github_api_request(compare_url)

    if comparison_data:
        return {file_info['filename'] for file_info in comparison_data.get('files', [])}
    return set()


# Find the latest branch with commits by the user
def find_latest_branch(branches):
    latest_branch = None
    latest_commit_time = None

    for branch in branches:
        branch_name = branch['name']
        commits = get_branch_commits(branch_name)

        if commits:
            for commit_info in commits:
                commit_author = commit_info['author']
                if commit_author and commit_author['login'] == USERNAME:
                    commit_date = commit_info['commit']['committer']['date']
                    if not latest_commit_time or commit_date > latest_commit_time:
                        latest_commit_time = commit_date
                        latest_branch = branch_name

    return latest_branch, latest_commit_time


# Find branches that have modified common files
def find_conflicting_branches(base_branch_files, branches, latest_branch):
    conflicting_branches = {}

    for branch in branches:
        branch_name = branch['name']

        if branch_name == latest_branch:
            continue

        branch_files = get_branch_files(branch_name)

        if branch_files:
            common_files = base_branch_files.intersection(branch_files)
            if common_files:
                conflicting_branches[branch_name] = common_files

    return conflicting_branches


# Main function to handle branch and conflict analysis
def main():
    branches = get_branches()
    if not branches:
        print("No branches found.")
        return

    latest_branch, commit_time = find_latest_branch(branches)

    if not latest_branch:
        print("No branches found with your commits.")
        return

    print(f"The branch you are working on is: {latest_branch} (Last commit time: {commit_time})")
    base_branch_files = get_branch_files(latest_branch)

    if base_branch_files:
        print(f"Files modified in branch '{latest_branch}':")
        for file in base_branch_files:
            print(f"  - {file}")

        # Find conflicting branches
        conflicting_branches = find_conflicting_branches(base_branch_files, branches, latest_branch)

        if conflicting_branches:
            print("\nOther branches working on the same files (potential conflicts):")
            for branch, files in conflicting_branches.items():
                print(f"\nBranch '{branch}' has modified the following files:")
                for file in files:
                    print(f"  - {file}")
        else:
            print("\nNo conflicting branches found.")
    else:
        print(f"No files found in branch '{latest_branch}'.")


if __name__ == "__main__":
    main()
