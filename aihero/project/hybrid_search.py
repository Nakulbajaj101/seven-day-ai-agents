import hashlib
import pickle

import numpy as np
from minsearch import Index, VectorSearch
from sentence_transformers import SentenceTransformer


class MinSearch:
    def __init__(self, docs: list, embeddings: np.array, model_name: str='multi-qa-distilbert-cos-v1'):
        self.docs = docs
        self.embeddings = embeddings
        self.index = self.text_index()
        self.v_index = self.vector_index()
        self.embedding_model = SentenceTransformer(f'{model_name}')
        
        
    def text_index(self) -> Index:
        """Creating a text , vast index"""

        index = Index(text_fields=['title', 'description', 'filename', 'section'],
                keyword_fields=[])
        index.fit(self.docs)
        return index

    def vector_index(self) -> VectorSearch:
        """Creating a vector index"""
        
        index = VectorSearch()
        index.fit(self.embeddings, self.docs)
        return index

    def text_search(self, query: str):
        return self.index.search(query, num_results=5)

    def vector_search(self, query: str):
        q = self.embedding_model.encode(query)
        return self.v_index.search(q, num_results=5)

    def hybrid_search(self, query: str):
        text_results = self.text_search(query)
        vector_results = self.vector_search(query)
        
        # Combine and deduplicate results
        seen_ids = set()
        combined_results = []

        for result in text_results + vector_results:
            text_to_hash = result['filename'] + ' ' + result['section'][0:250]
            encoded_string = text_to_hash.encode('utf-8')
            hash_object = hashlib.sha256(encoded_string)
            hex_digest = hash_object.hexdigest()
            if hex_digest not in seen_ids:
                seen_ids.add(result['filename'])
                combined_results.append(result)
        
        return combined_results


if __name__ == "__main__":
    FILE_PATH = "../course/vector_search_data.pkl"
    loaded_data = None
    try:
        with open(FILE_PATH, 'rb') as f:
            loaded_data = pickle.load(f)
        print(f"Data successfully unpickled from {FILE_PATH}")

        # Access the loaded data
        loaded_embeddings = loaded_data['embeddings']
        loaded_docs = loaded_data['documents']


    except FileNotFoundError:
        print(f"Error: The file {FILE_PATH} was not found.")
    except pickle.UnpicklingError as e:
        print(f"An error occurred during unpickling: {e}")

    if len(loaded_embeddings) > 0 and len(loaded_docs) > 0:
        ms = MinSearch(
            docs=loaded_docs,
            embeddings=loaded_embeddings
            )

        query = "How can I evaluate classification model results, and ensure numerical data is not drifted?"
        results = ms.hybrid_search(query=query)

        print(results)