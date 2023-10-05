import json
import os
import shutil
from typing import Dict, List

import boto3
import langchain
from chroma_downloader import download_s3_folder
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.llms import GPT4All
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.vectorstores import Chroma
from templates import combine_docs_prompt, standalone_question_prompt

langchain.verbose = True
langchain.debug = True


def get_cloud_formation_outputs(stack_name: str) -> dict:
    cf_client = boto3.client('cloudformation')
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response["Stacks"][0]["Outputs"]

    cf_outputs = {}
    for i in outputs:
        cf_outputs[i['OutputKey']] = i['OutputValue']
    return cf_outputs


class ContentHandlerEmbeddings(EmbeddingsContentHandler):
    """Content Handler for embeddings model."""
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"text_inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["embedding"]


class ContentHandler(LLMContentHandler):
    """Content Handler for generative model."""
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"text_inputs": prompt, **model_kwargs})
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["generated_texts"][0]


STACK_NAME = 'LLMStack'
cf_config = get_cloud_formation_outputs(STACK_NAME)
AWS_REGION = cf_config['AWSRegion']
ENDPOINT_EMBEDDINGS = cf_config['SageMakerEndpointEmbeddings']
ENDPOINT_GENERATIVE = cf_config['SageMakerEndpointGenerative']
S3_BUCKET = cf_config['S3BucketName']
CHROMA_DIR_LOCAL = 'chroma'
CHROMA_DIR_S3 = 'chroma'
MODEL_PATH = '../data/models/llama-2-7b-chat.ggmlv3.q4_0.bin'


def load_local_vector_db(embeddings):
    if not os.path.exists(CHROMA_DIR_LOCAL):
        os.makedirs(CHROMA_DIR_LOCAL)
    else:
        shutil.rmtree(CHROMA_DIR_LOCAL)
    print('Downloading db files from s3...')
    download_s3_folder(S3_BUCKET, s3_folder=CHROMA_DIR_S3, local_dir=CHROMA_DIR_LOCAL)

    vectordb = Chroma(
        persist_directory=CHROMA_DIR_LOCAL,
        embedding_function=embeddings, 
        collection_name='sagemaker_docs')
    
    print('Downloaded db files from s3.')
    return vectordb


content_handler_embeddings = ContentHandlerEmbeddings()
embeddings = SagemakerEndpointEmbeddings(
    endpoint_name=ENDPOINT_EMBEDDINGS,
    region_name=AWS_REGION,
    content_handler=content_handler_embeddings
)

# Due to aws quotas on my test account, I'm using only a single sagemaker endpoint for embeddings.
# Hosting generative model locally. Using GPT4All.

# content_handler = ContentHandler()
# llm = SagemakerEndpoint(
#     endpoint_name=ENDPOINT_GENERATIVE,
#     region_name=AWS_REGION,
#     model_kwargs={"temperature": 0.1, "max_length": 200},
#     content_handler=content_handler
# )

llm = GPT4All(
    model=MODEL_PATH,
    max_tokens=2048,
    temp=0
)

vector_db = load_local_vector_db(embeddings)


def build_chain() -> ConversationalRetrievalChain:
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_db.as_retriever(),
        condense_question_prompt=standalone_question_prompt,
        return_source_documents=True,
        return_generated_question=True,
        combine_docs_chain_kwargs={"prompt": combine_docs_prompt}
    )
    return chain


def run_chain(chain, prompt: str, history=[]) -> ConversationalRetrievalChain:
    return chain({"question": prompt, "chat_history": history})

