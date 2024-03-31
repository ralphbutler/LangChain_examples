
# use the new langchain version to build an agent and demo that the agent will
#   loop until if finds a solution to the problem

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool

@tool
def preferred_integer_checker(val: int) -> bool:
    """examine the val integer to determine if it is a 'preferred' integer"""
    print("DBGPC",val)
    preferred = (11, 22)
    return val in preferred

llm = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0.0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a friendly, helpful assistant."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

checker_tools = [preferred_integer_checker]

checker_agent = create_openai_functions_agent(
    llm=llm,
    prompt=prompt,
    tools=checker_tools,
)

checker_agent_executor = AgentExecutor(
    agent=checker_agent,
    tools=checker_tools,
    verbose=False,
    # max_iterations=2,  # will not find the answer
)

if __name__ == '__main__':
    query = """Find a number between 8 and 30 that is one of our 'preferred' numbers;
               you can use a tool to determine if a particular number is preferred."""
    r1 = checker_agent_executor.invoke( {"input": query} )
    print(r1)
    print(r1["output"])
