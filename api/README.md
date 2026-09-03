# ScPCA Portal API

All commands from this README should be run from the project's root directory.

## Local Development

Start the dev server for local development:

```bash
sportal docker:compose up
```

Run a command inside the docker container:

```bash
sportal api:run [command]
```

Or run the tests:

```
sportal api:test
```

Note that the tests are run with the Django unittest runner, so specific modules, classes, or methods may be specified in the standard unittest manner: https://docs.python.org/3/library/unittest.html#unittest-test-discovery.

For example, to run all the tests in the TestProjectSerializer class:

```
sportal api:test scpca_portal.test.serializers.test_project.TestProjectSerializer
```

For more commands, see:

```
sportal -h
```

The dev server runs by default on port 8000 with the docs being served at 8001.
If these ports are already in use on your local machine, you can run them at different ports with:

```bash
HTTP_PORT=8002 DOCS_PORT=8003 sportal docker:compose up
```

A postgres command line client can be started by running:

```
sportal postgres:cli
```

## Example Local Requests

You can use this to make a curl request to the API like so:

```
curl http://0.0.0.0:8000/v1/projects/
```

To get and activate an API token, make a request similar to:

```
curl http://0.0.0.0:8000/v1/tokens/ -X POST -d '{"is_activated": true}' -H "Content-Type: application/json"
```

Which should return something like:

```
{
    "id": "30e429fd-ded5-4c7d-84a7-84c702f596c1",
    "is_activated": true,
    "terms_and_conditions": "PLACEHOLDER"
}
```

For end-to-end example scripts that demonstrate querying, authenticating, and downloading data, see [`api-examples/`](../api-examples/).


## Local Data Management

> [!NOTE]
> **AWS SSO required.** Commands that access AWS resources (S3, Batch) must be run with an SSO profile:
> ```bash
> sportal --sso <profile> api:manage <command>
> ```
> Without `--sso`, `sportal` proceeds without credentials and AWS calls will fail.

### Syncing the OriginalFile Table
Before data can be processed, the `OriginalFile` table must be populated and synced via the `sync-original-files` command. This command builds a local representation of all objects available in the default (or passed) s3 input bucket, and is considered the single source of truth for input files throughout the codebase.

Syncing is carried out as follows:
```bash
sportal api:manage sync_original_files
```

By default the `sync_original_files` command uses the default bucket defined in the config file associated with the environment calling the command. This can be overriden by passing the `--bucket bucket-name` flag to sync the files of an alternative bucket.

In the rare case where all files have been deleted from the requested bucket, the `--allow-bucket-wipe` flag must be explicitly passed in order for all bucket files in the OriginalFile table to be wiped.


### The Pipeline and its Workflows
There are two independent workflows carried out within the data processing pipeline:
1. Loading metadata and populating the database
2. Creating CCDL datasets and populating S3

To run the load metadata workflow, call:
```
sportal api:manage load_metadata
```
To run the create CCDL datasets workflow, call:
```
sportal api:manage create_ccdl_datasets
```

### Load Metadata Configuration Options
Calling `sportal api:manage load_metadata` will populate your local database by pulling metadata from the `scpca-portal-input` bucket.

By default the command will only look for new projects.
If you would like to reimport existing projects you can run:

```
sportal api:manage load_metadata --reload-existing
```

If during the last run of `load_metadata` there were projects in the lockfile that are no longer being worked on, those projects can be reloaded by running:

```
sportal api:manage load_metadata --reload-locked
```

If you would like to update a specific project, use the `--scpca-project-id` flag:

```
sportal api:manage load_metadata --scpca-project-id SCPCP000001
```

The default input bucket for local development is `scpca-portal-input`. To pass a custom input bucket the `--input-bucket-name` flag can be passed, as illustrated below:

```
sportal api:manage load_metadata --input-bucket-name custom-input-bucket
```

The `--clean-up-input-data` flag can help you control the projects input data size. If the flag is set, the input data cleanup process will be run for each project right after its processing is over.
```
sportal api:manage load_metadata --clean-up-input-data
```

If you would like to purge a project from the db and remove its files from the S3 output bucket, the `purge_project` command should be used, as follows:

```
sportal api:manage purge_project --scpca-project-id SCPCP000001
```

