import unittest
from io import BytesIO
import os
import sqlite3
from flask_testing import TestCase
from app import app, init_db, DATABASE
import tempfile

class FlaskAppTestCase(TestCase):

    # Setting Flask's TESTING configuration flag to True
    TESTING = True

    def create_app(self):
        """Create and return a testing flask app."""
        app.config['TESTING'] = True
        return app

    def setUp(self):
        """Set up test environment before each test."""
        # Remove existing database file if it exists
        if os.path.exists(DATABASE):
            os.remove(DATABASE)

        # Create a temporary file for our test database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
        
        # Create a test client for sending HTTP requests
        self.app = app.test_client()

        # Initialize the database within the app context
        with app.app_context():
            init_db()

    def tearDown(self):
        """Clean up test environment after each test."""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def upload_file(self, filename):
        """
        Helper method to upload a file to the /upload endpoint.
        Returns the HTTP response.
        """
        try:
            with open(filename, 'rb') as f:
                data = {
                    'file': (f, os.path.basename(filename))
                }
                return self.app.post('/upload', data=data, content_type='multipart/form-data')
        except FileNotFoundError:
            return "File not found", 404

    def test_pdf_upload(self):
        """Test file upload functionality for PDFs and other file types."""
        # Test uploading a valid PDF
        response = self.upload_file('test_data/sample.pdf')
        self.assertEqual(response.status_code, 200)

        # Test uploading an invalid file type
        response = self.upload_file('test_data/sample.txt')
        self.assertNotEqual(response.status_code, 200)

    def test_summary_generation(self):
        """Test if a summary is generated upon successful file upload."""
        response = self.upload_file('test_data/sample.pdf')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'summary', response.data)

    def test_exception_handling(self):
        """Test the handling of exceptions during file upload."""
        response = self.upload_file('')
        self.assertEqual(response, ("File not found", 404))

    def test_database_cache(self):
        """Test if the database caches file uploads."""
        # Upload a file for the first time
        response = self.upload_file('test_data/sample.pdf')
        self.assertEqual(response.status_code, 200)

        # Upload the same file again to test caching
        response = self.upload_file('test_data/sample.pdf')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()



