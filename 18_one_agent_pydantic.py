
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain.output_parsers import PydanticOutputParser

@tool
def preferred_integer_checker(val: int) -> bool:
    """examine the val integer to determine if it is a 'preferred' integer"""
    print("DBGPC",val)
    preferred = (11, 22)
    return val in preferred

llm = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0.0)

human_template_string = """
You are a helpful assistant providing information about American history.
Use the formatting instructions below to provide the answers to user queries.

QUERY:
{query}

FORMATTING_INSTRUCTIONS:
{format_instructions}
If you can not find a value for a field, then assign it the value "None".
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a friendly, helpful assistant."),
        ("human", human_template_string),
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
    from pydantic import BaseModel
    class PreferredNum(BaseModel):
        number: int
    pydantic_parser = PydanticOutputParser(pydantic_object=PreferredNum)
    format_instructions = pydantic_parser.get_format_instructions()
    query = """\
            Find a number between 8 and 30 that is one of our 'preferred' numbers;
            you can use a tool to determine if a particular number is preferred.
            Format the result according to the provided format instructions."""
    response = checker_agent_executor.invoke({
        "query": query,
        "format_instructions": format_instructions,
    })
    print(response["output"])

    parsed_output = pydantic_parser.parse(response["output"])
    print(parsed_output)
