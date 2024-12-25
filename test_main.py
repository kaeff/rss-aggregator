import pytest
from fastapi.testclient import TestClient
from main import app
import requests
from unittest.mock import patch
from datetime import datetime
import uuid

client = TestClient(app)


@patch('feedparser.parse')
def test_merge_feeds(mock_parse):
    mock_parse.side_effect = [
        {
            'feed': {'title': 'Feed 1'},
            'entries': [
                {
                    'id': 'static-id-1',
                    'title': 'Feed 1 Entry',
                    'link': 'http://example.com/feed1/entry1',
                    'summary': 'Summary of Feed 1 Entry',
                    'updated': '2023-01-01T00:00:00Z'
                }
            ]
        },
        {
            'feed': {'title': 'Feed 2'},
            'entries': [
                {
                    'id': 'static-id-2',
                    'title': 'Feed 2 Entry',
                    'link': 'http://example.com/feed2/entry1',
                    'summary': 'Summary of Feed 2 Entry',
                    'updated': '2023-01-01T00:00:00Z'
                }
            ]
        }
    ]

    response = client.get("/merge", params={
        "urls[]": ["http://example.com/feed1", "http://example.com/feed2"],
        "removeDuplicates": "true",
        "title": "Test Feed"
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/atom+xml"
    assert "<title>Test Feed</title>" in response.text
    assert "<entry>" in response.text

@patch('feedparser.parse')
def test_remove_duplicates(mock_parse):
    mock_parse.side_effect = [
        {
            'feed': {'title': 'Feed 1'},
            'entries': [
                {
                    'id': 'feed-1-entry-1',
                    'title': 'Feed 1 Entry 1',
                    'link': 'http://example.com/feed1/entry1',
                    'summary': 'Summary of Feed 1 Entry',
                    'updated': '2023-01-01T00:00:00Z'
                },
                {
                    'id': 'feed-1-entry-2',
                    'title': 'Feed 1 Duplicate Entry',
                    'link': 'http://example.com/entry2?utm_source=feed1',
                    'summary': 'Summary of Feed 1 Duplicate Entry',
                    'updated': '2023-01-01T00:00:00Z'
                }
            ]
        },
        {
            'feed': {'title': 'Feed 2'},
            'entries': [
                {
                    'id': 'feed-2-entry-1',
                    'title': 'Feed 2 Duplicate Entry',
                    'link': 'http://example.com/entry2?utm_source=feed2',
                    'summary': 'Summary of Feed 2 Duplicate Entry',
                    'updated': '2023-01-01T00:00:00Z'
                }
            ]
        }
    ]

    response = client.get("/merge", params={
        "urls[]": ["http://example.com/feed1", "http://example.com/feed2"],
        "removeDuplicates": "true",
        "title": "Test Feed"
    })
    assert response.status_code == 200
    assert response.text.count("<entry>") == 2