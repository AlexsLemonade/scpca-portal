import json
import os
import urllib.parse
from pprint import pp
from urllib import request

# STEP 1: SET UP BASE API CONFIGS

# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT

# This is where we will save the token for future calls
API_TOKEN_FILENAME = ".token"

if not API_TOKEN_EMAIL or "example" in API_TOKEN_EMAIL:
    raise Exception("Please accept terms by adding a valid email for API_TOKEN_EMAIL")

# This is all boilerplate to make it easier to make api calls
# API_RESOURCES is pulled from the list shown on https://api.scpca.alexslemonade.org/v1/
API_BASE = "http://localhost:8000/v1/"  # TODO: Temporarily point to localhost for testing
API_RESOURCES = ["datasets", "projects", "samples", "tokens", "project-options"]
API_ENDPOINTS = {resource: f"{API_BASE}{resource}/" for resource in API_RESOURCES}

BASE_HEADERS = {"Accept": "application/json"}
BASE_PARAMS = {"limit": 2000}  # lets ignore pagination for now


# STEP 2: SET UP HELPERS


# Generic API Request method for API_RESOURCES
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
     - id: A string, int, or undefined: Id of resource.
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


# Version 1: Populate the data from queried projects
def get_data(
    projects: list[dict],
    *,
    data_format: str = "SINGLE_CELL_EXPERIMENT",
    excludes_multiplexed: bool = False,
    includes_bulk: bool = False,
    includes_merged: bool = False,
) -> dict[str, dict]:
    """
    Populates a data dictionary from queried projects.
    Accepts:
    - projects: List of queried projects
    - data_format: Data format for your dataset
    - excludes_multiplexed: If True, excludes multiplexed samples
    - includes_bulk: If True, includes bulk data when available
    - includes_merged: If True, merges single-cell samples into 1 object
    """
    data = {}

    for project in projects:
        project_id = project["scpca_id"]

        has_bulk = project["has_bulk_rna_seq"]
        has_multiplexed = project["has_multiplexed_data"]

        modality_samples = project["modality_samples"]
        single_cell_samples = modality_samples["SINGLE_CELL"]
        spatial_samples = modality_samples["SPATIAL"]
        multiplexed_samples = project["multiplexed_samples"]

        single_cell = single_cell_samples

        if has_multiplexed:
            if excludes_multiplexed or data_format == "ANN_DATA":
                # NOTE: Multiplexed samples are not available as AnnData
                single_cell = [s for s in single_cell_samples if s not in multiplexed_samples]
        elif includes_merged:
            # NOTE: Merged objects are not available for projects with multiplexed data
            single_cell = "MERGED"

        data[project_id] = {
            "SINGLE_CELL": single_cell,
            "SPATIAL": spatial_samples,
            "includes_bulk": includes_bulk and has_bulk,
        }

    return data


# Version 2: Populate the data by making a second API call to the samples endpoint using project IDs
def get_data_by_samples(
    projects: list[dict],
    *,
    data_format: str = "SINGLE_CELL_EXPERIMENT",
    excludes_multiplexed: bool = False,
    includes_bulk: bool = False,
    includes_merged: bool = False,
) -> dict[str, dict]:
    """
    Fetches samples for queried projects by project IDs, and populates a data dictionary.
    Accepts:
    - projects: List of queried projects
    - data_format: Data format for your dataset
    - excludes_multiplexed: If True, excludes multiplexed samples
    - includes_bulk: If True, includes bulk data when available
    - includes_merged: If True, merges single-cell samples into 1 object
    """
    data = {}

    for project in projects:
        project_id = project["scpca_id"]

        project_has_bulk = project["has_bulk_rna_seq"]
        project_has_multiplexed = project["has_multiplexed_data"]

        single_cell = []
        spatial = []

        # Projects are added to your data only if they contain samples
        if samples := request_api("samples", query={"project__scpca_id": project_id}).get(
            "results", []
        ):
            for sample in samples:
                sample_id = sample.get("scpca_id")

                has_single_cell = sample["has_single_cell_data"]
                has_spatial = sample["has_spatial_data"]

                if has_single_cell:
                    if project_has_multiplexed and (
                        excludes_multiplexed or data_format == "ANN_DATA"
                    ):
                        # NOTE: Multiplexed samples are not available as AnnData
                        continue
                    single_cell.append(sample_id)

                if has_spatial:
                    spatial.append(sample_id)

            if includes_merged and not project_has_multiplexed:
                # Merge all project single-cell samples into 1 object if requested
                # NOTE: Merged objects are not available for projects with multiplexed data
                single_cell = "MERGED"

            data[project_id] = {
                "SINGLE_CELL": single_cell,
                "SPATIAL": spatial,
                "includes_bulk": includes_bulk and project_has_bulk,
            }

    return data


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
# Set a data format (SINGLE_CELL_EXPERIMENT or ANN_DATA) for your dataset
data_format = "SINGLE_CELL_EXPERIMENT"  # Required upon dataset creation
# Set True if you want to exclude multiplexed samples
excludes_multiplexed = False
# Set True if you want to include Bulk RNA-seq data
includes_bulk = True
# Set True if you want to merge single-cell samples into 1 object
includes_merged = True

# PROJECTS
# NOTE: See available project options by querying project-options (https://api.scpca.alexslemonade.org/v1/project-options)
query = {"diagnoses": "Ganglioglioma"}  # Can also be a list (e.g., ['Ganglioglioma', 'Ependymoma'])

# Append a flag for merged objects if requested
if includes_merged:
    if data_format == "SINGLE_CELL_EXPERIMENT":
        query["includes_merged_sce"] = True
    else:
        query["includes_merged_anndata"] = True

queried_projects = request_api("projects", query=query).get("results", [])

print(
    f"Found {len(queried_projects)} projects for your reuqested query:\n{json.dumps(query, indent=2)}"
)

# Populate a data for your dataset
data = get_data(
    queried_projects, data_format=data_format, includes_bulk=includes_bulk, includes_merged=True
)

print(f"Your dataset includes:\n{json.dumps(data, indent=2)}")

# 3. Create Your Dataset
# DATASETS
# Make API call to create and process your dataset for download.
# You'll be notified via email once your dataset is processed.
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

# 4. (Optional) Download Your Dataset
# NOTE: As an alternative to email notification, you can download your processed dataset via the API

# processed_dataset = request_api("datasets", id=dataset.id, token=API_TOKEN)
# print(f"Signed Download URL for your dataset {dataset.id}")
# print(f"Downloading: {processed_dataset.get("download_url")}")

# request.urlretrieve(download_url, computed_file["s3_key"])
# print(f"Finished Downloading:  {processed_dataset.get("download_url")}")
