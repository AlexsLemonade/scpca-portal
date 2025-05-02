import os
import subprocess


def build_and_push_docker_image(image_name, *build_args, build_dir="../api"):
    """docker-py doesn't seem to work, so use subprocess to call Docker"""

    # return 1
    cwd = os.getcwd()

    # Change dir so docker can see the code.
    os.chdir(build_dir)

    command = [
        "docker",
        "build",
    ]

    # insert build_args
    for build_arg in build_args:
        command.extend(build_arg.split(" ", 1))

    command.extend(
        [
            "--platform",
            "linux/amd64",
            "--tag",
            image_name,
            "-f",
            "Dockerfile.prod",
            ".",
        ]
    )

    # check_call() will raise an exception for us if this fails.
    completed_command = subprocess.check_call(command)

    docker_login_command = ["docker", "login"]

    if "DOCKER_USERNAME" in os.environ:
        docker_login_command.extend(["--username", "$DOCKER_USERNAME"])

        if "DOCKER_PASSWORD" in os.environ:
            docker_login_command = (
                ["echo", "$DOCKER_PASSWORD", "|"]  # pipe password
                + docker_login_command
                + ["--password-stdin"]  # take password from pipe
            )

    try:
        completed_command = subprocess.check_call(docker_login_command)
        print("Logged into docker.")
    except subprocess.CalledProcessError:
        print("Failed to login to docker.")
        return 1

    if completed_command != 0:
        return completed_command

    completed_command = subprocess.check_call(["docker", "push", image_name])

    # Change dir back so terraform is run from the correct location:
    os.chdir(cwd)

    return completed_command
