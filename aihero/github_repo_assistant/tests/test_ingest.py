import unittest
from unittest.mock import MagicMock, patch

from ingest import index_data


class TestIngest(unittest.TestCase):
    
    @patch('ingest.read_repo_data')
    def test_index_data_with_mocked_download(self, mock_read_repo):
        # Setup mock return value
        # read_repo_data returns a list of dictionaries with 'content' and other fields
        mock_docs = [
            {
                'content': 'This is a test document content that is long enough to be chunked potentially.',
                'filename': 'test_doc.md',
                'title': 'Test Document'
            }
        ]
        mock_read_repo.return_value = mock_docs
        
        # Call the function under test
        print("\nTesting index_data with mocked repo data...")
        index = index_data(repo_owner='test_owner', repo_name='test_repo')
        
        # Assertions
        self.assertIsNotNone(index)
        # Check if basic search works
        results = index.search("test", num_results=1)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['filename'], 'test_doc.md')
        print("✅ index_data successfully created an index and searched it.")

    def test_chunking_logic(self):
        # Test if index_data correctly calls chunking
        # We can just rely on the fact that if search works on chunks, it's fine.
        # But let's verify if chunking creates chunks.
        
        from ingest import create_chunks
        
        docs = [{
            'content': '1234567890',
            'filename': 'nums.md'
        }]
        
        # size=5, step=2
        # 0:5 -> 12345
        # 2:7 -> 34567
        # 4:9 -> 56789
        # 6:11 -> 7890 (end)
        
        chunks = create_chunks(docs, size=5, step=2)
        print(f"\nTesting chunking logic. Generated {len(chunks)} chunks.")
        
        self.assertTrue(len(chunks) > 1)
        self.assertEqual(chunks[0]['content'], '12345')
        print("✅ chunking logic verification passed.")

if __name__ == '__main__':
    unittest.main()
