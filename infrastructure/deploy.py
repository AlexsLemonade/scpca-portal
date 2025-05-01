"""This script deploys the cloud infrastructure for the ScPCA project."""

import argparse
import os
import subprocess
import time

from deploy_modules import docker, terraform

NEW_ENVS = ["dev"]
PRIVATE_KEY_FILE_PATH = "scpca-portal-key.pem"

DEV_SECRETS_FILE = "api-configuration/dev-secrets"
TAINT_ON_APPLY = ["aws_instance.api_server_1"]

# These environment variables are passed to terraform
# via parse_args args attribute.
TF_ARG_VAR = {
    "user": "TF_VAR_user",
    "env": "TF_VAR_stage",
    "region": "TF_VAR_region",
    "dockerhub_account": "TF_VAR_dockerhub_account",
    "system_version": "TF_VAR_system_version",
}

# These environment variables are injected based on the envar name.
# This may be overriden by contents of DEV_SECRETS_FILE
TF_ENV_VAR = {
    "DATABASE_PASSWORD": "TF_VAR_database_password",
    "DJANGO_SECRET_KEY": "TF_VAR_django_secret_key",
    "SENTRY_DSN": "TF_VAR_sentry_dsn",
    "SENTRY_ENV": "TF_VAR_sentry_env",
    "SSH_PUBLIC_KEY": "TF_VAR_ssh_public_key",
    "SLACK_CCDL_TEST_CHANNEL_EMAIL": "TF_VAR_slack_ccdl_test_channel_email",
}


def parse_args():
    description = """This script can be used to deploy and update a
    `scpca portal` instance stack. It will create all of the AWS infrastructure
    (roles/instances/db/network/etc), open an ingress, perform a database
    migration, and close the ingress. This can be run from a CI/CD machine or
    a local dev box. This script must be run from /infrastructure!"""
    parser = argparse.ArgumentParser(description=description)

    env_help_text = """Specify the environment you would like to deploy to.
    Not optional. Valid values are: prod, staging, and dev `prod` and `staging`
    will deploy the production stack. These should only be used from a
    deployment machine. `dev` will deploy a dev stack which is appropriate
    for a single developer to use to test."""
    parser.add_argument(
        "-e",
        "--env",
        help=env_help_text,
        required=True,
        choices=["dev", "staging", "prod"],
    )

    user_help_text = (
        "Specify the username of the deployer. "
        "Should be the developer's name in development stacks."
    )
    parser.add_argument("-u", "--user", help=user_help_text, required=True)

    dockerhub_help_text = (
        "Specify the dockerhub account from which to pull the docker image."
        " Can be useful for using your own dockerhub account for a development stack."
    )
    parser.add_argument(
        "-d",
        "--dockerhub-account",
        help=dockerhub_help_text,
        required=True,
    )

    version_help_text = "Specify the version of the system that is being deployed."
    parser.add_argument("-v", "--system-version", help=version_help_text, required=True)

    region_help_text = (
        "Specify the AWS region to deploy the stack to. Default is us-east-1."
    )
    parser.add_argument("-r", "--region", help=region_help_text, default="us-east-1")
    return parser.parse_args()


def get_env(script_args: dict):
    """Load environment specific variables.

    For dev environment, just use the variables contained in
    api-configuration/dev-secrets.
    """
    env = os.environ.copy()

    # Copy envar to TF_VAR envar
    for envar, tfvar in TF_ENV_VAR.items():
        print(f"{envar} to {tfvar} with {env[envar]}")
        env[tfvar] = env[envar].strip()

    # Assign arg to TF_VAR envar
    for arg, tfvar in TF_ARG_VAR.items():
        print(f"{arg} to {tfvar} with {script_args[arg]}")
        env[tfvar] = script_args[arg].strip()

    return env


def run_remote_command(ip_address, command):
    completed_command = subprocess.check_output(
        [
            "ssh",
            "-i",
            PRIVATE_KEY_FILE_PATH,
            "-o",
            "StrictHostKeyChecking=no",
            f"ubuntu@{ip_address}",
            command,
        ],
    )

    return completed_command


def restart_api_if_still_running(args, api_ip_address):
    try:
        if not run_remote_command(api_ip_address, "docker ps -q -a"):
            print(
                "Seems like the API came up, but has no docker containers "
                "so it will start them itself."
            )
            return 0
    except subprocess.CalledProcessError:
        print("Seems like the API isn't up yet, which means it got cycled.")
        return 0

    print("The API is still up! Restarting!")
    run_remote_command(
        api_ip_address, "docker rm -f $(docker ps -a -q) 2>/dev/null || true"
    )

    print("Waiting for API container to stop.")
    time.sleep(30)

    # Handle the small edge case where we're able to ssh onto the API
    # but it hasn't finished it's init script. If this happens we're
    # successful because the init script will run this script for us.
    try:
        run_remote_command(api_ip_address, "test -e start_api_with_migrations.sh")
    except subprocess.CalledProcessError:
        print(
            "API start script not written yet, letting the init script run it instead."
        )
        return 0

    try:
        run_remote_command(api_ip_address, "sudo bash start_api_with_migrations.sh")
    except subprocess.CalledProcessError:
        return 1

    return 0


def post_deploy_hook():
    api_ip_key = "api_server_1_ip"
    api_ip_address = terraform_output.get(api_ip_key, {}).get("value", None)

    if not api_ip_address:
        print(
            "Could not find the API's IP address. Something has gone wrong or changed."
        )
        print(f"{api_ip_key} not defined in outputs")
        exit(1)

    # Create a key file from env var
    with open(PRIVATE_KEY_FILE_PATH, "w") as private_key_file:
        private_key_file.write(os.environ["SSH_PRIVATE_KEY"])

    os.chmod(PRIVATE_KEY_FILE_PATH, 0o600)

    # This is the last command, so the script's return code should
    # match it.
    return restart_api_if_still_running(args, api_ip_address)


# This is the deploy process.
if __name__ == "__main__":
    args = parse_args()
    # get environ to inject into terraform commands
    environ = get_env(vars(args))

    docker_code = docker.build_and_push_docker_image(
        f"{args.dockerhub_account}/scpca_portal_api",
        f"--build-arg SYSTEM_VERSION={args.system_version}",
        "--build-arg HTTP_PORT=8081",
    )

    if docker_code != 0:
        exit(docker_code)

    configs = [
        f"bucket=scpca-portal-tfstate-{args.env}",
        f"key=terraform-{args.user}.tfstate",
        "dynamodb_table=scpca-portal-terraform-lock",
    ]

    # OVERRIDES

    if args.env in NEW_ENVS:
        configs = [
            "bucket=scpca-portal-terraform-backend",
            f"key={args.user}-{args.env}.tfstate",
            "use_lockfile=true",
        ]

    init_code = terraform.init(configs)

    if init_code != 0:
        exit(init_code)

    terraform_code, terraform_output = terraform.apply(
        f"-var-file=tf_vars/{args.env}.tfvars", environ=environ, taints=TAINT_ON_APPLY
    )

    if terraform_code != 0:
        exit(terraform_code)

    return_code = post_deploy_hook()

    if return_code == 0:
        print("\nDeploy completed successfully!!")

    exit(return_code)
