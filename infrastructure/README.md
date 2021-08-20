# ScPCA Portal Infrstructure

The ScPCA Portal is configured to run in AWS.
You will need to have your AWS credentials configured or make them available as environment variables.

The configuration is written in [terraform](https://learn.hashicorp.com/terraform/getting-started/install.html).
You will need to have it installed to be able to deploy.

All commands from this README should be run from the `infrastructure/` directory.

## Deployment

The staging stack will be redeployed upon every merge to dev.
The production stack has not yet been configured.

A dev stack can be deployed from a local machine.
The deploy script will look for a private SSH key named `scpca-portal-key.pem` in the `infrastructure/` directory.
You will need to create an SSH key, name it that, and paste the public key for it into security.tf (replacing the existing one which is used for deploys to the cloud.

```
python3 deploy.py -d [dockerhub-repo] -e dev -u [username] -v v0.0.0
```

To make requests against the API that you deployed see the [READEME for the API](../api/README.md).

## Teardown

You can destroy an existing stack with:
```
python3 destroy_terraform.py -e dev -u [username]
```

The username you use to destroy should match the one you supplied to `deploy.py`.
