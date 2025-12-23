import argparse
import io
import zipfile

import frontmatter
import requests


def read_repo_data(repo_owner, repo_name):
    """Function to read repo data from markdown files"""
    
    base_url = "https://codeload.github.com"
    repo_url = f"{base_url}/{repo_owner}/{repo_name}/zip/refs/heads/main"
    
    resp = requests.get(repo_url)
    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")

    repository_data = []
    with zipfile.ZipFile(io.BytesIO(initial_bytes=resp.content)) as zf:
        for file_info in zf.infolist():
            filename = file_info.filename.lower()
            if not filename.endswith(".md") or filename.endswith(".mdx"):
                continue
            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read()
                    post = frontmatter.loads(content)
                    data = post.to_dict()
                    data['filename'] = filename
                    repository_data.append(data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        return repository_data

def main(repo_owner, repo_name):
    """Function to run the main of reading data from a repo"""

    data = read_repo_data(repo_owner=repo_owner, repo_name=repo_name)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='ExtractGithubRepoData',
                    description='The program helps to extract data from github repos into dict objects',
                    usage='%(prog)s [options]')
    
    parser.add_argument("-o", "--owner", type=str, required=True, help="user name of the github repo owner")
    parser.add_argument("-r", "--repo", type=str, required=True, help="name of the repository on github")

    args = parser.parse_args()

    data = main(repo_owner=args.owner, repo_name=args.repo)
    print(len(data))
    print()
    print(data[1])
    