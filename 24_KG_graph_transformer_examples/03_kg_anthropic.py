
# %%
import sys, os, time

from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.chains import GraphCypherQAChain
from langchain_core.documents import Document
from langchain_anthropic import ChatAnthropic

# %%
url = "bolt://localhost:7687"
username ="neo4j"
password = "foobar_neo4j"

# %%
graph = Neo4jGraph(
    url=url, 
    username=username, 
    password=password
)


# model_name = "claude-3-opus-20240229"
model_name = "claude-3-haiku-20240307"
llm = ChatAnthropic(temperature=0, model_name=model_name)

llm_transformer = LLMGraphTransformer(llm=llm)

text = """
Marie Curie, born in 1867, was a Polish and naturalised-French physicist and
chemist who conducted pioneering research on radioactivity.  She was the first
woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the
only person to win a Nobel Prize in two scientific fields.  Her husband, Pierre
Curie, was a co-winner of her first Nobel Prize, making them the first-ever
married couple to win the Nobel Prize and launching the Curie family legacy of
five Nobel Prizes.  She was, in 1906, the first woman to become a professor at the
University of Paris.
"""

documents = [Document(page_content=text)]
graph_documents = llm_transformer.convert_to_graph_documents(documents)
print(f"Nodes:{graph_documents[0].nodes}")
print(f"Relationships:{graph_documents[0].relationships}")
print("-"*50)

graph.add_graph_documents(graph_documents)

#### and now do a few simple queries to verify it is working

# get index info just for fun
result = graph.query("""
    SHOW INDEXES
    YIELD name, type, labelsOrTypes, properties, options
""")
print("NUMIDXS",len(result))
print("all indexes:")
for x in result:
    print(x)
print("-"*50)

# retrieve a little info that was inserted
# first with Cypher queries
result = graph.query("""
    MATCH (p:Person)
    RETURN p
""")
print(result)
for x in result:
    print(x)
print("-"*50)

# next with LangChain using NLP queries
llm_query = ChatAnthropic(temperature=0, model_name=model_name)
chain = GraphCypherQAChain.from_llm( llm_query, graph=graph, verbose=False,)
query = "Who are all the Persons listed in the graph database?"
response = chain.invoke(query)
print(response)
print(response["result"])
print("-"*50)
