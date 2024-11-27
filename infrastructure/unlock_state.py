import signal
import subprocess


def unlock_state(lock_id):
    """
    Manually unlocks the state file for the current configuration.
    This command does not modify infrastructure,
    but rather removes the lock on the state file stored on the remote backend.

    This is especially useful when a terraform operation exists abruptly without returning the lock,
    leaving the infrastructure immutable until the lock is manually removed.
    """

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        command = ["terraform", "force-unlock", "-force", lock_id]
        terraform_process = subprocess.Popen(command)
        terraform_process.wait()
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)
        terraform_process.wait()

    # ignore error
    return 1
