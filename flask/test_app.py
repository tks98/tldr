import unittest
from unittest.mock import patch, Mock
from io import BytesIO
from app import app  # Assuming the provided code is saved in a file named `app.py`.

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('app.extract_text_from_pdf', return_value="Sample text from PDF")
    @patch('app.query_db', return_value=[])
    @patch('app.openai_summarization', return_value="Summarized text")
    @patch('app.get_db')
    def test_upload_file(self, mock_db, mock_extract, mock_query, mock_summarize):
        mock_db.return_value.execute.return_value = Mock()  # mock the database execute method
        data = {
            'file': (BytesIO(b'Some mock bytes'), 'sample.pdf')
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Summarized text', response.data)

    @patch('app.extract_text_from_pdf', return_value="Sample text from PDF")
    @patch('app.query_db', return_value=[("Cached Summarized text",)])
    @patch('app.openai_summarization', return_value="This should not be returned")
    def test_upload_file_with_cached_summary(self, mock_extract, mock_query, mock_summarize):
        data = {
            'file': (BytesIO(b'Some mock bytes'), 'sample.pdf')
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cached Summarized text', response.data)
        mock_extract.assert_not_called()  # Ensure extract_text_from_pdf was not called


    @patch('app.extract_text_from_pdf', return_value="Sample text from PDF")
    @patch('app.query_db', return_value=[])
    @patch('app.openai_summarization', side_effect=Exception("OpenAI Error"))
    def test_upload_file_with_openai_error(self, mock_extract, mock_query, mock_summarize):
        data = {
            'file': (BytesIO(b'Some mock bytes'), 'sample.pdf')
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Error occurred during summarization.", response.data)

if __name__ == '__main__':
    unittest.main()
