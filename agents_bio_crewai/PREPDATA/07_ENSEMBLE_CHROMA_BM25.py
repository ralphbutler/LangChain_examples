
from langchain.retrievers import EnsembleRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


embeddings = OpenAIEmbeddings()
vectordb = Chroma(
    embedding_function=embeddings,
    persist_directory="./genomes.chromadb",
)

# k docs to return, default 4
chroma_retriever = vectordb.as_retriever(search_kwargs={"k": 3})
print("SEARCH TYPE",chroma_retriever.search_type)
print("SEARCH KWARGS",chroma_retriever.search_kwargs)

llm = ChatOpenAI(temperature=0.0, model_name='gpt-4')

with open("genomes.bm25") as f:
    bmtexts = [ line.strip() for line in f ]
bm25_retriever = BM25Retriever.from_texts(bmtexts)
bm25_retriever.k = 3

## in case we just want the relevant docs instead of the answer to a query
query = "What is the name of the genome with ID 83332.12 ?"
docs = bm25_retriever.get_relevant_documents(query, k=4)  # k=8 is default
docs_page_content = " ".join([d.page_content for d in docs])
print("RELEVANT DOCS")
print(docs_page_content)

ensemble_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", # stuff all in at once
    retriever=ensemble_retriever,
    return_source_documents=True,
)

query = "What is the name of the genome with ID 83332.12 ?"  # Mycobacterium tuberculosis H37Rv
llm_response = qa_chain(query)
print("RESPONSE1")
print(llm_response['result'])

# query = "What can you tell me about the feature with identifier fig|83332.12.peg.3671 ?"
query = "What is the gene name of the feature with identifier fig|511145.12.peg.1785 ?" # pheS
llm_response = qa_chain(query)
print("RESPONSE2")
print(llm_response['result'])

print("EXITING ****") ; exit(0)
