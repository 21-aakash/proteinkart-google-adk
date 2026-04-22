#!/bin/bash
# Deployment script for ProteinKart Startup Backend

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./deploy.sh <PROJECT_ID>"
    exit 1
fi

echo "🚀 Deploying ProteinKart Backend to GCP: $PROJECT_ID"

# 1. Enable APIs
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com --project "$PROJECT_ID"

# 2. Build and Push
gcloud builds submit --tag "gcr.io/$PROJECT_ID/proteinkart-backend" --project "$PROJECT_ID"

# 3. Deploy to Cloud Run
# We allow unauthenticated for the workshop so students can reach the API
gcloud run deploy proteinkart-backend \
    --image "gcr.io/$PROJECT_ID/proteinkart-backend" \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --project "$PROJECT_ID"

echo ""
echo "✅ Backend Live!"
echo "Students should use the provided URL in their MCP servers."
