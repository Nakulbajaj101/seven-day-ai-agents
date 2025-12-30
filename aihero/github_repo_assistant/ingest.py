import io
import zipfile

import frontmatter
import requests
from minsearch import Index
from tqdm.auto import tqdm
from typing_extensions import Dict, List


def read_repo_data(repo_owner, repo_name):
    """Function to read repo data from markdown files"""
    
    base_url = "https://codeload.github.com"
    default_branch = "main"
    repo_url = f"{base_url}/{repo_owner}/{repo_name}/zip/refs/heads/{default_branch}"
    
    resp = requests.get(repo_url)
    
    # Retry with 'master' if 'main' is not found
    if resp.status_code == 404:
        default_branch = "master"
        repo_url = f"{base_url}/{repo_owner}/{repo_name}/zip/refs/heads/{default_branch}"
        resp = requests.get(repo_url)

    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code} (checked 'main' and 'master' branches)")

    repository_data = []
    with zipfile.ZipFile(io.BytesIO(initial_bytes=resp.content)) as zf:
        for file_info in zf.infolist():
            filename = file_info.filename.lower()
            if not filename.endswith((".md", ".mdx")):
                continue
            try:
                with zf.open(file_info) as f_in:
                    content_bytes = f_in.read()
                    try:
                        content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                         # Fallback or skip
                         print(f"Skipping binary/non-utf8 file: {filename}")
                         continue
                         
                    post = frontmatter.loads(content)
                    data = post.to_dict()
                    _, filename_repo = file_info.filename.split('/', maxsplit=1)
                    data['filename'] = filename_repo
                    repository_data.append(data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        return repository_data

def sliding_window(seq, size: int, step: int) -> List[Dict]:
    """Function to create chunks from large docs
    and keep overlapping data"""

    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")
    if size <= step:
        raise ValueError("size must be greater than step")
    n = len(seq)
    chunks = []
    for i in range(0, n, step):
        chunk = seq[i: i+size]
        chunks.append({'start': i, 'content': chunk})
        if i + size >= n:
            break
    return chunks


def create_chunks(repo_data, size:int = 2000, step: int=1000):

    repo_chunks = []
    for doc in tqdm(repo_data):
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content')

        chunks = sliding_window(
            seq=doc_content,
            size=size,
            step=step
        )

        for chunk in chunks:
            chunk.update(doc_copy)
        repo_chunks.extend(chunks)

    return repo_chunks

def index_data(
        repo_owner,
        repo_name,
        chunk=True,
        chunking_params=None,
    ):
    """Function to index the data and add to minseach"""


    docs = read_repo_data(repo_owner, repo_name)

    if chunk:
        if chunking_params is None:
            chunking_params = {'size': 2000, 'step': 1000}
        docs = create_chunks(docs, **chunking_params)

    index = Index(
        text_fields=["content", "filename"],
    )

    # Filter out documents that are missing required keys to prevent minsearch crashes
    valid_docs = []
    for doc in docs:
        try:
            # Force conversion to dict to avoid custom object weirdness
            clean_doc = dict(doc)
            if clean_doc.get('filename') and clean_doc.get('content'):
                valid_docs.append(clean_doc)
            else:
               pass # Skip invalid
        except Exception:
            pass

    docs = valid_docs
    
    if not docs:
        print("❌ Error: No valid documents found after filtering. Indexing aborted.")
        return Index(text_fields=["content", "filename"])

    print(f"Indexing {len(docs)} valid documents...")
    try:
        index.fit(docs)
    except Exception as e:
        print(f"❌ Critical Error during indexing: {e}")
        # Debug print for the first bad doc if any (though we filtered)
        if len(docs) > 0:
            print(f"First doc keys: {docs[0].keys()}")
        raise e
        
    return index
