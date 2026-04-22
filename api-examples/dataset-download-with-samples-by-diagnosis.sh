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

if [[ $API_TOKEN_EMAIL == *"example"* ]]; then
  echo "Please accept terms by adding a valid email for API_TOKEN_EMAIL"
  exit 0
fi

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

# STEP 2: PROCESS DATASET

# 1. Authenticate API Key
if [ -f "$API_TOKEN_FILE" ]; then
  # Check if a token file exists.
  API_TOKEN=$(cat $API_TOKEN_FILE)
  echo "Using the API token from $API_TOKEN_FILE"
else
  # Otherwise create a new token and save it to the file
  echo "Creating token using $API_TOKEN_EMAIL"
  # Create a token - This is the important part
  TOKEN_RESPONSE=$(curl -s -X 'POST' \
    "${API_ROOT}/tokens/" \
    -H "Content-Type: application/json" \
    -d "{\"is_activated\": true, \"email\": \"${API_TOKEN_EMAIL}\"}"
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
# See available diagnoses at https://api.scpca.alexslemonade.org/v1/project-options
# Query single-cell samples in ANN_DATA format containing the specified diagnosis
# - Set has_single_cell_data to true for samples with SINGLE_CELL modality
# - Set includes_anndata to true for ANN_DATA format
DIAGNOSIS=Neuroblastoma
HAS_SINGLE_CELL_DATA=true
INCLUDES_ANNDATA=true
LIMIT=2000 # Ignore pagination in this example

SAMPLES_RESPONSE=$(curl -s --get \
    "${API_ROOT}/samples/" \
    -H "Content-Type: application/json" \
    -d "diagnosis=$DIAGNOSIS" \
    -d "has_single_cell_data=$HAS_SINGLE_CELL_DATA" \
    -d "includes_anndata=$INCLUDES_ANNDATA" \
    -d "limit=$LIMIT"
 )

SAMPLE_COUNT=$(echo "$SAMPLES_RESPONSE" | jq '.count')

if [ -z "$SAMPLE_COUNT" ]; then
  # Uh oh, something happened so print the response.
  echo "Error in querying samples:"
  echo "$SAMPLES_RESPONSE" | jq
  echo "Exiting..."
  exit 1
fi

if [ "$SAMPLE_COUNT" = 0 ]; then
  echo "No samples found. Exiting..."
  exit 0
fi

echo "Found $SAMPLE_COUNT samples for the query"

# Populate a dataset from the queried samples
QUERIED_SAMPLES=$(echo "$SAMPLES_RESPONSE" | jq '.results')
# Steps:
# 1. Pipe the results via jq, grouped by project IDs
# 2. Map grouped results, where each key is a project ID and the value of SINGLE_CELL contains the sample IDs
# 3. Convert the mapped array into a JSON object via jq from_entries
# NOTE: Bulk RNA-seq data is excluded in this example (i.e., includes_bulk).
# NOTE: SPATIAL modality is excluded in this example (i.e., SPATIAL).
DATA=$(echo "$QUERIED_SAMPLES" | jq 'group_by(.project) | map({
    key: .[0].project,
    value: {
      SINGLE_CELL: map(.scpca_id),
      SPATIAL:[],
      includes_bulk: false
    }
  }) | from_entries'
)

# Dataset to be processed
DATASET=$(jq -n \
  --argjson data "$DATA" \
  --arg start "$PROCESS_DATASET" \
  --arg email "$API_TOKEN_EMAIL" \
 '{
   "format": "ANN_DATA",
   "data": $data,
   "start": $start,
   "email": $email
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
echo "Starting dataset processing..."
DATASET_RESPONSE=$(curl -s -X POST \
  "${API_ROOT}/datasets/" \
  -H "Content-Type: application/json" \
  -H "API-KEY: $API_TOKEN" \
  -d "$DATASET")

DATASET_ID=$(echo "$DATASET_RESPONSE" | jq '.id')

if [ "$DATASET_ID" = 'null' ] || [ -z "$DATASET_ID" ]; then
  # Uh oh, something happened so print the response.
  echo "Error in starting dataset processing:"
  echo "$DATASET_RESPONSE" | jq
  echo "Exiting..."
  exit 1
fi

echo "Dataset $DATASET_ID has been created."
echo "Once processing is complete, a download link will be sent to $API_TOKEN_EMAIL"

# STEP 3: WAIT AND DOWNLOAD DATASET
# See https://api.scpca.alexslemonade.org/docs/swagger/#/ccdl-datasets/ccdl_datasets_retrieve
if [ "$WAIT_FOR_DOWNLOAD" != true ]; then
  echo "Set WAIT_FOR_DOWNLOAD to true to download dataset. Exiting..."
  exit 0
fi

# Check the dataset status
while true; do
  echo "Dataset still processing. Checking status in 2 minutes..."
  sleep 2m

  # Append the dataset ID to URL
  DATASET_RESPONSE=$(curl -s --get \
    "${API_ROOT}/datasets/${DATASET_ID}" \
    -H "Content-Type: application/json" \
    -H "API-KEY: $API_TOKEN"
  )

  IS_SUCCEEDED=$(echo "$DATASET_RESPONSE" | jq '.is_succeeded')
  IS_FAILED=$(echo "$DATASET_RESPONSE" | jq '.is_failed')

  if [ "$IS_SUCCEEDED" = "true" ]; then
    break
  fi

  if [ "$IS_FAILED" = "true" ]; then
    echo "Dataset processing failed. Exiting..."
    exit 1
  fi

done

DOWNLOAD_URL=$(echo "$DATASET_RESPONSE" | jq -r '.download_url // "null"')

if [ "$DOWNLOAD_URL" = "null" ]; then
  # Uh oh, something happened so print the response.
  echo "Error in response:"
  echo "$DATASET_RESPONSE" | jq
  echo "Exiting..."
  exit 1
fi

# Success
echo "Downloading: $DOWNLOAD_URL"
curl -O "$DOWNLOAD_URL"
echo "Completed Successfully."
