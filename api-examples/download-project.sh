#! /bin/bash

# Note: This script uses the following which must be installed:
# bash - tested with version: 3.2.57
# jq - https://jqlang.org/ - tested with version: jq-1.7.1-apple
# curl - https://curl.se/ - tested with version: 8.7.1

#
# Mandatory configs for the script
#
# The email address you want to use to create a token.
EMAIL_ADDRESS="user@example.com" # You MUST change this to your email.
# If you already have a token save it to a file located at $TOKEN_FILE
TOKEN_FILE=".token"

#
# Additional Configuration
# 
API_ROOT="https://api.scpca.alexslemonade.org/v1"



#
# Step 1: Find projects of interest.
#

DIAGNOSIS="Ganglioglioma"

PROJECTS_RESPONSE=$(curl -s --get \
  "${API_ROOT}/projects/" \
  -H 'Content-Type: application/json' \
  -d "diagnoses=$DIAGNOSIS" # filtering by Projects that contain samples with $DIAGNOSIS
)

echo "Found $(echo $PROJECTS_RESPONSE | jq '.count') projects."


#
# Step 2: Get the computed files in the format and modality that you want.
#

# Get a flat list of computed files from the projects response.
ALL_COMPUTED_FILES=$(
  echo $PROJECTS_RESPONSE | jq '.results[].computed_files[]'
)

# ARGS for jq filtering
FORMAT="SINGLE_CELL_EXPERIMENT"
MODALITY="SINGLE_CELL"
INCLUDES_MERGED=false
HAS_MULTIPLEXED_DATA=false

COMPUTED_FILES=$(
  echo $ALL_COMPUTED_FILES | jq \
    --arg FORMAT $FORMAT \
    --arg MODALITY $MODALITY \
    --argjson INCLUDES_MERGED $INCLUDES_MERGED \
    --argjson HAS_MULTIPLEXED_DATA $HAS_MULTIPLEXED_DATA \
    '. | select(
      .format == $FORMAT and
      .modality == $MODALITY and
      .includes_merged == $INCLUDES_MERGED and
      .has_multiplexed_data == $HAS_MULTIPLEXED_DATA
    )'
)

# Grab the computed file IDs
COMPUTED_FILE_IDS=$(
  echo $COMPUTED_FILES | jq '.id'
)


#
# Step 1: Create a token to get download urls
#

if [ -f "$TOKEN_FILE" ]; then
  # Check if token file exists.
  echo "Using Token from $TOKEN_FILE"
  TOKEN=`cat $TOKEN_FILE`
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
  TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.id')

  if [ "$TOKEN" = "null" ]; then
    # Uh oh, something happened so print the response.
    echo "Using $EMAIL_ADDRESS"
    echo $TOKEN_RESPONSE | jq
  else
    # Success
    echo "Saving Token to '$TOKEN_FILE'"
    echo $TOKEN > $TOKEN_FILE
  fi
fi


#
# Step 4: Get the download URLs, they expire after 7 days
#
# 
for computed_file_id in $COMPUTED_FILE_IDS; do
  COMPUTED_FILE_RESPONSE=$(curl -s --get \
    "${API_ROOT}/computed-files/$computed_file_id" \
    -H 'Content-Type: application/json' \
    -H "API-KEY: $TOKEN"
  )

  # The id is the API Key that will be used later to get a download url.
  DOWNLOAD_URL=$(echo $COMPUTED_FILE_RESPONSE| jq -r '.download_url')

  if [ "$DOWNLOAD_URL" = "null" ]; then
    # Uh oh, something happened so print the response.
    echo "Error in response."
    echo $COMPUTED_FILE_RESPONSE | jq
    continue
  fi

  # Success
  echo "Signed Download URL for computed file $computed_file_id:"
  echo $DOWNLOAD_URL
  echo "---"
  # Or just download it now.
  # curl -O $download_url
done
