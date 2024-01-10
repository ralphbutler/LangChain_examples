
import sys, os, time

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader

# os.system("rm -rf ./genomes.chromadb")  #### <----

# loader = TextLoader('./tempin')
loader = DirectoryLoader('./', glob="./genomes_txt/*.text", loader_cls=TextLoader)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    separators = ["\n"],
    keep_separator = False,
    strip_whitespace=True,   ### DOES NOT SEEM TO WORK
    chunk_size = 0,    # just splits on lines (separators)
    chunk_overlap  = 0,
    length_function = len,
    is_separator_regex = False,
    add_start_index = True,
)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
vectordb = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="genomes.chromadb"
)

# k docs to return, default 4
retriever = vectordb.as_retriever(search_kwargs={"k": 2})
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
