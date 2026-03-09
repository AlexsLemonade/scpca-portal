import json
import os
import urllib.parse
from pprint import pp
from urllib import request

# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT
# this is where we will save the token for future calls
API_TOKEN_FILENAME = ".token"

if not API_TOKEN_EMAIL or "example" in API_TOKEN_EMAIL:
    raise Exception("Please accept terms by adding a valid email for API_TOKEN_EMAIL")

# This is all boiler plate to make it easier to make api calls
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
BASE_PARAMS = {"limit": 2000}  # lets ignore pagination for now


# Generic API Request method for tokens, samples, projects etc
def request_api(
    resource: str,
    id: str | int | None = None,
    *,  # use the following as keyword arguments to prevent confusion
    query: dict = {},
    body: dict | None = None,
    token: str | None = None,
    method: str = "GET",
) -> dict:
    """
    Genertic API Wrapper.
    Accepts:
     - resource: A string that is definied in API_RESOURCES. Ex: "samples"
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

    # if ID is passed, tack it to end of reuqest
    if id is not None:
        resource_url += f"{id}/"

    if not id or query:  # adding not id to always list out all items without pagination
        query_params = BASE_PARAMS.copy()
        query_params.update(query)
        resource_url += f"?{urllib.parse.urlencode(query_params)}"

    data = None
    if body:
        data = urllib.parse.urlencode(body).encode("utf-8")

    # if passed attach api-key header
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


# API TOKEN

API_TOKEN = None
# Here we are creating a token using the above helper method.
# This also will save the file locally to API_TOKEN_FILENAME to use for future calls.
# Please try to re-use your tokens and don't create a new one for every request.
if os.path.isfile(API_TOKEN_FILENAME):
    with open(API_TOKEN_FILENAME, "r") as f:
        print("Using existing token")
        API_TOKEN = f.readlines()[0].strip()
else:
    print(f"Fetching token with {API_TOKEN_EMAIL}")
    # This is the payload that you need to send to /tokens to get an active API_TOKEN
    API_TOKEN_BODY = {"email": API_TOKEN_EMAIL, "is_activated": True}
    token = request_api("tokens", body=API_TOKEN_BODY, method="POST")

    # Only continue if API token created and response received
    try:
        token = dict(token)
        API_TOKEN = token["id"]
    except KeyError:
        print(f"An error occurred when trying to create an API token.")

    if API_TOKEN:
        print(f"Saving token to {API_TOKEN_FILENAME}")
        with open(API_TOKEN_FILENAME, "w") as f:
            f.write(API_TOKEN)


# CCDL DATASETS

# QUERYING CCDL DATASETS
# Each project has the potential to have up 7 different ccdl datasets associated with it,
# depending on the data contained within that project.
# The 7 possible datasets, reffered to by the attribute "ccdl_name", include:
#   ALL_METADATA: exclusively with project and sample level metadata
#   SINGLE_CELL_SINGLE_CELL_EXPERIMENT:
#       with all data matching the single cell modality and single cell experiemnt format,
#       including any multiplexed data associated with the project
#   SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED:
#       with all data matching the single cell modality and single cell experiemnt format,
#       but excluding the project's multiplexed data
#   SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED:
#       with all merged data matching the single cell modality and single cell experiemnt format
#   SINGLE_CELL_ANN_DATA:
#       with all data matching the single cell modality and anndata format,
#       (there is no multiplexed data associated with the anndata format)
#   SINGLE_CELL_ANN_DATA_MERGED:
#       with all merged data matching the single cell modality and anndata format
#   SPATIAL_SPATIAL_SPACERANGER:
#       with all data matching the spatial modality, generated with the spaceranger format,

# Possible query options for CCDL Datasets include:
#   id, ccdl_name, ccdl_project_id, ccdl_modality and format
# ccdl_modality options include: SINGLE_CELL and SPATIAL
# format options include: ANNDATA, SINGLE_CELL_EXPERIMENT, and METADATA
# NOTE: SPATIAL_SPACERANGER is not considered a dataset format.
# To fetch all SPATIAL CCDL Datasets data, use ccdl_modality attr to query all SPATIAL data

# For CCDL Project Datasets, the ccdl_prjoect_id__isnull attr must be set to False,
# For CCDL Portal Wide Datasets, it must be set to True
query = {
    "ccdl_modality": "SINGLE_CELL",
    "format": "SINGLE_CELL_EXPERIMENT",
    "ccdl_project_id__isnull": False,
}

queried_ccdl_datasets = request_api("ccdl-datasets", query=query).get("results", [])

print(f"Found {len(queried_ccdl_datasets)} projects for {query.items()}")

# DOWNLOADING CCDL DATASETS

# Grab the IDs
downloadable_ccdl_dataset_ids = [
    ccdl_dataset["id"]
    for ccdl_dataset in queried_ccdl_datasets
    if ccdl_dataset.get("computed_file")
]
print(f"Found {len(downloadable_ccdl_dataset_ids)} downloadable CCDL Datasets.")

# For example lets just download one file
download_id = downloadable_ccdl_dataset_ids[0]
print(
    f"For demonstration purposes, we will only download 1 CCDL Dataset (CCDL Dataset {download_id})."
)
ccdl_dataset = request_api("ccdl-datasets", download_id, token=API_TOKEN)

# Another request to actually download using pre-signed url
if download_url := ccdl_dataset.get("download_url"):
    print(f"Signed Download URL for CCDL Dataset {download_id}")
    print(download_url)
    print("---")

#   download_filename = ccdl_dataset["download_filename"]
#   print(f"Downloading: {download_filename}")
#   request.urlretrieve(download_url, download_filename)
#   print(f"Finished Downloading: {download_filename}")
