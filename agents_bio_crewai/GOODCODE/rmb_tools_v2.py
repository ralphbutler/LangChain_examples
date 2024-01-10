
# for SQL
import sqlite3
# from langchain.utilities import SQLDatabase
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

# for RAG
from gensim.parsing.preprocessing import remove_stopwords, STOPWORDS
from langchain.retrievers import EnsembleRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from langchain.tools import tool

def SqlTool(llm,sql_dbname):
    sql_db = SQLDatabase.from_uri(f"sqlite:///{sql_dbname}")
    db_chain = SQLDatabaseChain.from_llm(llm, sql_db, verbose=True)

    class TheTool():
        @tool("Perform SQL query")
        def do_sql_query(query):
            """Useful to perform an SQL query.
               Input should be an English query from which enough info can be
               extracted to do the SQL query.
            """
            print("DBGSQL1",query)
            response = db_chain.run(query)
            print("DBGSQL2",response)
            return str(response)

    return TheTool.do_sql_query

def RagTool(llm, chroma_dbname, bm25_filename):
    stopwords = [ s for s in STOPWORDS if len(s) <= 3 ]

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=chroma_dbname,
    )

    chroma_retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    with open(bm25_filename) as f:
        bmtexts = [ line.strip() for line in f ]
    bm25_retriever = BM25Retriever.from_texts(bmtexts)
    bm25_retriever.k = 3

    ensemble_retriever = EnsembleRetriever(
        retrievers=[chroma_retriever, bm25_retriever],
        weights=[0.5, 0.5],
    )

    # qa_chain = RetrievalQA.from_chain_type(
        # llm=llm,
        # chain_type="stuff", # stuff -> all in at once
        # retriever=ensemble_retriever,
        # return_source_documents=True,
    # )
    qa_chain = RetrievalQA.from_llm(
        llm=llm,
        retriever=ensemble_retriever,
    )

    class TheTool():
        @tool("Perform an ensemble (vectorDB or BM25) query")
        def do_rag_query(query):
            """Useful to perform query against a set of text files.
               Input should be an English query from which enough info can be
               extracted to use in the query.
            """
            print("DBGRAG1")
            query_no_stopwords = remove_stopwords(query,stopwords)
            response = qa_chain(query_no_stopwords)
            print("DBGRAG2")
            return str(response['result'])

    return TheTool.do_rag_query
