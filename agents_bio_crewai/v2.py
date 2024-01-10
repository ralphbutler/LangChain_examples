import sys, os, time, textwrap
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process

from rmb_tools import SqlTool, RagTool

USE_OPENAI = True

if USE_OPENAI:
    llm = ChatOpenAI(model_name='gpt-4-1106-preview', temperature=0.0)
else:
    from langchain_community.llms import LlamaCpp
    model_path = '/Users/rbutler/MODELS/TheBloke/mistral-7b-instruct-v0.1.Q5_K_M.gguf'
    llm = LlamaCpp(
        model_path=model_path,
        temperature=0.3,
        max_tokens=256,
        top_p=1,
        verbose=False,  # Verbose is required to pass to the callback manager
        streaming=False,  # turn on to stream as result being generated (debug)
        n_ctx=2048,   # buffer problems without this (rory uses 4096 in a pgm)
    )

sql_tool = SqlTool(
    llm=llm,
    sql_dbname="cpd_rxn.db"
)
rag_tool = RagTool(
    llm=llm,
    chroma_dbname="genomes.chromadb",
    bm25_filename="genomes.bm25",
)

query_planner = Agent(
    role="Query Planner",
    goal="Plan order in which to perform queries of SQL DB and text files",
    backstory=textwrap.dedent("""
        You are an expert at decomposing a user-query into sub-queries that such
        that the solution of the sub-queries in the correct order will result in
        a correct result to the user-query.
        Accept the user-query and determine if it requires sub-queries to both the
        SQL DB and to the text files about genomes and features of genomes.  In the
        case of both being required, determine which portion of the user-query can
        be satisfied by a sub-query and formulate both.
        Also, you have to determine which one of the sub-queries must be performed
        first; if data needs to be extracted from the SQL DB to use in the sub-query
        to the genome text files, then place the SQL sub-query first in the info you
        pass to the query_executor.
        Your final answer MUST be a description of one or two sub-queries that are
        in the correct order such that, when they are performed, the result is an
        answer to the user-query.
    """),
    verbose=True,
    allow_delegation=False,
    tools=[],  ###
    llm=llm,
)

query_executor = Agent(
    role="Searcher of SQL DBs and Text Files",
    goal="Perform sub-queries in the correct order",
    backstory=textwrap.dedent("""
        Accept descriptions of sub-queries from the query_planner agent and perform
        them in order.
        There may just be one sub-query, but if there are two, the result of the
        first sub-query will become part of the input for the second sub-query.
        It is important to include the info obtained from the first sub-query in
        the second sub-query so it will be complete.
        Perform the sub-queries in the order given and report the result out.
        Your final answer MUST be a correct response to the original user-query.
    """),
    verbose=True,
    llm=llm,
    # tools=[SqlTools.do_sql_query, RagTools.do_rag_query],
    tools=[sql_tool, rag_tool],
    allow_delegation=True,
)

## Get the EC value for reaction rxn34000 and info about any genome
##    feature that has the same EC.

# RAG only - worked
# user_query = "What is the name of the genome with identifier 83332.12 ?"

# SQL only - worked
# user_query = "Get the EC value for reaction rxn34000."

# both with RAG first - worked
# user_query = "Find a list of any reactions that have the same EC number as product Histidinol-phosphatase in genome feature fig|83332.12.peg.3503 ?"

# both with SQL first - worked
user_query = "Find a list of gene products in genome 83332.12 which have the same EC number as the EC number for reaction rxn34000 ?"

task1 = Task(
  description=textwrap.dedent(f"""
      If any SQL access is required, you have access to a table that was created
      with this SQL command:
          ```sql
              CREATE TABLE IF NOT EXISTS reactions (
                  REACTION_ID TEXT PRIMARY KEY,
                  EC TEXT
          ```
      Create a description of the sub-queries to handle this user-query:
          {user_query}
      Prepare the correct sub-queries (there may just be one) and pass them
      along to the query_executor.  You should only use the SQL query capability
      if the data is obviously in the SQL tables provided.
  """),
  agent=query_planner
)

task2 = Task(
    description=textwrap.dedent(f"""
        You will receive a set of one or two sub-queries from the query_planner.
        Use those tools to perform SQL queries and/or RAG (text) queries as necessary.
        Your final answer MUST be a correct answer to the original user-query:
            {user_query}
    """),
    agent=query_executor
)

crew = Crew(
    agents=[query_planner, query_executor],
    tasks=[task1, task2],
    verbose=2, # print what tasks are being worked on, can set it to 1 or 2
    process=Process.sequential,
)

result = crew.kickoff()

print("######################")
print(result)
