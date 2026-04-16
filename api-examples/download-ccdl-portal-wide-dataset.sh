#! /bin/bash

# Note: This script uses the following which must be installed:
# bash - tested with version: 3.2.57
# jq - https://jqlang.org/ - tested with version: jq-1.7.1-apple
# curl - https://curl.se/ - tested with version: 8.6.0

#
# Mandatory configs for the script
#
# The email address you want to use to create a token.
EMAIL_ADDRESS="user@example.com" # You MUST change this to your email.
# If you already have a token, save it to a file located at $TOKEN_FILE
TOKEN_FILE=".token"

# By default, we only print the signed download URL
# Set this to True if you would like to initiate the download
INITIATE_DOWNLOAD="false"

#
# Additional Configuration
API_ROOT="https://api.scpca.alexslemonade.org/v1"


#
# Step 1: Find CCDL project datasets of interest.
CCDL_PROJECT_ID__ISNULL=true
CCDL_NAME=SINGLE_CELL_SINGLE_CELL_EXPERIMENT

CCDL_DATASETS_RESPONSE=$(curl -s --get \
  "${API_ROOT}/ccdl-datasets/" \
  -H "Content-Type: application/json" \
  -d "ccdl_project_id__isnull=$CCDL_PROJECT_ID__ISNULL" \
  -d "ccdl_name=$CCDL_NAME"
)

echo "Found $(echo "$CCDL_DATASETS_RESPONSE" | jq '.count') projects."

CCDL_PORTAL_WIDE_DATASET=$(
  echo "$CCDL_DATASETS_RESPONSE" | jq '.results[0]'
)
CCDL_PORTAL_WIDE_DATASET_ID=$(
  echo "$CCDL_PORTAL_WIDE_DATASET" | jq -r '.id'
)


#
# Step 2: Create a token to get download urls

if [ -f "$TOKEN_FILE" ]; then
  # Check if token file exists.
  echo "Using Token from $TOKEN_FILE"
  TOKEN=$(cat $TOKEN_FILE)
else
  # Otherwise create a new token and save it to the file
  echo "Creating token:"
  # Create a token - This is the important part
  TOKEN_RESPONSE=$(curl -s -X 'POST' \
    "${API_ROOT}/tokens/" \
    -H 'Content-Type: application/json' \
    -d "{\"is_activated\": true, \"email\": \"${EMAIL_ADDRESS}\"}"
  )

  # The id is the API Key that will be used later to get a download url.
  # -r to remove quotes
  TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.id')

  if [ "$TOKEN" = "null" ]; then
    # Uh oh, something happened so print the response.
    echo "Using $EMAIL_ADDRESS"
    echo "$TOKEN_RESPONSE" | jq
  else
    # Success
    echo "Saving Token to '$TOKEN_FILE'"
    echo "$TOKEN" > $TOKEN_FILE
  fi
fi


#
# Step 3: Get the download URLs, they expire after 7 days
CCDL_DATASET_DOWNLOAD_RESPONSE=$(curl -s --get \
  "${API_ROOT}/ccdl-datasets/$CCDL_PORTAL_WIDE_DATASET_ID" \
  -H 'Content-Type: application/json' \
  -H "API-KEY: $TOKEN"
)

DOWNLOAD_URL=$(echo "$CCDL_DATASET_DOWNLOAD_RESPONSE" | jq -r '.download_url')
DOWNLOAD_FILENAME=$(echo "$CCDL_DATASET_DOWNLOAD_RESPONSE" | jq -r '.download_filename')

if [ "$DOWNLOAD_URL" = "null" ]; then
  # Uh oh, something happened so print the response.
  echo "Error in response."
  echo "$CCDL_DATASET_DOWNLOAD_RESPONSE" | jq
  continue
fi

# Success
echo "Signed Download URL for CCDL Dataset $DOWNLOAD_FILENAME"
echo "$DOWNLOAD_URL"
echo "---"

if [ "$INITIATE_DOWNLOAD" = "true" ]; then
  echo "Downloading: $DOWNLOAD_FILENAME"
  curl -o "$DOWNLOAD_FILENAME" "$DOWNLOAD_URL"
  echo "Finished Downloading: $DOWNLOAD_FILENAME"
else
  echo "Skipping downloading."
fi
