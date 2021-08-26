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


## Local Data Management

To populate your local database you can run:

```
sportal manage-api load_data
```

This will sync the `scpca-portal-inputs` bucket locally, read the metadata out of it, and load that into your local database.
To save time, by default it will not package up the actual data in that bucket and upload it to `scpca-local-data`.

If you would like to update the data in the `scpca-local-data` bucket, you can do so with the following command:

```
sportal manage-api load_data --upload True
```

By default the command also will only look for new projects.
If you would like to reimport all projects you can run

```
sportal manage-api load_data --reload-existing
```

or to reimport and upload all projects:

```
sportal manage-api load_data --reload-existing --upload True
```

If you would like to update a single project, you can do so by purging and then loading the data without reloading existing projects:

```
sportal manage-api purge_project --pi-name dyer_chen
sportal manage-api load_data
```

If you would like to purge a project and remove its files from the S3 bucket, you can use:

```
sportal manage-api purge_project --pi-name dyer_chen --delete-from-s3
```

## Cloud Data Management

The `load_data` and `purge_project` commands can also be run in the cloud.
The one difference is that in the cloud `load_data` defaults to uploading data.
This is to help prevent the S3 bucket data from accidentally becoming out of sync with the database.
It's not recommended but if you really want to just update the metadata without reuploading the data to S3 you can pass `--upload False`.

## Cloud Deployments

To deploy the API to AWS follow the directions for doing so in the [infrastructure README](../infrastructure/README.md).

Once you have completed a deploy you can replace with `0.0.0.0:8000` in the requests above with the `elastic_ip_address` output by terraform.
