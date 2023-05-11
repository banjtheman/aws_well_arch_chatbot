from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
import os

# Set Context for response
TEMPLATE = """You are an AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. Return your response in markdown, so you can bold and highlight important steps for customers. If the answer cannot be found within the context, write 'I could not find an answer' 

Use the following context from the AWS Well-Architected Framework to answer the user's query. Make sure to read all the context before providing an answer.\nContext:\n{context}\nQuestion: {question}
"""

QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])


def setup_chain():
    llm = ChatOpenAI(
        temperature=0.7,
        openai_api_key=os.environ["OPENAI_API_KEY"],
        model_name="gpt-3.5-turbo",
    )
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    vectorstore = FAISS.load_local("local_index", embeddings)

    chain = ConversationalRetrievalChain.from_llm(
        llm, vectorstore.as_retriever(), return_source_documents=True
    )

    return chain
