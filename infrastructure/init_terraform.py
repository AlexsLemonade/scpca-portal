import os
import signal
import subprocess


def init_terraform(env, user):
    """Initializes terraform's backend.

    Should be called before calling other terraform commands.
    """
    init_bucket = f"-backend-config=bucket=scpca-portal-tfstate-{env}"
    init_key = f"-backend-config=key=terraform-{user}.tfstate"

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        command = [
            "terraform",
            "init",
            init_bucket,
            init_key,
            "-backend-config=dynamodb_table=scpca-portal-terraform-lock",
            "-force-copy",
        ]
        terraform_process = subprocess.Popen(command, env=dict(os.environ, TF_LOG="TRACE"))
        terraform_process.wait()
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)
        terraform_process.wait()

    return terraform_process.returncode
