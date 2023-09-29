import os
from tqdm import tqdm
import boto3

STACK_NAME = 'LLMStackS3'
DATA_PATH = 'data/sagemaker_documentation/'

def get_cloud_formation_outputs() -> dict:
    cf_client = boto3.client('cloudformation')
    response = cf_client.describe_stacks(StackName=STACK_NAME)
    outputs = response["Stacks"][0]["Outputs"]

    cf_outputs = {}
    for i in outputs:
        cf_outputs[i['OutputKey']] = i['OutputValue']
    return cf_outputs


cf_config = get_cloud_formation_outputs()
role_arn = cf_config['DataUploaderRoleArn']
bucket_name = cf_config['S3BucketName']

sts_client = boto3.client('sts')

assumed_role_object=sts_client.assume_role(
    RoleArn=role_arn,
    RoleSessionName="AssumeRoleSession1"
)

credentials=assumed_role_object['Credentials']

s3_resource=boto3.resource(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
)

file_names_list = os.listdir(DATA_PATH)
file_paths_list = [os.path.join(DATA_PATH, i) for i in file_names_list]

print(f'There are {len(file_paths_list)} files.')

for filename, filepath in tqdm(zip(file_names_list, file_paths_list)):    
    s3_resource.Bucket(bucket_name).upload_file(filepath, os.path.join('input_data', filename))

print(f'Uploded all files to {bucket_name} s3 bucket.')