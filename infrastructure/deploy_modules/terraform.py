"""
This module is a collection of terraform commands that are used for deployment or debugging.

Exported functions:
    - init
    - apply
    - output
    - destroy
    - force_unlock
    - replace_provider
"""

import subprocess
import json
import signal
import os


def init(configs=[], log_trace=True):
    """Initializes terraform's backend.

    Should be called before calling other terraform commands.

    Accepts a list of configs to be passed to apply.
    ex: bucket=the-name-of-your-bucket
    """

    # TODO: Remove bucket and key defaults?
    backend_config = [f"-backend-config={config}" for config in configs]

    # -reconfigure
    terraform_init = ["terraform", "init", "-upgrade"]
    command = terraform_init + backend_config + ["-force-copy"]

    # Pass environment to init
    init_environ = os.environ.copy()

    if log_trace:
        init_environ = dict(os.environ, TF_LOG="TRACE")

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        terraform_process = subprocess.Popen(command, env=init_environ)
        terraform_process.wait()
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)
        terraform_process.wait()

    return terraform_process.returncode


def output():
    process = subprocess.Popen(["terraform", "output", "-json"], stdout=subprocess.PIPE)

    process.wait()

    return json.loads(process.stdout.read().decode("utf-8"))


def apply(var_file_arg, taints=[], environ=os.environ.copy(), print_output=True):
    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        taint_output = {}

        for taint in taints:
            process = subprocess.Popen(["terraform", "taint", taint], env=environ)
            process.wait()

            taint_output.update(output())

        process = subprocess.Popen(
            ["terraform", "apply", var_file_arg, "-auto-approve"], env=environ
        )
        process.wait()

        apply_output = output()

    except KeyboardInterrupt:
        process.send_signal(signal.SIGINT)
        process.wait()

    merged_output = {**taint_output, **apply_output}

    if print_output:
        print(json.dumps(merged_output, indent=2))

    return process.returncode, merged_output


def destroy(env, user):
    # init terrafrom first
    init(env, user)

    # locally defined defaults
    var_file_arg = f"-var-file=tf_vars/{env}.tfvars"

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        terraform_process = subprocess.Popen(
            ["terraform", "destroy", var_file_arg, "-auto-approve"]
        )
        terraform_process.wait()
        exit(terraform_process.returncode)
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)


def force_unlock(lock_id):
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
        process = subprocess.Popen(command)
        process.wait()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGINT)
        process.wait()

    # ignore error
    return process.returncode


def replace_provider(org, provider):
    """
    Replaces the aws provider.
    Takes an org name, and a provider,
    and changes the terraform state to use the new qualified provider.
    """

    # Make sure that Terraform is allowed to shut down gracefully.
    try:
        command = [
            "terraform",
            "state",
            "replace-provider",
            "-auto-approve",
            f"registry.terraform.io/-/{provider}",
            f"registry.terraform.io/{org}/{provider}",
        ]
        terraform_process = subprocess.Popen(command)
        terraform_process.wait()
    except KeyboardInterrupt:
        terraform_process.send_signal(signal.SIGINT)
        terraform_process.wait()

    return terraform_process.returncode
