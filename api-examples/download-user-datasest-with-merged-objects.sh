#! /bin/bash

# NOTE: This script uses the following which must be installed:
# bash - tested with version: 3.2.57
# jq - https://jqlang.org/ - tested with version 1.8.1
# curl - https://curl.se/ - tested with version: 8.19.0

# STEP 1: SET UP MANDATORY CONFIGS

# By adding your email, you agree to the terms of service and privacy policy:
# - Terms of Service: https://scpca.alexslemonade.org/terms-of-use
# - Privacy Policy: https://scpca.alexslemonade.org/privacy-policy
#
# Email address is used to:
# - Create a token (a.k.a API Key)
# - Process a dataset for file download
API_TOKEN_EMAIL="user@example.com" # You MUST change this to your email.

# TODO: Add email validation?

# Set this to True if you want to start processing the dataset immediately.
# (For STEP 2: PROCESS DATASET)
PROCESS_DATASET=false

# Set this to True if you want to wait and download the dataset once processing is complete.
# (For STEP 3: WAIT AND DOWNLOAD DATASET)
# NOTE: Dataset processing may take up to 20 minutes.
# NOTE: This option is ignored if PROCESS_DATASET is False.
WAIT_FOR_DOWNLOAD=false

# This is where we will save the token for future calls.
# Token is used to:
# - Process a dataset for file download
# - Retrieve a signed download URL
# NOTE: If you already have a token, save it to a file located at $API_TOKEN_FILE.
API_TOKEN_FILE=".token"

# Public API for the ScPCA Portal:
# See API schema https://api.scpca.alexslemonade.org/docs/swagger/
API_ROOT="https://api.scpca.alexslemonade.org/v1"

API_CONTENT_TYPE='Content-Type: application/json'
API_LIMIT="&limit=2000" # Ignore pagination in this example

# STEP 2: PROCESS DATASET

# 1. Authenticate API Key
if [ -f "$API_TOKEN_FILE" ]; then
  # Check if a token file exists.
  API_TOKEN=$(cat $API_TOKEN_FILE)
  echo "Using the API token from $API_TOKEN_FILE"
else
  # Otherwise create a new token and save it to the file
  echo "Creating token using $API_TOKEN_EMAIL:"
  TOKEN_RESOURCE="${API_ROOT}/tokens/"
  TOKEN_BODY="{\"is_activated\": true, \"email\": \"${API_TOKEN_EMAIL}\"}"

  TOKEN_RESPONSE=$(curl -s -X 'POST' \
    "$TOKEN_RESOURCE" \
    -H "$API_CONTENT_TYPE" \
    -d "$TOKEN_BODY"
  )

  # The id is the API Key that will be used later
  # -r to remove quotes before saving
  API_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.id')

  if [ "$API_TOKEN" = "null" ] || [ -z "$API_TOKEN" ]; then
    # Uh oh, something happened so print the response.
    echo "Error occurred while trying to create a token:"
    echo "$TOKEN_RESPONSE" | jq
    echo "Exiting..."
    exit 1
  else
    # Success
    echo "Saving token to '$API_TOKEN_FILE'"
    echo "$API_TOKEN" > $API_TOKEN_FILE
  fi
fi

# 2. Prepare Dataset
# See available project options at https://api.scpca.alexslemonade.org/v1/project-options
PROJECT_RESOURCE="${API_ROOT}/projects/"
# Query projects in SINGLE_CELL_EXPERIMENT containing the following diagnoses and including merged objects:
# - diagnoses can also be comma separated (e.g., diagnoses=Ganglioglioma, Ependymoma)
# - Set includes_merged_sce to true for merged objects
PROJECT_QUERY="diagnoses=Ganglioglioma&includes_merged_sce=true${API_LIMIT}"

PROJECTS_RESPONSE=$(curl -s --get \
    "$PROJECT_RESOURCE" \
    -H "$API_CONTENT_TYPE" \
    -d "$PROJECT_QUERY"
)

PROJECT_COUNT=$(echo "$PROJECTS_RESPONSE" | jq '.count')

if [ -z "$PROJECT_COUNT" ]; then
  # Uh oh, something happened so print the response.
  echo "Error in querying projects. Exiting..."
  echo "$PROJECTS_RESPONSE" | jq
  exit 1
fi

if [ "$PROJECT_COUNT" = 0 ]; then
  echo "No project founds. Exiting..."
  exit 0
