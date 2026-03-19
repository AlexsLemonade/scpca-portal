import json
import os
import urllib.parse
from pprint import pp
from urllib import request

# SCRIPT CONSTANTS
# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
# By adding your email, you agree to the terms of service and privacy policy:
# - Terms of Service: https://scpca.alexslemonade.org/terms-of-use
# - Privacy Policy: https://scpca.alexslemonade.org/privacy-policy
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT

# by default, we only attempt to work with one downloadable file
# set this to True if you would like to loop over all downloadable files
LOOP_OVER_ALL_DOWNLOADS = False

# by default, we only print the signed download URL
# set this to True if you would like to initiate the download
INITIATE_DOWNLOAD = False

# this is where we will save the token for future calls
API_TOKEN_FILENAME = ".token"

if not API_TOKEN_EMAIL or "example" in API_TOKEN_EMAIL:
    raise Exception("Please accept terms by adding a valid email for API_TOKEN_EMAIL")

# This is all boiler plate to make it easier to make api calls
# API_RESOURCES is pulled from the list shown on https://api.scpca.alexslemonade.org/v1/
API_BASE = "https://api.scpca.alexslemonade.org/v1/"
API_RESOURCES = ["computed-files", "projects", "samples", "tokens", "project-options"]
API_ENDPOINTS = {resource: f"{API_BASE}{resource}/" for resource in API_RESOURCES}

BASE_HEADERS = {"Accept": "application/json"}
BASE_PARAMS = {"limit": 2000}  # lets ignore pagination for now


# Generic API Request method for tokens, samples, projects etc
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


# API TOKEN

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


# PROJECTS
query = {"diagnoses": "Ganglioglioma"}

queried_projects = request_api("projects", query=query).get("results", [])

print(f"Found {len(queried_projects)} projects for query:")
pp(query)

# COMPUTED FILES

# here we will collect computed files that we want to collect based on the samples
# Note: Each sample is associated with multiple computed_files
# so you will need to filter on modality again.
computed_files_of_interest = []

for project in queried_projects:
    for computed_file in project["computed_files"]:
        # You need to filter for the types of downloads that you need.
        if (
            computed_file["modality"] == "SINGLE_CELL"
            and computed_file["format"] == "SINGLE_CELL_EXPERIMENT"
            and computed_file.get("includes_merged")
            and not computed_file.get("metadata_only")
        ):
            computed_files_of_interest.append(computed_file)
# grab the IDs
computed_file_ids = [cf["id"] for cf in computed_files_of_interest]

print(f"Found {len(computed_files_of_interest)} project computed-files.")

# DOWNLOADING
download_ids = computed_file_ids if LOOP_OVER_ALL_DOWNLOADS else computed_file_ids[0:1]
for id in download_ids:
    computed_file = request_api("computed-files", id, token=API_TOKEN)

    # Another request to actually download using pre-signed url
    if download_url := computed_file.get("download_url"):
        print(f"Signed Download URL for computed file {id}")
        print(download_url)
        print("---")

        if INITIATE_DOWNLOAD:
            print(f"Downloading: {computed_file['s3_key']}")
            request.urlretrieve(download_url, computed_file["s3_key"])
            print(f"Finished Downloading: {computed_file['s3_key']}")
        else:
            print("Skipping downloading.")
