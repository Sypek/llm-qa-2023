from langchain.prompts import PromptTemplate

prompt_template = """
    The following is a friendly conversation between a human and an AI, where user asks questions to the documentation provided in the context.
    If the AI does not know the answer to a question, it says: "I don't know the answer"
    Context:
    {context}

    Instruction: Based on the above context, provide a detailed answer for this question: "{question}"

    Solution:"""

combine_docs_prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

condense_qa_template = """
    Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)