fi

echo "Found $PROJECT_COUNT projects for query:"
echo "$PROJECT_QUERY"

# Populate a dataset from the queried projects
QUERIED_PROJECTS=$(echo "$PROJECTS_RESPONSE" | jq '.results')

# NOTE: Replace "MERGED" with .modality_samples.SINGLE_CELL for individual samples.
# NOTE: Bulk RNA-seq data will be included if available. Set includes_bulk to false to exclude it.
DATA=$(echo "$QUERIED_PROJECTS" | jq 'map({
    key: .scpca_id,
    value: {
      "SINGLE_CELL": "MERGED",
      "SPATIAL": .modality_samples.SPATIAL,
      "includes_bulk": .has_bulk_rna_seq
    }
  }) | from_entries'
)

# Dataset to be processed
DATASET=$(jq -n \
  --argjson data "$DATA" \
  --arg start "$PROCESS_DATASET" \
  --arg email "$API_TOKEN_EMAIL" \
  --arg token "$API_TOKEN" \
 '{
   "format": "SINGLE_CELL_EXPERIMENT",
   "data": $data,
   "start": $start,
   "email": $email,
   "token": $token
  }'
)

echo "Dataset Structure:"
echo "$DATASET" | jq

if [ "$PROCESS_DATASET" != true ]; then
  echo "Set PROCESS_DATASET to true to start processing. Exiting..."
  exit 0
fi

# 3. Process Dataset
# See https://api.scpca.alexslemonade.org/docs/swagger/#/datasets/datasets_create
# NOTE: Dataset processing may take up to 20 minutes.
# NOTE: A download URL will be sent to API_TOKEN_EMAIL once processed.
# NOTE: Download URLs expire after 7 days.

echo "Start processing the dataset..."
DATASET_RESOURCE="${API_ROOT}/datasets/"
DATASET_BODY=$DATASET

DATASET_RESPONSE=$(curl -s -X POST \
  "$DATASET_RESOURCE" \
  -H "$API_CONTENT_TYPE" \
  -H "API-KEY: ${API_TOKEN}" \
  -d "$DATASET_BODY")

DATASET_ID=$(echo "$DATASET_RESPONSE" | jq '.id')

if [ "$DATASET_ID" = 'null' ] || [ -z "$DATASET_ID" ]; then
  # Uh oh, something happened so print the response.
  echo "Error in starting dataset processing. Exiting..."
  echo "$DATASET_RESPONSE" | jq
  exit 1
fi

echo "Dataset $DATASET_ID has been created."
echo "A download link will be sent to $API_TOKEN_EMAIL when processing is complete."

# STEP 3: WAIT AND DOWNLOAD DATASET
# See https://api.scpca.alexslemonade.org/docs/swagger/#/ccdl-datasets/ccdl_datasets_retrieve
if [ "$WAIT_FOR_DOWNLOAD" = true ]; then
  # Check the dataset status
  while true; do
    echo "Dataset still processing. Checking status in 2 minutes..."
    sleep 2m

    # Append the dataset ID
    DATASET_RESOURCE="${API_ROOT}/datasets/${DATASET_ID}"

    DATASET_RESPONSE=$(curl -s --get \
      "$DATASET_RESOURCE" \
      -H "$API_CONTENT_TYPE" \
      -H "API-KEY: ${API_TOKEN}" \ # Required for a download URL
    )

    IS_SUCCEEDED=$(echo "$DATASET_RESPONSE" | jq '.is_succeeded')
    IS_FAILED=$(echo "$DATASET_RESPONSE" | jq '.is_failed')

    if [ "$IS_SUCCEEDED" = "true" ]; then
      break
    fi

    if [ "$IS_FAILED" = "true" ]; then
      echo "Dataset processing failed. Exiting..."
      exit 0
    fi

  done

  DOWNLOAD_URL=$(echo "$DATASET_RESPONSE" | jq -r '.download_url // "null"')

  if [ "$DOWNLOAD_URL" = "null" ]; then
    # Uh oh, something happened so print the response.
    echo "Error in response. Exiting..."
    echo "$DATASET_RESPONSE" | jq
    exit 1
  fi

  # Success
  echo "Downloading: $DOWNLOAD_URL"
  curl -O "$DOWNLOAD_URL"
  echo "Completed Successfully."
fi

echo "Wait and download dataset was skipped."
echo "End of script."
