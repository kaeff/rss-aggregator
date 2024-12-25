gcloud run deploy rss-aggregator \
    --region=europe-west1 \
    --allow-unauthenticated \
    --execution-environment=gen2 \
    --port 8080 \
    --source .