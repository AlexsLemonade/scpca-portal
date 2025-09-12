# Cellbrowser

## Contents of folder

This folder contains the two modified files to the cellbrowser static site hosted on s3.

## Updating the customized files

Updating the files is as simple as copying them over with the s3 command.

```bash

aws s3 [--profile scpca] cp ./index.html s3://[bucket-name]/index.html

```

### Production example  
```bash
s3 --profile scpca cp ./index.html s3://scpca-portal-cellbrowser-deployer-prod/index.html
```

### Staging example  
```bash
s3 --profile scpca cp ./index.html s3://scpca-portal-cellbrowser-deployer-staging/index.html
```
