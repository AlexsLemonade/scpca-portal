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

i.e. the tests:

```
sportal test-api
```

Note that the tests are run with the Django unittest runner, so specific modules, classes, or methods may be specified in the standard unittest manner: https://docs.python.org/3/library/unittest.html#unittest-test-discovery.
For example:
```
sportal test-api scpca_portal.test.serializers.test_project.TestProjectSerializer
```

will run all the tests in the TestProjectSerializer class.

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

## Cloud Deployments

To deploy the API to AWS follow the directions for doing so in the [infrastructure README](../infrastructure/README.md).

Once you have completed a deploy you can replace with `0.0.0.0:8000` in the requests above with the `elastic_ip_address` output by terraform.
