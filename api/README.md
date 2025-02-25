# ScPCA Portal API

All commands from this README should be run from the project's root directory.

## Local Development

Start the dev server for local development:

```bash
sportal up
```

Run a command inside the docker container:

```bash
sportal run-api [command]
```

Or run the tests:

```
sportal test-api
```

Note that the tests are run with the Django unittest runner, so specific modules, classes, or methods may be specified in the standard unittest manner: https://docs.python.org/3/library/unittest.html#unittest-test-discovery.
For example:

```
sportal test-api scpca_portal.test.serializers.test_project.TestProjectSerializer
```

will run all the tests in the TestProjectSerializer class.

See

```
sportal -h
```

For more commands.

The dev server runs by default on port 8000 with the docs being served at 8001.
If these ports are already in use on your local machine, you can run them at different ports with:

```bash
HTTP_PORT=8002 DOCS_PORT=8003 sportal up
```

A postgres command line client can be started by running:

```
sportal postgres-cli
```

## Example Local Requests

You can use this to make a curl request to the API like so:

```
curl http://0.0.0.0:8000/v1/projects/
```

Computed files won't provide a `download_url` unless an API token is provided.
To get and activate an API token, make a request similar to:

```
curl http://0.0.0.0:8000/v1/tokens/ -X POST -d '{"is_activated": true}' -H "Content-Type: application/json"
```

Which should return something like

```
{
    "id": "30e429fd-ded5-4c7d-84a7-84c702f596c1",
    "is_activated": true,
    "terms_and_conditions": "PLACEHOLDER"
}
```

This `id` can then be provided as the value for the `API-KEY` header in a request to the `/v1/computed-files/` endpoint like so:

```
curl http://0.0.0.0:8000/v1/computed-files/1/ -H 'API-KEY: 658f859a-b9d0-4b44-be3d-dad9db57164a'
```

`download_url` can only be retrieved for ComputedFiles one at a time.

## Local Data Management

To populate your local database you can run:

```
sportal load-data
```

This will sync the `scpca-portal-inputs` bucket locally, read the metadata out of it, and load that into your local database.
To save time, by default it will not package up the actual data in that bucket and upload it to `scpca-local-data`.

If you would like to update the data in the `scpca-local-data` bucket, you can do so with the following command:

```
sportal load-data --update-s3
```

By default the command also will only look for new projects.
If you would like to reimport existing projects you can run

```
sportal load-data --reload-existing
```

or to reimport and upload projects that exist in the input data:

```
sportal load-data --reload-existing --update-s3
```

or to reimport and upload all projects:

```
sportal load-data --reload-all --update-s3
```

If you would like to update a specific project use --scpca-project-id flag:

```
sportal load-data --scpca-project-id SCPCP000001 --scpca-project-id SCPCP000002
```

For a specific sample update use --scpca-sample-id flag:

```
sportal load-data --scpca-project-id SCPCP000001 --scpca-sample-id SCPCS000001
```

If you don't want the data to be re-synced from the input bucket use --skip-sync flag:

```
sportal load-data --scpca-project-id SCPCP000001 --skip-sync
```

If you would like to purge a project and remove its files from the S3 bucket, you can use:

```
sportal manage-api purge_project --scpca-project-id SCPCP000001 --delete-from-s3
```

The `--clean-up-input-data` flag can help you control the projects input data size. If flag is set the
input data cleanup process will be run for each project right after its processing is over.
```
sportal load-data --clean-up-input-data --reload-all --update-s3
```

The `--clean-up-output-data` flag can help you control the projects output data size. If flag is set the
output (no longer needed) data cleanup process will be run for each project right after its processing is over.
```
sportal load-data --clean-up-output-data --reload-all --update-s3
```

The `--max-workers` flag can be used for setting a number of simultaneously processed projects/samples
to speed up the data loading process. The provided number will be used to spawn threads within two
separate thread pool executors -- for project and sample processing.
```
sportal load-data --max-workers 10 --reload-all --update-s3
```

AWS S3 configuration options:

The `--s3-max-bandwidth` flag controls the maximum bandwidth (in MB/s) that the S3 commands will
utilize for S3 transfers. Default - None.
```
sportal load-data --max-workers 10 --reload-all --update-s3 --s3-max-bandwidth 100
```

The `--s3-max-concurrent-requests` specifies the maximum number of downloads/uploads that are
allowed at any given time. Default - 10.
```
sportal load-data --max-workers 10 --reload-all --update-s3 --s3-max-concurrent-requests 20
```

The `--s3-multipart-chunk-size` specifies the chunk size (in MB) for multipart operations.
Default - 8MB.
```
sportal load-data --max-workers 10 --reload-all --update-s3 --s3-multipart-chunk-size 64
```


## Cloud Data Management

### Processing Options
There are two options available for processing data in the Cloud:
- Running `load_data` on the API instance (or a combination of `load_metadata` and `generate_computed_files`)
- Running `dispatch_to_batch` on the API instance, which kicks off processing on AWS Batch resources

Due to the fact that processing on Batch is ~10x faster than processing on the API, we recommend using Batch for processing.

### Commands in Production
To run a command in production, there is a `run_command.sh` script that is created on the API instance. It passes any arguments through to the `manage.py` script, making the following acceptable `./run_command.sh load_data --reload-all`.

### Processing on the API
The following code can be used to process projects on the API, one by one, with a minimum disk space footprint:

```bash
for i in $(seq -f "%02g" 1 20); do
    ./run_command.sh load_data --clean-up-input-data --clean-up-output-data --reload-existing --scpca-project-id SCPCP0000$i
done
```

Alternatively, for a more granular approach, first run `load_metadata`, and thereafter `generate_computed_files`, as follows:

```bash
for i in $(seq -f "%02g" 1 20); do
    ./run_command.sh load_metadata --clean-up-input-data --reload-existing --scpca-project-id SCPCP0000$i
done

for i in $(seq -f "%02g" 1 20); do
    ./run_command.sh generate_computed_files --clean-up-input-data --clean-up-output-data --scpca-project-id SCPCP0000$i
done

```

One note about running `load_data` in production is that it defaults to uploading completed computed files to S3. This is to help prevent the S3 bucket data from accidentally becoming out of sync with the database.

### Processing via Batch
The following code is used for processing projects via AWS Batch:
```bash
./run_command.sh dispatch_to_batch
```

By default the `dispatch_to_batch` command will look at all projects and filter out all projects that already have at least 1 computed file. AWS Batch jobs will be dispatched and create valid computed files for matching projects that were not filtered out.

You can override this filter by passing the `--regenerate-all` flag. This will dispatch jobs independent of existing computed files. Any existing computed files will be purged before new ones are generated to replace them.

You can limit the scope of this command to only apply to a specific project by passing the `--project-id <SCPCP999999>` flag. This can be used in conjunction with `--regenerate-all` if you want to ignore existing computed files for that project.

### Purge project
To purge a project from the database (and from S3 if so desired), run the following command:
```bash
./run_command.sh purge_project --scpca-id SCPCP000001 --delete-from-s3
```
## Cloud Deployments

To deploy the API to AWS follow the directions for doing so in the [infrastructure README](../infrastructure/README.md).

Once you have completed a deploy you can replace with `0.0.0.0:8000` in the requests above with the `elastic_ip_address` output by terraform.
