import json
import os
import urllib.parse
from pprint import pp
from urllib import request

# STEP 1: SET UP BASE API CONFIGS

# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
# By adding your email, you agree to the terms of service and privacy policy:
# - Terms of Service: https://scpca.alexslemonade.org/terms-of-use
# - Privacy Policy: https://scpca.alexslemonade.org/privacy-policy
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT

# Set this to True if you'd like to start processing your dataset for file download
PROCESS_DATASET = False
# Set this to True if you'd like for requested files to be downloaded at the end of the script
# NOTE: Your dataset is available for download only after processing is complate
DOWNLOAD_DATASET = False

# This is where we will save the token for future calls
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

# 2. Prepare Your Dataset
# Set a data format (SINGLE_CELL_EXPERIMENT or ANN_DATA)
data_format = "SINGLE_CELL_EXPERIMENT"  # Required upon dataset creation

# PROJECTS
print(f"See available project options by querying project-options: {API_BASE}/project-options")
# Let's query projects containing the following diagnoses and including mergd objects
# - diagnoses can also be a list  (e.g., ['Ganglioglioma', 'Ependymoma'])
# - Use the includes_merged_anndata flag for ANN_DATA
query = {"diagnoses": "Ganglioglioma", "includes_merged_sce": True}

queried_projects = request_api("projects", query=query).get("results", [])

print(f"Found {len(queried_projects)} projects for query:")
pp(query)

# Let's build your dataset
dataset = {
    "format": data_format,
    "data": {},
    "start": PROCESS_DATASET,  # Set True to process your dataset immediately
    "email": API_TOKEN_EMAIL,  # Required for email notification
}

# Let's populate a data dictionary from the queried projects
# NOTE: Replace "MERGED" with project["modality_samples"]["SINGLE_CELL"] if you prefer no merged objects
for project in queried_projects:
    dataset["data"][project["scpca_id"]] = {
        "SINGLE_CELL": "MERGED",  # Marks all single-cell samples as one merged object
        "SPATIAL": project["modality_samples"]["SPATIAL"],
        "includes_bulk": project["has_bulk_rna_seq"],  # Include bulk data if available
    }

print("Your dataset includes:")
pp(dataset["data"])


# 3. Create Your Dataset
# See https://api.staging.scpca.alexslemonade.org/docs/swagger/#/datasets/datasets_create

# DATASETS
dataset = request_api(
    "datasets",
    body=dataset,
    token=API_TOKEN,  # Required for dataset processing
    method="POST",
)

if PROCESS_DATASET:
    # You'll receive a download link via email once your dataset is processed.
    print(f"Check your email {API_TOKEN_EMAIL} for the dataset download notification.")
    # NOTE: You'll need to accept terms again when downloading your dataset via the email link in a browser.
else:
    # You can view your dataset via our public API
    print(f"Your dataset has been created: {API_BASE}/{dataset["id"]}")

# 4. (Optional) Download Your Dataset
# See https://api.staging.scpca.alexslemonade.org/docs/swagger/#/ccdl-datasets/ccdl_datasets_retrieve
# NOTE: Instead of using the email link, you can download the processed dataset directly via the API.

if DOWNLOAD_DATASET:
    dataset_id = dataset[
        "id"
    ]  # Add your processed dataset ID here (UUID available via the email link)

    processed_dataset = request_api(
        "datasets", id=dataset_id, token=API_TOKEN  # Required for dataset download
    )

    download_url = processed_dataset["download_url"]
    print(f"Signed Download URL for your dataset {dataset_id}")
    print(f"Downloading: {download_url}")

    request.urlretrieve(download_url, processed_dataset["s3_key"])
    print(f"Finished Downloading: {download_url}")
