# ScPCA Portal Infrstructure

The ScPCA Portal is configured to run in AWS.
You will need to have your AWS credentials configured or make them available as environment variables.

The configuration is written in [terraform](https://learn.hashicorp.com/terraform/getting-started/install.html).
You will need to have it installed to be able to deploy.

All commands from this README should be run from the `infrastructure/` directory.

## Deployment

The staging stack will be redeployed upon every merge to dev.
The production stack will be redeployed upon every merge to main.

A dev stack can be deployed from a local machine.
The deploy script will look for an SSH key pair in the `infrastructure/` directory.
The private key should be named `scpca-portal-key.pem`, and the public key should be named `scpca-portal-key.pub`.

```
python3 deploy.py -d [dockerhub-account] -e dev -u [username] -v v0.0.0
```

To make requests against the API that you deployed see the [README for the API](../api/README.md).

## Teardown

You can destroy an existing stack with:
```
python3 destroy_terraform.py -e dev -u [username]
```

The username you use to destroy should match the one you supplied to `deploy.py`.
