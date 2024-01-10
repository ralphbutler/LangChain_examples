import sys, os, time, textwrap
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process

llm = ChatOpenAI(model_name='gpt-4', temperature=0.0)

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
    tools=[],
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
    allow_delegation=True
)

## Get the EC value for reaction rxn34000.
## Is there any genome feature that has the same EC value as reaction rxn34000?
task1 = Task(
  description=textwrap.dedent("""
      If any SQL access is required, you have access to a table that was created
      with this SQL command:
          ```sql
              CREATE TABLE IF NOT EXISTS reactions (
                  REACTION_ID TEXT PRIMARY KEY,
                  EC TEXT
          ```
      Create a description of the sub-queries to handle this user-query:
          Get the EC value for reaction rxn34000 and info about any genome
          feature that has the same EC.
      Prepare the correct sub-queries (there may just be one) and pass them
      along to the query_exector.
  """),
  agent=query_planner
)

task2 = Task(
    description=textwrap.dedent("""
        We are only testing so will not truly execute the subqueries.
        Print the first sub-query that you would execute.
        Pretend that the info retrieved from the first is:  FOOBAR
        Then print the second sub-query you would perform by using the
        info obtained from the first.
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
