aws cloudformation create-stack \
  --stack-name LLMStack \
  --template-body file://infrastructure/template.yaml \
  --parameters ParameterKey=DevRoleArn,ParameterValue=arn:aws:sts::549693052025:assumed-role/IibsAdminAccess-DO-NOT-DELETE/kubasyp@MIDWAY.AMAZON.COM \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name LLMStack