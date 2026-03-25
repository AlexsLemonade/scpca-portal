import json
import os
import sys
import urllib.parse
from pprint import pp
from time import sleep
from urllib import request

# STEP 1: SET UP BASE API CONFIGS

# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
# By adding your email, you agree to the terms of service and privacy policy:
# - Terms of Service: https://scpca.alexslemonade.org/terms-of-use
# - Privacy Policy: https://scpca.alexslemonade.org/privacy-policy
#
# Email address is used to:
# - Create a API token
# - Process a dataset for file download
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT

# Set this to True if you want to start processing the dataset immediately.
# (For 3. Process Dataset)
PROCESS_DATASET = False

# Set this to True if you want to wait and download the dataset once processing is complete.
# (For 4. Wait and Download Dataset)
# NOTE: Dataset processing may take up to 20 minutes.
# NOTE: This option is ignored if PROCESS_DATASET is False.
WAIT_FOR_DOWNLOAD = False

# This is where we will save the token for future calls
# Token is used to:
# - Process a dataset for file download
# - Retrieve a signed download URL
API_TOKEN_FILENAME = ".token"

if not API_TOKEN_EMAIL or "example" in API_TOKEN_EMAIL:
    raise Exception("Please accept terms by adding a valid email for API_TOKEN_EMAIL")

# This is all boilerplate to make it easier to make API calls
# API_RESOURCES is pulled from the list shown on https://api.scpca.alexslemonade.org/v1/
API_BASE = "https://api.scpca.alexslemonade.org/v1/"
API_RESOURCES = [
    "ccdl-datasets",
    "computed-files",
    "datasets",
    "projects",
    "samples",
    "tokens",
    "project-options",
]
API_ENDPOINTS = {resource: f"{API_BASE}{resource}/" for resource in API_RESOURCES}

BASE_HEADERS = {"Accept": "application/json"}
BASE_PARAMS = {"limit": 2000}  # Let's ignore pagination for now


# STEP 2: SET UP API HELPER


def request_api(
    resource: str,
    id: str | int | None = None,
    *,  # Use the following as keyword arguments to prevent confusion
    query: dict = {},
    body: dict | None = None,
    token: str | None = None,
    method: str = "GET",
) -> dict:
    """
    Generic API Wrapper.
    Accepts:
     - resource: A string that is defined in API_RESOURCES. Ex: "samples"
     - id: A string, int, or undefined: Id of resource. Ex: project.scpca_id
     - query: A query parameters as a dict to be urlencoded to tack onto the request.
     - body: A dict that is the payload of your request.
     - token: A authenticated API token to add to the request headers.
     - method: HTTP Method: ex: "GET" or "POST" - defaults to "GET"
    """
    # Only continue if trying to access a known API resource
    try:
        resource_url = API_ENDPOINTS[resource]
    except KeyError:
        print(f"{resource} is not an API resource, options are {API_RESOURCES}")

    # If ID is passed, tack it to end of request
    if id is not None:
        resource_url += f"{id}/"

    if not id or query:  # Adding not id to always list out all items without pagination
        # Convert lists to comma-separated strings
        formatted_query = {}
        for key, value in query.items():
            if isinstance(value, list):
                formatted_query[key] = ",".join(str(v) for v in value)
            else:
                formatted_query[key] = value

        query_params = BASE_PARAMS.copy()
        query_params.update(formatted_query)
        resource_url += f"?{urllib.parse.urlencode(query_params)}"

    # Convert body to JSON if provided
    data = None
    if body:
        data = json.dumps(body).encode("utf-8")

    # If passed, set headers
    headers = BASE_HEADERS.copy()
    if body:
        headers["Content-Type"] = "application/json"
    if token:
        headers["API-KEY"] = token

    print(f"{method}: {resource_url}")
    if headers:
        print("Headers:")
        pp(headers)
    if data:
        print("Payload")
        pp(body)

    httprequest = request.Request(resource_url, data=data, headers=headers, method=method)

    with request.urlopen(httprequest) as response:
        resp = json.loads(response.read().decode())

    return resp


# STEP 3: DATASET DOWNLOAD

