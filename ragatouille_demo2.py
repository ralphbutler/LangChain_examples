
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ragatouille import RAGPretrainedModel

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

prompt = ChatPromptTemplate.from_template(
    """Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}"""
)

rag_index = RAG.from_index(".ragatouille/colbert/indexes/gregory_castle")
retriever = rag_index.as_langchain_retriever(k=8)

llm = ChatOpenAI()

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

query = "How man storeys are in the castle inherited by Scottish physician David Gregory?"
result = retrieval_chain.invoke( {"input": query} )
print("RESULT:",result["answer"])
