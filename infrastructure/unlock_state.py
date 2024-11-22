import signal
import subprocess


def replace_provider(lock_id):
    """
    Replaces the aws provider.
    Takes an org name, and a provider,
    and changes the terraform state to use the new qualified provider.
    """

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        command = [
            "terraform",
            "force-unlock",
            "-force",
            lock_id
        ]
        terraform_process = subprocess.Popen(command)
        terraform_process.wait()
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)
        terraform_process.wait()

    # ignore error
    return 1
