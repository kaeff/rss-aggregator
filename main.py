import asyncio
import re
from fastapi import FastAPI, Request, Response
import feedparser
from feedgen.feed import FeedGenerator
import os
import aiohttp
from urllib.parse import urlparse, urlunparse

app = FastAPI()

@app.get("/merge")
async def merge_feeds(request: Request):
    urls = request.query_params.getlist('urls[]')
    remove_duplicates = request.query_params.get('removeDuplicates', 'false').lower() == 'true'
    custom_title = request.query_params.get('title', 'Aggregated Feed')
    exclude_titles = request.query_params.getlist('excludeTitles[]')

    feeds = await fetch_and_parse_feeds(urls)
    entries = merge_sources(feeds)

    if exclude_titles:
        entries = apply_filters(entries, exclude_titles)

    if remove_duplicates:
        entries = remove_duplicate_entries(entries)
    
    atom_feed = generate_atom_feed(custom_title, entries)   
    return Response(content=atom_feed, media_type="application/atom+xml")

async def fetch_and_parse_feeds(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url) for url in urls]
        feeds = await asyncio.gather(*tasks)
        return feeds

async def fetch_feed(session, url):
    async with session.get(url) as response:
        content = await response.read()
        feed = feedparser.parse(content)
        feed['href'] = url  # Store the URL in the feed for error reporting
        return feed
    
    return feed.entries

def merge_sources(feeds):
    entries = [entry for feed in feeds for entry in feed['entries']]
    entries.sort(key=lambda entry: entry['updated'], reverse=False)
    return entries

def apply_filters(entries, exclude_titles):
        # Filter entries based on exclude_titles
        exclude_patterns = [re.compile(pattern) for pattern in exclude_titles]
        filtered_entries = [
            entry for entry in entries
            if not any(pattern.match(entry['title']) for pattern in exclude_patterns)
        ]
        return filtered_entries

def remove_duplicate_entries(entries):
    def entry_key(entry):
        if 'link' in entry:
            parsed_url = urlparse(entry.get('link', entry['id']))
            return urlunparse(parsed_url._replace(query=''))
        else:
            return entry['id']

    unique_entries = {entry_key(entry): entry for entry in entries}.values()
    return list(unique_entries)

def generate_atom_feed(title, entries):
    fg = FeedGenerator()
    fg.title(title)
    base_url = os.getenv('CLOUD_RUN_SERVICE_URL', 'http://localhost:8080')
    fg.id(base_url)
    fg.link(href=base_url, rel='self')

    for entry in entries:
        fe = fg.add_entry()
        fe.title(entry['title'])
        fe.link(href=entry['link'])
        fe.summary(entry['summary'])
        fe.updated(entry['updated'])
        fe.id(entry['link'])
        if 'author' in entry:
            fe.author(name=entry['author'])

    return fg.atom_str(pretty=True)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)