# 1. Authenticate API TOKEN
API_TOKEN = None
# Here we are creating a token using the above helper method.
# This also will save the file locally to API_TOKEN_FILENAME to use for future calls.
# Please try to re-use your tokens and don't create a new one for every request.
if not os.path.isfile(API_TOKEN_FILENAME):
    print(f"Fetching token with {API_TOKEN_EMAIL}")
    # This is the payload that you need to send to /tokens to get an active API_TOKEN
    API_TOKEN_BODY = {"email": API_TOKEN_EMAIL, "is_activated": True}
    try:
        token_response = request_api("tokens", body=API_TOKEN_BODY, method="POST")
    except Exception as e:
        print("ERROR: The following error occurred while trying to create an API token:")
        print(f"ERROR: {e}")
        exit()

    token = dict(token_response)
    API_TOKEN = token.get("id")

    if API_TOKEN:
        print(f"Saving token to {API_TOKEN_FILENAME}")
        with open(API_TOKEN_FILENAME, "w") as f:
            f.write(API_TOKEN)
else:
    with open(API_TOKEN_FILENAME, "r") as f:
        print("Using existing token")
        API_TOKEN = f.readlines()[0].strip()

# 2. Prepare Dataset
# SAMPLES
# See available diagnoses at https://api.scpca.alexslemonade.org/v1/project-options
# Query samples in ANN_DATA format containing the specified diagnosis
# - Set has_single_cell_data to True for SINGLE_CELL modality samples
# - Set includes_anndata to True for samples in ANN_DATA format
query = {"diagnosis": "Neuroblastoma", "has_single_cell_data": True, "includes_anndata": True}

queried_samples = request_api("samples", query=query).get("results", [])

print(f"Found {len(queried_samples)} samples for query:")
pp(query)

# Populate a dataset from queried_samples
dataset = {
    "format": "ANN_DATA",  # Required upon dataset creation
    "data": {},
    "start": PROCESS_DATASET,
    "email": API_TOKEN_EMAIL,
}

# NOTE: Bulk RNA-seq data will be excluded in this example (i.e., includes_bulk).
for sample in queried_samples:
    project_id = sample["project"]
    sample_id = sample["scpca_id"]

    # Initialize the project data
    if project_id not in dataset["data"]:
        dataset["data"][project_id] = {
            "SINGLE_CELL": [],
            "SPATIAL": [],
            "includes_bulk": False,
        }

    if sample["has_single_cell_data"]:
        dataset["data"][project_id]["SINGLE_CELL"].append(sample_id)

    if sample["has_spatial_data"]:
        dataset["data"][project_id]["SPATIAL"].append(sample_id)

print("Dataset Structure:")
pp(dataset)

if not PROCESS_DATASET:
    print("Set PROCESS_DATASET to true to start processing. Exiting...")
    sys.exit(0)

# 3. Process Dataset
# See https://api.scpca.alexslemonade.org/docs/swagger/#/datasets/datasets_create
# NOTE: Dataset processing may take up to 20 minutes.
# NOTE: A download URL will be sent to API_TOKEN_EMAIL once processed.
# NOTE: Download URLs expire after 7 days.

# Replace your locally populated dataset with the API response.
print("Start processing the dataset...")
dataset = request_api(
    "datasets",
    body=dataset,
    token=API_TOKEN,
    method="POST",
)

print(
    f"Dataset {dataset["id"]} has been created. A download link will be sent to {API_TOKEN_EMAIL} when processing is complete."
)

# 4. Wait and Download Dataset
# See https://api.scpca.alexslemonade.org/docs/swagger/#/ccdl-datasets/ccdl_datasets_retrieve

if WAIT_FOR_DOWNLOAD:
    # Check the dataset status
    while True:
        print("Dataset still processing. Checking status in 2 minutes...")
        sleep(60 * 2)
        dataset = request_api("datasets", id=dataset["id"], token=API_TOKEN)

        if dataset["is_succeeded"] == True:
            break

        if dataset["is_failed"] == True:
            print("Dataset processing failed. Exiting...")
            sys.exit(1)

    download_url = dataset["download_url"]
    print(f"Downloading: {download_url}")

    request.urlretrieve(download_url, dataset["s3_key"])
    print(f"Completed Successfully.")
