"""This script deploys the cloud infrastructure for the ScPCA project."""

import argparse
import os
import subprocess
import time

from deploy_modules import docker, terraform

# CONFIGS
PRIVATE_KEY_FILE_PATH = "scpca-portal-key.pem"
# TODO: Convert to argument
TAINT_ON_APPLY = ["aws_instance.api_server_1"]

# These environment variables are passed to terraform
# via parse_args args attribute.
TF_ARG_VAR = {
    "user": "TF_VAR_user",
    "stage": "TF_VAR_stage",
    "region": "TF_VAR_region",
    "dockerhub_account": "TF_VAR_dockerhub_account",
    "system_version": "TF_VAR_system_version",
}

# These environment variables are injected based on the envar name.
TF_ENV_VAR = {
    "DATABASE_PASSWORD": "TF_VAR_database_password",
    "DJANGO_SECRET_KEY": "TF_VAR_django_secret_key",
    "SENTRY_DSN": "TF_VAR_sentry_dsn",
    "SENTRY_ENV": "TF_VAR_sentry_env",
    "SSH_PUBLIC_KEY": "TF_VAR_ssh_public_key",
    "SLACK_CCDL_TEST_CHANNEL_EMAIL": "TF_VAR_slack_ccdl_test_channel_email",
    "ENABLE_FEATURE_PREVIEW": "TF_VAR_enable_feature_preview",
    "CELLBROWSER_SECURITY_TOKEN": "TF_VAR_cellbrowser_security_token",
    "CELLBROWSER_UPLOADERS": "TF_VAR_cellbrowser_uploaders",
}


def parse_args():
    description = """This script can be used to deploy and update a
    `scpca portal` instance stack. It will create all of the AWS infrastructure
    (roles/instances/db/network/etc), open an ingress, perform a database
    migration, and close the ingress. This can be run from a CI/CD machine or
    a local dev box. This script must be run from /infrastructure!"""
    parser = argparse.ArgumentParser(description=description)

    # STAGE
    env_help_text = """Specify the stage you would like to deploy to.
    Not optional. Valid values are: prod, staging, and dev `prod` and `staging`
    will deploy the production stack. These should only be used from a
    deployment machine. `dev` will deploy a dev stack which is appropriate
    for a single developer to use to test."""
    parser.add_argument(
        "-s",
        "--stage",
        help=env_help_text,
        required=True,
        choices=["dev", "staging", "prod"],
    )

    # USER
    user_help_text = (
        "Specify the username of the deployer. "
        "Should be the developer's name in development stacks."
    )
    parser.add_argument("-u", "--user", help=user_help_text, required=True)

    # DOCKER ACCOUNT
    dockerhub_help_text = (
        "Specify the dockerhub account from which to pull the docker image."
        " Can be useful for using your own dockerhub account for a development stack."
    )
    parser.add_argument(
        "-a",
        "--dockerhub-account",
        help=dockerhub_help_text,
        required=True,
    )

    # VERSION INFO
    version_help_text = "Specify the version of the system that is being deployed."
    parser.add_argument("-v", "--system-version", help=version_help_text, required=True)

    # REGION
    region_help_text = "Specify the AWS region to deploy the stack to. Default is us-east-1."
    parser.add_argument("-r", "--region", help=region_help_text, default="us-east-1")

    # DESTROY
    destroy_help_text = "Specify that you want to destroy existing stack."
    parser.add_argument("--destroy", help=destroy_help_text, action=argparse.BooleanOptionalAction)

    # INIT
    destroy_help_text = "Run terraform init. Skips docker builds."
    parser.add_argument("--init", help=destroy_help_text, action=argparse.BooleanOptionalAction)

    # PLAN
    plan_help_text = "Run terraform plan. Skips docker builds."
    parser.add_argument("--plan", help=plan_help_text, action=argparse.BooleanOptionalAction)

    # SAVE PLAN
    save_out_help_text = "Used with --plan. Saves output for next deploy."
    parser.add_argument(
        "--save-plan", help=save_out_help_text, action=argparse.BooleanOptionalAction
    )

    # CONSOLE
    console_help_text = "Run terraform console. Skips docker builds."
    parser.add_argument("--console", help=console_help_text, action=argparse.BooleanOptionalAction)

    # SKIP DOCKER
    skip_docker_text = "Specify that you want to skip building docker container."
    parser.add_argument(
        "--skip-docker", help=skip_docker_text, action=argparse.BooleanOptionalAction
    )

    # TEMP
    # PROJECT ACCOUNT
    project_help_text = "Specify that you want to deploy with new settings."
    parser.add_argument("--project", help=project_help_text, action=argparse.BooleanOptionalAction)

    return parser.parse_args()


def get_env(script_args: dict):
    """Load environment specific variables."""
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


