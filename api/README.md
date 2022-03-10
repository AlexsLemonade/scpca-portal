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

A postgres commmand line client can be started by running:

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
sportal load-data --upload True
```

By default the command also will only look for new projects.
If you would like to reimport existing projects you can run

```
sportal load-data --reload-existing
```

or to reimport and upload projects that exist in the input data:

```
sportal load-data --reload-existing --upload True
```

or to reimport and upload all projects:

```
sportal load-data --reload-all --upload True
```

If you would like to update a single project, you can do so by purging and then loading the data without reloading existing projects:

```
sportal manage-api purge_project --scpca-id SCPCP000001
sportal load-data
```

If you would like to purge a project and remove its files from the S3 bucket, you can use:

```
sportal manage-api purge_project --scpca-id SCPCP000001 --delete-from-s3
```

## Cloud Data Management

The `load_data` and `purge_project` commands can also be run in the cloud.
The one difference is that in the cloud `load_data` defaults to uploading data.
This is to help prevent the S3 bucket data from accidentally becoming out of sync with the database.
It's not recommended but if you really want to just update the metadata without reuploading the data to S3 you can pass `--upload False`.

To run the `load_data` command in production, there is a load_data.sh script that is created on the API instance.
It passes any arguments to it through to the command, so `./load_data.sh --reload-all` will work nicely.

The `purge_project` command does not have it's own script.
Ideally it should only be run via the `load_data` command using the `--reload-existing` and `--reload-all` options, but if it ever needs to be run on it's own then `docker exec -it scpca_portal_api python3 manage.py purge_project --scpca-id SCPCP000001` will still work.
The `load_data` command necessitated it's own script because it does need to be run enough and also it can take a while to load all the data so doing so without a TTY is preferable.

## Cloud Deployments

To deploy the API to AWS follow the directions for doing so in the [infrastructure README](../infrastructure/README.md).

Once you have completed a deploy you can replace with `0.0.0.0:8000` in the requests above with the `elastic_ip_address` output by terraform.
