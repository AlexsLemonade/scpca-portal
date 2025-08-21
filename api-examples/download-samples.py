from urllib import request
import urllib.parse
import json
import os
from pprint import pp

# NOTE: UPDATE EMAIL OR SCRIPT WILL NOT WORK
# save an api key here and use it for subsequest calls
# this is where we will save the token for future calls
API_TOKEN_EMAIL = "user@example.com"  # NOTE: REPLACE THIS WITH A VALID EMAIL OR IT WILL ERROR OUT
API_TOKEN_FILENAME = ".token"
API_TOKEN = None

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
     - id: A string, int, or undefined: If specified will request that specific resource from the API.
     - query: A dict that represents the query parameters to tack onto the request. Will be url encoded.
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
        headers["api-key"] = token

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


# This is a helper method to do filtering locally.
# When the API supports datasets this wont be necessary.
def filter_resources(resources: list, filters: dict):
    """
    Generic filtering function.
    Takes a list of things from the API and a filter dict.
    The filter dict will remove any items from the list of resources
    that do not match on all key value pairs.
    Booleans must match exactly, so if you pass {A: True}
    then only the elements in `resources` where resource.A === True will be kept.
    Strings are lax, so if you pass {A: "substring"}
    then only the elemends in `resources` where resource.A = "example_substring" will not be omitted.
    """
    matches = []
    for r in resources:
        include = True
        for filter, value in filters.items():
            if filter not in r:
                raise KeyError(f"{filter} is not in {r.keys()}")
            if isinstance(r.get(filter), bool):
                if r.get(filter) is not value:
                    include = False
            elif value not in r.get(filter):
                include = False

        if include:
            matches.append(r)

    return matches



# API TOKEN

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

    token = dict(token)
    API_TOKEN = token.get("id")

    print(f"Saving token to {API_TOKEN_FILENAME}")
    with open(API_TOKEN_FILENAME, "w") as f:
        f.writelines(token)



# SAMPLES

# There are 704 samples. Loading everything is pretty trivial as a sigle request.
all_samples = request_api("samples").get("results", [])


# filter object to apply to samples response
# if you need to apply multiple values for a filter
# or other logic you will need to implement that as needed.
diagnoses_filter = {
    "diagnosis": "Ganglioglioma",
}

filtered_samples = filter_resources(all_samples, diagnoses_filter)

print(len(filtered_samples))

# COMPUTED FILES

# here we will collect computed files that we want to collect based on the samples
# Note: Each sample is associated with multiple computed_files
# so you will need to filter on modality again.
computed_files_of_interest = []

for sample in filtered_samples:
    for computed_file in sample["computed_files"]:
        # You need to filter for the types of downloads that you need.
        if (
            computed_file["modality"] == "SINGLE_CELL"
            and computed_file["format"] == "SINGLE_CELL_EXPERIMENT"
        ):
            computed_files_of_interest.append(computed_file)

# grab the IDs
computed_file_ids = [cf["id"] for cf in computed_files_of_interest]

print(f"Found {len(computed_files_of_interest)} Computed Files.")

# DOWNLOADING

# for example lets just download one file
print("For demonstation purposes only looping through 1 Computed File.")
download_ids = computed_file_ids[0:1]

print(f"Downloading {len(download_ids)} Computed File.")

for id in download_ids:
    # one request to get the download_url using the token
    computed_file = request_api("computed-files", id, token=API_TOKEN)
    # another request to actually download using pre-signed url
    if download_url := computed_file.get("download_url"):
        print(f"Signed Download URL for computed file {id}")
        print(download_url)
        print("---")

    # print(f"Downloading: {computed_file["s3_key"]}")
    # request.urlretrieve(download_url, computed_file["s3_key"])
    # print(f"Finished Downloading: {computed_file["s3_key"]}")
