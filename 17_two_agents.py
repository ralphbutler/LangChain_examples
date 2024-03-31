
# use two agents where one checks the output of the other; they are not likely
#   to find a preferred number unless we were to iterate over them, and then
#   we would have to add logic to cause the search to ignore prior guesses

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool

@tool
def random_integer_picker() -> int:
    """choose a random integer for checking to see if it is 'preferred' """
    print("DBGRP")
    import random
    val = random.randint(1,100)
    return val

@tool
def preferred_integer_checker(val: int) -> bool:
    """examine the val integer to determine if it is a 'preferred' integer"""
    print("DBGPC")
    preferred = (11, 22, 33, 44, 55, 66, 77, 88, 99)
    return val in preferred

llm = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0.0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a friendly, helpful assistant."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

picker_tools = [random_integer_picker]

picker_agent = create_openai_functions_agent(
    llm=llm,
    prompt=prompt,
    tools=picker_tools
)

picker_agent_executor = AgentExecutor(
    agent=picker_agent,
    tools=picker_tools,
    verbose=False,
    # max_iterations=2,
)

checker_tools = [preferred_integer_checker]

checker_agent = create_openai_functions_agent(
    llm=llm,
    prompt=prompt,
    tools=checker_tools
)

checker_agent_executor = AgentExecutor(
    agent=checker_agent,
    tools=checker_tools,
    verbose=False,
)

if __name__ == '__main__':
    r1 = picker_agent_executor.invoke( {"input": "pick one random number between 8 and 30 to check for preferred"} )
    print(r1)
    r2 = checker_agent_executor.invoke( {"input": "check for preferred " + str(r1)} )
    print(r2)
