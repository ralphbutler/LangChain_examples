
import sys, os, time

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

embeddings = OpenAIEmbeddings()
vectordb = Chroma(
    embedding_function=embeddings,
    persist_directory="./genomes.chromadb",
)

# k docs to return, default 4
retriever = vectordb.as_retriever(search_kwargs={"k": 3})
print("SEARCH TYPE",retriever.search_type)
print("SEARCH KWARGS",retriever.search_kwargs)

llm = ChatOpenAI(temperature=0.0, model_name='gpt-4')

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

query = "What is the name of the genome with identifier 83332.12 ?"
llm_response = qa_chain(query)
print("LLM_RESPONSE")
print(llm_response)
print("RESULT")
print(llm_response["result"])
