aws cloudformation create-stack \
  --stack-name LLMStackS3 \
  --template-body file://s3_bukcet_template.yaml \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name LLMStackS3