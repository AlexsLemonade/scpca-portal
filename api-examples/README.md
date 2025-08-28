# API Examples

## Overview

This documentation aims to provide an introduction to using the ScPCA Portal's API.

## Redoc

For a quick overview of the ScPCA Portal's API available endpoints and responses, please visit the [ScPCA Portal Redoc documentation](https://api.scpca.alexslemonade.org/docs/redoc).
This shows all available endpoints, accepted query parameters, and the structure of endpoint responses.

## Swagger

For an interactive user interface, please visit the [ScPCA Portal Swagger documentation](https://api.scpca.alexslemonade.org/docs/swagger).
There, you can submit queries and see real API responses.

## Clients

- [web](https://scpca.alexslemonade.org)

<!-- Should we add an interest form or link to github issue? -->
> [!NOTE]
> We will be releasing language specific clients in the future.

## API Tokens

All endpoints can be accessed without using an API Token.
However, in order to receive a download url for data, you must create a token to attach to your request.
This indicates that you have accepted the [ScPCA Portal's Terms of Use](https://scpca.alexslemonade.org/terms-of-service).

## Language Specific Example Scripts

We have prepared some example scripts for querying projects and samples then downloading their related computed files.

> [!IMPORTANT]
> Please review the script before running.
> You will need to update the email address variable in order to successfully execute the script.

### Bash
- [Download Project in Bash](./download-project.sh)
- [Download Sample in Bash](./download-samples.sh)

### Python
- [Download Project in Python](./download-project.py)
- [Download Sample in Python](./download-samples.py)
