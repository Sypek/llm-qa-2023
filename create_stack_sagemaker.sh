aws cloudformation create-stack \
  --stack-name LLMStackSagemaker \
  --template-body file://sagemaker_template.yaml \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name LLMStackSagemaker