aws cloudformation update-stack \
  --stack-name LLMStackKendra \
  --template-body file://template.yaml \
  --parameters ParameterKey=S3BucketName,ParameterValue=llmstacks3-s3bucket-1b39zw19b74me \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-update-complete --stack-name LLMStackS3