import json
import os
import urllib.parse
from pprint import pp
from urllib import request

# STEP 1: SET UP BASE API CONFIGS

# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT
# NOTE: By adding your email, you agree to the terms of service and privacy policy:
# Terms of Service: https://scpca.alexslemonade.org/terms-of-use
# Privacy Policy: https://scpca.alexslemonade.org/privacy-policy

# This is where we will save the token for future calls
API_TOKEN_FILENAME = ".token"

if not API_TOKEN_EMAIL or "example" in API_TOKEN_EMAIL:
    raise Exception("Please accept terms by adding a valid email for API_TOKEN_EMAIL")

# This is all boilerplate to make it easier to make API calls
# API_RESOURCES is pulled from the list shown on https://api.scpca.alexslemonade.org/v1/
API_BASE = "http://localhost:8000/v1/"  # TODO: Temporarily point to localhost for testing
API_RESOURCES = ["datasets", "projects", "samples", "tokens", "project-options"]
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

    data = None
    if body:
        data = urllib.parse.urlencode(body).encode("utf-8")

    # If passed, attach api-key header
    headers = BASE_HEADERS.copy()
    if token:
        headers["API-KEY"] = token

    print(f"{method}: {resource_url}")
    if data:
        print("Payload")
        pp(body)
    if headers:
        print("Headers:")
        pp(headers)

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
if os.path.isfile(API_TOKEN_FILENAME):
    with open(API_TOKEN_FILENAME, "r") as f:
        API_TOKEN = f.readlines()[0].strip()
        print("Using existing token", API_TOKEN)
else:
    print(f"Fetching token with {API_TOKEN_EMAIL}")
    # This is the payload that you need to send to /tokens to get an active API_TOKEN
    API_TOKEN_BODY = {"email": API_TOKEN_EMAIL, "is_activated": True}
    token = request_api("tokens", body=API_TOKEN_BODY, method="POST")

    token = dict(token)
    API_TOKEN = token.get("id")

    print(f"Saving token to {API_TOKEN_FILENAME}")
    with open(API_TOKEN_FILENAME, "w") as f:
        f.writelines(API_TOKEN)

# 2. Prepare Your Dataset
# Set a data format (SINGLE_CELL_EXPERIMENT or ANN_DATA)
data_format = "SINGLE_CELL_EXPERIMENT"  # Required upon dataset creation

# PROJECTS
# NOTE: See available project options by querying project-options (https://api.scpca.alexslemonade.org/v1/project-options)
# We'll query projects containing the following diagnoses and including mergd objects
query = {"diagnoses": "Ganglioglioma"}  # Can also be a list (e.g., ['Ganglioglioma', 'Ependymoma'])

# Append the appropriate flag for merged objects based on the specified data format
if data_format == "SINGLE_CELL_EXPERIMENT":
    query["includes_merged_sce"] = True
else:
    query["includes_merged_anndata"] = True

queried_projects = request_api("projects", query=query).get("results", [])

print(
    f"Found {len(queried_projects)} projects for your reuqested query:\n{json.dumps(query, indent=2)}"
)

# Let's populate a data dictionary from the queried projects
MERGED = "MERGED"  # This constant marks all single-cell samples as 1 merged object

data = {}
for project in queried_projects:
    data[project["scpca_id"]] = {
        "SINGLE_CELL": MERGED,
        "SPATIAL": project["modality_samples"]["SPATIAL"],
        "includes_bulk": project["has_bulk_rna_seq"],  # Bulk data is included if available
    }

print(f"Your dataset includes:\n{json.dumps(data, indent=2)}")

# 3. Create Your Dataset
# See https://api.staging.scpca.alexslemonade.org/docs/swagger/#/datasets/datasets_create

# DATASETS
# Make a API call to create and process your dataset for download.
# You'll receive a download link via email once your dataset is processed.
if data:
    dataset = request_api(
        "datasets",
        body={
            "format": data_format,
            "data": data,
            "start": True,  # Set True to process your dataset immediately
            "email": API_TOKEN_EMAIL,  # Required for email notification
        },
        token=API_TOKEN,
        method="POST",
    )

print(f"Check your email {API_TOKEN_EMAIL} for the dataset download notification.")
# NOTE: You'll need to accept terms again on the browser, when downloading your dataset via the email link.

# 4. (Optional) Download Your Dataset
# NOTE: Instead of using the email link, you can download the processed dataset directly via the API.

# dataset_id = "" # Add your processed dataset ID here (UUID available via the email link)

# processed_dataset = request_api("datasets", id=dataset_id, token=API_TOKEN)

# download_url = processed_dataset["download_url"]
# print(f"Signed Download URL for your dataset {dataset_id}")
# print(f"Downloading: {download_url}")

# request.urlretrieve(download_url, processed_dataset["s3_key"])
# print(f"Finished Downloading: {download_url}")
