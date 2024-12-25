import pytest
from fastapi.testclient import TestClient
from main import app
import requests
from unittest.mock import patch
from datetime import datetime
import uuid
import re
import xml.etree.ElementTree as ET

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

@patch('feedparser.parse')
def test_filter_entries_by_title(mock_parse):
    mock_parse.side_effect = [
        {
            'feed': {'title': 'Feed 1'},
            'entries': [
                {
                    'id': 'feed-1-entry-1',
                    'title': 'Podcast: Feed 1 Entry 1',
                    'link': 'http://example.com/feed1/entry1',
                    'summary': 'Summary of Feed 1 Entry 1',
                    'updated': '2023-01-01T00:00:00Z'
                },
                {
                    'id': 'feed-1-entry-2',
                    'title': 'Feed 1 Entry 2',
                    'link': 'http://example.com/feed1/entry2',
                    'summary': 'Summary of Feed 1 Entry 2',
                    'updated': '2023-01-01T00:00:00Z'
                },
                {
                    'id': 'feed-1-entry-3',
                    'title': 'Feed 1 News Roundup: Entry 3',
                    'link': 'http://example.com/feed1/entry3',
                    'summary': 'Summary of Feed 1 Entry 3',
                    'updated': '2023-01-01T00:00:00Z'
                }
            ]
        }
    ]

    response = client.get("/merge", params={
        "urls[]": ["http://example.com/feed1"],
        "excludeTitles[]": ["^Podcast:", "News Roundup"],
    })
    print(response.content)
    assert response.text.count("<entry>") == 1
    assert "Podcast: Feed 1 Entry 1" not in response.text
    assert "Feed 1 News Roundup: Entry 3" not in response.text
    assert "Feed 1 Entry 2" in response.text

@patch('feedparser.parse')
def test_merged_entries_sorted_by_updated(mock_parse):
    mock_parse.side_effect = [
        {
            'feed': {'title': 'Feed 1'},
            'entries': [
                {
                    'id': 'feed-1-entry-1',
                    'title': 'Feed 1 Entry 1',
                    'link': 'http://example.com/feed1/entry1',
                    'summary': 'Summary of Feed 1 Entry 1',
                    'updated': '2023-01-03T00:00:00Z'
                },
                {
                    'id': 'feed-1-entry-2',
                    'title': 'Feed 1 Entry 2',
                    'link': 'http://example.com/feed1/entry2',
                    'summary': 'Summary of Feed 1 Entry 2',
                    'updated': '2023-01-01T00:00:00Z'
                }
            ]
        },
        {
            'feed': {'title': 'Feed 2'},
            'entries': [
                {
                    'id': 'feed-2-entry-1',
                    'title': 'Feed 2 Entry 1',
                    'link': 'http://example.com/feed2/entry1',
                    'summary': 'Summary of Feed 2 Entry 1',
                    'updated': '2023-01-02T00:00:00Z'
                }
            ]
        }
    ]

    response = client.get("/merge", params={
        "urls[]": ["http://example.com/feed1", "http://example.com/feed2"],
        "title": "Sorted Feed"
    })

    assert response.status_code == 200
    root = ET.fromstring(response.content)
    
    updated_dates = [entry.find("{http://www.w3.org/2005/Atom}updated").text for entry in root.findall("{http://www.w3.org/2005/Atom}entry")]
    # assert updated_dates == sorted(updated_dates, reverse=True)
    assert updated_dates[0].startswith('2023-01-03')
    assert updated_dates[1].startswith('2023-01-02')
    assert updated_dates[2].startswith('2023-01-01')
    # assert updated_dates == sorted(updated_dates, reverse=True)