def create_ssh_private_key_file():
    # Create a key file from env var
    with open(PRIVATE_KEY_FILE_PATH, "w") as private_key_file:
        private_key_file.write(os.environ["SSH_PRIVATE_KEY"])

    os.chmod(PRIVATE_KEY_FILE_PATH, 0o600)


def run_remote_command(ip_address, command):
    if not os.path.exists(PRIVATE_KEY_FILE_PATH):
        create_ssh_private_key_file()

    print(f"Remote Command on {ip_address}: '{command}'")
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


def get_api_ip_address_from_output(terraform_output: dict):
    api_ip_key = "api_server_1_ip"
    api_ip_address = terraform_output.get(api_ip_key, {}).get("value", None)

    if not api_ip_address:
        print(f"Could not find the API's IP address. {api_ip_key} is not defined in outputs.")

    return api_ip_address


def pre_deploy_hook(terraform_output: dict):
    """Terminates all processing jobs and queues them for submission upon API re-cycling."""
    api_ip_address = get_api_ip_address_from_output(terraform_output)
    if not api_ip_address:
        return 0

    # Stop cron now so no new batch jobs are submitted after processing is paused
    try:
        run_remote_command(api_ip_address, "sudo systemctl stop cron")
    except subprocess.CalledProcessError:
        print("There was an error disabling the cron service.")
        return 1

    try:
        run_remote_command(api_ip_address, "sudo ./run_command.sh pause_processing")
    except subprocess.CalledProcessError:
        print("There was an error terminating currently processing jobs.")
        return 1

    print("Processing jobs requeued successfully.")
    return 0


def post_deploy_hook(terraform_output: dict):
    """Restarts the API if it's still running."""
    api_ip_address = get_api_ip_address_from_output(terraform_output)
    if not api_ip_address:
        return 0

    try:
        if not run_remote_command(api_ip_address, "sudo docker ps -q -a"):
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
        api_ip_address, "sudo docker rm -f $(sudo docker ps -a -q) 2>/dev/null || true"
    )

    print("Waiting for API container to stop.")
    time.sleep(30)

    # Handle the small edge case where we're able to ssh onto the API
    # but it hasn't finished it's init script. If this happens we're
    # successful because the init script will run this script for us.
    try:
        run_remote_command(api_ip_address, "test -e start_api_with_migrations.sh")
    except subprocess.CalledProcessError:
        print("API start script not written yet, letting the init script run it instead.")
        return 0

    try:
        run_remote_command(api_ip_address, "sudo bash start_api_with_migrations.sh")
    except subprocess.CalledProcessError:
        return 1

    # Explicitly start the cron service to handle the case where the same API,
    # which had its cron service stopped during the pre deploy hook, is still running here
    try:
        run_remote_command(api_ip_address, "sudo systemctl start cron")
    except subprocess.CalledProcessError:
        print("There was an error starting the cron service.")
        return 1

    return 0


# This is the deploy process.
if __name__ == "__main__":
    args = parse_args()

    # get environ to inject into terraform commands
    env = get_env(vars(args))

    skip_docker = any([args.skip_docker, args.destroy, args.init, args.plan, args.console])

    if not skip_docker:
        docker_code = docker.build_and_push_docker_image(
            f"{args.dockerhub_account}/scpca_portal_api",
            f"--build-arg SYSTEM_VERSION={args.system_version}",
            "--build-arg HTTP_PORT=8081",
        )

        if docker_code != 0:
            exit(docker_code)

    # OLD LOCK FILE
    backend_configs = [
        f"bucket=scpca-portal-tfstate-{args.stage}",
        f"key=terraform-{args.user}.tfstate",
        "use_lockfile=true",
    ]

    # NEW LOCK FILE
    if args.project:
        backend_configs = [
            "bucket=scpca-portal-terraform-backend",
            f"key={args.user}-{args.stage}.tfstate",
            "use_lockfile=true",
        ]

    # Always init first
    init_code = terraform.init(backend_configs, env=env)

    if init_code != 0 or args.init:
        exit(init_code)

    # Only call pre_deploy_hook on a running stack
    return_code = pre_deploy_hook(terraform.output())

    if return_code != 0:
        exit(return_code)

    # Shared for destroy and apply
    var_file_arg = f"-var-file=tf_vars/{args.stage}.tfvars"

    if args.plan:
        terraform.plan(var_file_arg, args.save_plan, env=env)
        exit(1)

    if args.console:
        terraform.console(var_file_arg, env=env)
        exit(1)

    if args.destroy:
        terraform.destroy(var_file_arg, env=env)
        exit(1)

    terraform_code, terraform_output = terraform.apply(var_file_arg, taints=TAINT_ON_APPLY, env=env)

    if terraform_code != 0:
        exit(terraform_code)

    return_code = post_deploy_hook(terraform_output)

    if return_code == 0:
        print("\nDeploy completed successfully!!")

    exit(return_code)