### Create CCDL Datasets Configuration Options
> [!NOTE]
> **Local limitation.** Running `create_ccdl_datasets` against the local Docker environment only inserts database records with `computed_file=null`. It does not submit Batch jobs or populate S3. Full end-to-end execution requires the `dev` server on cloud, which also requires an SSO profile.

Calling `sportal api:manage create_ccdl_datasets` will create all CCDL datasets and dispatch them as jobs to AWS Batch.

By default the `create_ccdl_datasets` command only processes datasets that are new or whose hash has changed. To force reprocessing of all datasets regardless of hash:

```
sportal api:manage create_ccdl_datasets --ignore-hash
```

By default, failed jobs are queued for retry. To disable automatic retry queueing:

```
sportal api:manage create_ccdl_datasets --no-retry-failed-jobs
```

### Creating User Datasets
> [!NOTE]
> **Local limitation.** Against the local Docker environment, Batch submission is skipped. The user dataset record is created without populating the computed file to S3. Full end-to-end processing requires the `dev` server on cloud.

User datasets are customizable collections of samples created on demand via the API.

To create a dataset, POST to `/v1/datasets/`:

```
curl http://0.0.0.0:8000/v1/datasets/ \
  -X POST \
  -H "Content-Type: application/json" \
  -H "API-KEY: <token-id>" \
  -d '{"format": "SINGLE_CELL_EXPERIMENT", "data": {...}, "email": "user@example.com", "start": true}'
```

Include `email` and an `API-KEY` header to start dataset processing with `"start": true`:

```
curl http://0.0.0.0:8000/v1/datasets/<dataset-id>/ \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "API-KEY: <token-id>" \
  -d '{"start": true}'
```

For end-to-end example scripts that demonstrate querying projects, authenticating, and downloading user datasets, see:
- Bash: [`dataset-download-with-merged-objects.sh`](../api-examples/dataset-download-with-merged-objects.sh), [`dataset-download-with-samples-by-diagnosis.sh`](../api-examples/dataset-download-with-samples-by-diagnosis.sh)
- Python: [`dataset-download-with-merged-objects.py`](../api-examples/dataset-download-with-merged-objects.py), [`dataset-download-with-samples-by-diagnosis.py`](../api-examples/dataset-download-with-samples-by-diagnosis.py)


## Cloud Data Management

### Processing Options
After syncing the database by running the `sync_original_files` and `load_metadata` commands, CCDL datasets are created and dispatched to AWS Batch via the `create_ccdl_datasets` command.

### Commands in Production
To run a command in production, there is a `run_command.sh` script that is created on the API instance. It passes any arguments through to the `manage.py` script, making the following acceptable: `./run_command.sh create_ccdl_datasets`.

### Syncing the OriginalFile Table
As mentioned in the above [Local Data Management - Syncing the OriginalFile Table section](#syncing-the-originalfile-table), the `OriginalFile` table must be populated before data can be processed via the `sync_original_files` command.

Syncing is carried out as follows:
```bash
./run_command.sh sync_original_files
```

Details of the `sync_original_files` can be found in the Syncing the OriginalFile table header in the Local Data Management section above.

### Processing via Batch

#### CCDL Datasets

CCDL datasets are pre-configured datasets managed by the CCDL (see [Local Data Management - Create CCDL Datasets Configuration Options](#create-ccdl-datasets-configuration-options)).

To create all CCDL datasets and dispatch them to AWS Batch:

```bash
./run_command.sh create_ccdl_datasets
```

Details of the `sync_original_files` can be found in the Create CCDL Datasets Configuration Options header in the Local Data Management section above.

#### User Datasets

User datasets are created via the `/v1/datasets/` API endpoint (see [Local Data Management - Creating User Datasets](#creating-user-datasets)).

Details of the `sync_original_files` can be found in the Syncing the Creating User Datasets header in the Local Data Management section above.

### Purge Project
To purge a project from the database (and from S3 if so desired), run the following command:
```bash
./run_command.sh purge_project --scpca-id SCPCP000001 --delete-from-s3
```
## Cloud Deployments

To deploy the API to AWS follow the directions for doing so in the [infrastructure README](../infrastructure/README.md).

Once you have completed a deploy you can replace with `0.0.0.0:8000` in the requests above with the `elastic_ip_address` output by terraform.
