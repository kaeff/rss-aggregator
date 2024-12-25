# RSS Feed Aggregator

This project is a simple RSS feed aggregator built using Python and Flask. It allows users to merge multiple RSS feed URLs into a single output feed, with options to remove duplicates and customize the title of the aggregated feed.

## Features

- Merge multiple RSS feed URLs into one.
- Option to remove duplicate entries based on the feed link.
- Customizable title for the aggregated feed.
- Returns the result as an Atom feed.

## Setup

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd rss-aggregator
   ```

2. **Install dependencies:**
   Navigate to the `src` directory and install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application locally:**
   You can run the Flask application locally for testing:
   ```
   python main.py
   ```

4. **Deploying to Google Cloud Run:**
   - Build the Docker image:
     ```
     docker build -t rss-aggregator .
     ```
   - Deploy to Cloud Run:
     ```
     gcloud run deploy rss-aggregator --image gcr.io/<project-id>/rss-aggregator --platform managed
     ```

## Usage

Once deployed, you can access the aggregator function via the `/merge` endpoint. You can make a GET request with the following parameters:

- `urls`: A comma-separated list of RSS feed URLs.
- `removeDuplicates`: A boolean value (`true` or `false`) to specify if duplicates should be removed.
- `customTitle`: A string to customize the title of the aggregated feed.

### Example Request

```
GET https://<your-cloud-run-url>/merge?urls=https://example.com/feed1.xml,https://example.com/feed2.xml&removeDuplicates=true&customTitle=My%20Aggregated%20Feed
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.