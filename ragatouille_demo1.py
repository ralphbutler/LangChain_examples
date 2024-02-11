# there sorta 2 programs in one here, second below ========

import os
os.system("rm -rf .ragatouille/colbert/")  # start over

from ragatouille import RAGPretrainedModel

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

collection = []
with open("./in.gregory") as f:
    gregory_doc = f.read()
print(gregory_doc[:100])
collection.append(gregory_doc)
with open("./in.kinnairdy") as f:
    kinnairdy_doc = f.read()
print(kinnairdy_doc[:100])
collection.append(kinnairdy_doc)

RAG.index(
    collection=collection,
    index_name="gregory_castle",
    max_document_length=400,
    split_documents=True,
)

result = RAG.search(query="What castle did David Gregory inherit?", k=8)
print("NUMBER MATCH DOCS", len(result))
content0 = result[0]["content"]
score0 = result[0]["score"]
print(f"SCORE {score0} CONTENT {content0[:100]}")
content1 = result[1]["content"]
score1 = result[1]["score"]
print(f"SCORE {score1} CONTENT {content1[:100]}")

retriever = RAG.as_langchain_retriever(k=8)
result = retriever.invoke("What castle did David Gregory inherit?")
print("RETRIEVER NUMBER MATCH DOCS", len(result))

#================

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    """Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}"""
)

llm = ChatOpenAI()

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

query = "How man storeys are in the castle inherited by Scottish physician David Gregory?"
result = retrieval_chain.invoke( {"input": query} )
print(result["answer"])
