import argparse
import signal
import subprocess

from init_terraform import init_terraform


def destroy_terraform():
    description = """This script can be used to destroy an infrastructure stack that was created
    with deploy.py. This script must be run from /infrastructure!"""
    parser = argparse.ArgumentParser(description=description)

    env_help_text = """Specify the environment you would like to deploy to. Not optional.
    Valid values are: prod, staging, and dev `prod` and `staging` will deploy the
    production stack. These should only be used from a deployment machine. `dev` will
    deploy a dev stack which is appropriate for a single developer to use to test."""
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

    args = parser.parse_args()

    init_terraform(args.env, args.user)

    var_file_arg = "-var-file=tf_vars/{}.tfvars".format(args.env)

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        terraform_process = subprocess.Popen(
            ["terraform", "destroy", var_file_arg, "-auto-approve"]
        )
        terraform_process.wait()
        exit(terraform_process.returncode)
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)


if __name__ == "__main__":
    destroy_terraform()
