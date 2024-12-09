import unittest
from unittest.mock import MagicMock, patch
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup
from crawler import MongoDBClient, crawl, send_analysis, send_doc

class TestMongoDBClient(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_collection = self.mock_client.test.RAW
        self.db_client = MongoDBClient()
        self.db_client.client = self.mock_client  # Mock the MongoDB client

    def test_insert_document_success(self):
        page_json = {
            "_id": "123",
            "url": "https://www.example.com",
            "text_length": 50,
            "text": "Sample HTML content",
            "type": "html"
        }
        self.db_client.insert_document(page_json)
        self.mock_collection.insert_one.assert_called_once_with(page_json)

    def test_insert_document_failure(self):
        self.mock_collection.insert_one.side_effect = PyMongoError("Insert failed")
        page_json = {"key": "value"}
        with self.assertLogs() as log:
            self.db_client.insert_document(page_json)
        self.assertIn("Error inserting document", log.output[0])

class TestCrawl(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = "<html><body><a href='/link1'>Link1</a></body></html>"
        mock_get.return_value = mock_response

        extracted_urls, page_json = crawl("https://www.example.com")

        self.assertIn("https://www.example.com/link1", extracted_urls)
        self.assertEqual(page_json['url'], "https://www.example.com")
        self.assertEqual(page_json['type'], "html")

    @patch('requests.get')
    def test_crawl_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            crawl("https://www.example.com")
        self.assertIn("Failed to retrieve the page", str(context.exception))

class TestSendAnalysis(unittest.TestCase):
    @patch('requests.post')
    def test_send_analysis_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        info = {"url": "www.google.com", "child_nodes": []}
        with self.assertLogs() as log:
            send_analysis(info)
        self.assertIn("Success", log.output[0])

    @patch('requests.post')
    def test_send_analysis_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        info = {"url": "www.google.com", "child_nodes": []}
        with self.assertLogs() as log:
            send_analysis(info)
        self.assertIn("Error", log.output[0])

    @patch('requests.post', side_effect=RequestException("Request failed"))
    def test_send_analysis_request_exception(self, mock_post):
        info = {"url": "www.google.com", "child_nodes": []}
        with self.assertLogs() as log:
            send_analysis(info)
        self.assertIn("Request failed", log.output[0])

class TestSendDoc(unittest.TestCase):
    def setUp(self):
        self.mock_db_client = MagicMock()

    def test_send_doc_success(self):
        page_json = {
            "_id": str(ObjectId()),
            "url": "https://www.example.com",
            "text_length": 50,
            "text": "Sample HTML content",
            "type": "html"
        }

        send_doc(page_json, self.mock_db_client)
        self.mock_db_client.insert_document.assert_called_once_with(page_json)

if __name__ == "__main__":
    unittest.main()
