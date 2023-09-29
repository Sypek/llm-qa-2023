from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
import json
from templates import standalone_question_prompt, combine_docs_prompt

AWS_REGION = ''
KENDRA_INDEX_ID = ''
ENDPOINT = ''

class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"text_inputs": prompt, **model_kwargs})
        return input_str.encode('utf-8')
    
    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["generated_texts"][0]
    

def build_chain() -> ConversationalRetrievalChain:
    content_handler = ContentHandler()

    llm=SagemakerEndpoint(
            endpoint_name=ENDPOINT, 
            region_name=AWS_REGION, 
            model_kwargs={"temperature":1e-10, "max_length": 500},
            content_handler=content_handler
        )
        
    retriever = AmazonKendraRetriever(index_id=KENDRA_INDEX_ID, region_name=AWS_REGION)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        condense_question_prompt=standalone_question_prompt, 
        return_source_documents=True, 
        combine_docs_chain_kwargs={"prompt":combine_docs_prompt})
    
    return chain

def run_chain(chain, prompt: str, history=[]) -> ConversationalRetrievalChain:
    return chain({"question": prompt, "chat_history": history})

