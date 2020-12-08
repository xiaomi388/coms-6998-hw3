#!/bin/bash

# shellcheck disable=SC2164
cd "$1/package"
zip -r "../function.zip" .

cd ..
zip -g function.zip index.py
aws lambda update-function-code --function-name "$LF1" --zip-file fileb://function.zip --region "$AWS_DEFAULT_REGION"
