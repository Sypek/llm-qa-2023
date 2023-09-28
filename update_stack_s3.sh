aws cloudformation update-stack \
  --stack-name LLMStackS3 \
  --template-body file://s3_bukcet_template.yaml \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-update-complete --stack-name LLMStackS3