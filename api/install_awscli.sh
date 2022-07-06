#!/bin/bash

curl -s "https://awscli.amazonaws.com/awscli-exe-linux-`uname -m`.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
