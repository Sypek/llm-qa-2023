aws cloudformation create-stack \
  --stack-name LLMStack \
  --template-body file://infrastructure/template.yaml \
  --parameters ParameterKey=DevRoleArn,ParameterValue=XXXXXXXXX \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name LLMStack