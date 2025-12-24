import argparse
import io
import zipfile

import frontmatter
import requests
from config import prompt_template
from openai import OpenAI
from tqdm.auto import tqdm


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

def sliding_window(seq, size, step):
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")
    if size <= step:
        raise ValueError("size must be greater than step")
    n = len(seq)
    chunks = []
    for i in range(0, n, step):
        chunk = seq[i: i+size]
        chunks.append({'start': i, 'chunk': chunk})
        if i + size >= n:
            break
    return chunks

def split_markdown_by_level(text, level=2):
    """
    Split markdown text by a specific header level.
    
    :param text: Markdown text as a string
    :param level: Header level to split on
    :return: List of sections as strings
    """
    # This regex matches markdown headers
    # For level 2, it matches lines starting with "## "
    header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
    pattern = re.compile(header_pattern, re.MULTILINE)

    # Split and keep the headers
    parts = pattern.split(text)
    
    sections = []
    for i in range(1, len(parts), 3):
        # We step by 3 because regex.split() with
        # capturing groups returns:
        # [before_match, group1, group2, after_match, ...]
        # here group1 is "## ", group2 is the header text
        header = parts[i] + parts[i+1]  # "## " + "Title"
        header = header.strip()

        # Get the content after this header
        content = ""
        if i+2 < len(parts):
            content = parts[i+2].strip()

        if content:
            section = f'{header}\n\n{content}'
        else:
            section = header
        sections.append(section)
    
    return sections

class OpenAIClient:
    def __init__(self, model):
        self.model = model
        self._client = OpenAI()

    def llm(self, prompt):
        messages = [
        {"role": "user", "content": prompt}
        ]

        response = self._client.responses.create(
            model=f'{self.model}',
            input=messages
            )

        return response.output_text

class IntelligentChunking(OpenAIClient):
    def __init__(self, openai_model):
        super().__init__(self, model=openai_model)
    
    def intelligent_chunking(self, text):
        prompt = prompt_template.format(document=text)
        response = self.llm(prompt)
        sections = response.split('---')
        sections = [s.strip() for s in sections if s.strip()]
        return sections


def create_chunks(repo_data, model_name):

    repo_chunks = []
    for doc in tqdm(repo_data):
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content')

        ic = IntelligentChunking(openai_model=model_name)
        sections = ic.intelligent_chunking(text=doc_content)
        for section in sections:
            section_doc = doc_copy.copy()
            section_doc['section'] = section
            repo_chunks.append(section_doc)
    
    return repo_chunks


def main(repo_owner, repo_name, model_name):
    """Function to run the main of reading data from a repo"""

    repo_data = read_repo_data(repo_owner=repo_owner, repo_name=repo_name)
    repo_intelligent_chunked_data = create_chunks(repo_data=repo_data, model_name=model_name)
    return repo_intelligent_chunked_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='ExtractGithubRepoData',
                    description='The program helps to extract data from github repos into dict objects',
                    usage='%(prog)s [options]')
    
    parser.add_argument("-o", "--owner", type=str, required=True, help="user name of the github repo owner")
    parser.add_argument("-r", "--repo", type=str, required=True, help="name of the repository on github")
    parser.add_argument("-m", "--model", type=str, required=False, help="name of openai model")
    args = parser.parse_args()

    # Extract and chunk data
    data = main(repo_owner=args.owner, repo_name=args.repo, model_name=args.model)
    print(data)
