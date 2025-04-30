import argparse

from terraform import destroy


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

    destroy(args.env, args.user)

if __name__ == "__main__":
    destroy_terraform()
