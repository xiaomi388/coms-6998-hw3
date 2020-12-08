#!/bin/bash

OLDPWD=$(dirname "$0")

mkdir -p ./package
# shellcheck disable=SC2164
cd "${OLDPWD}/package"
zip -r9 "${OLDPWD}/function.zip" .

# shellcheck disable=SC2164
cd "${OLDPWD}"
zip -g function.zip index.py
aws lambda update-function-code --function-name "$LF2" --zip-file fileb://function.zip --region "$AWS_DEFAULT_REGION"
