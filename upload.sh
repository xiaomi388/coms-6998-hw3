#!/bin/bash

# shellcheck disable=SC2164
cd "$1/package"
zip -r "../function.zip" .

cd ..
cat index.py
zip -g function.zip index.py
aws lambda update-function-code --function-name "$2" --zip-file fileb://function.zip --region "$AWS_DEFAULT_REGION"
