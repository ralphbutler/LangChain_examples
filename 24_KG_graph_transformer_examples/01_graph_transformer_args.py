
####
# these examples do NOT actually put data into a graph; they prepare the
#   data to be inserted; examples of inserting:
#        graph.add_graph_documents(graph_documents)
#   are in later demos

# %%
import sys, os, time

from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

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


llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

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

################
# WE CAN FILTER THE SET OF NODES FOR THE GRAPH
################

llm_transformer_filtered = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Country", "Organization"],
    allowed_relationships=["NATIONALITY", "LOCATED_IN", "WORKED_AT", "SPOUSE"],
)
graph_documents_filtered = llm_transformer_filtered.convert_to_graph_documents(
    documents
)
print(f"Nodes:{graph_documents_filtered[0].nodes}")
print(f"Relationships:{graph_documents_filtered[0].relationships}")
print("-"*50)

################
# WE CAN SPECIFY node_properties:
#    The node_properties parameter enables the extraction of node properties,
#    allowing the creation of a more detailed graph. When set to True, LLM autonomously
#    identifies and extracts relevant node properties. Conversely, if node_properties
#    is defined as a list of strings, the LLM selectively retrieves only the specified
#    properties from the text.
################

llm_transformer_props = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Country", "Organization"],
    allowed_relationships=["NATIONALITY", "LOCATED_IN", "WORKED_AT", "SPOUSE"],
    node_properties=["born_year"],
)
graph_documents_props = llm_transformer_props.convert_to_graph_documents(documents)
print(f"Nodes:{graph_documents_props[0].nodes}")
print(f"Relationships:{graph_documents_props[0].relationships}")
print("-"*50)


## put them into the graph database
graph.add_graph_documents(graph_documents_props)
