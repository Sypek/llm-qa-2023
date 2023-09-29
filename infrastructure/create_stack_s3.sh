aws cloudformation create-stack \
  --stack-name LLMStackS3 \
  --template-body file://s3_bukcet_template.yaml \
  --parameters ParameterKey=DevRoleArn,ParameterValue=[XXXXXX] \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name LLMStackS3

arn:aws:sts::878691224389:assumed-role/IibsAdminAccess-DO-NOT-DELETE/kubasyp@MIDWAY.AMAZON.CO