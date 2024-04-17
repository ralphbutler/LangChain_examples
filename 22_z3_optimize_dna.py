
from z3 import *

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

class Z3_values(BaseModel):
    """two numbers giving the number of sequencers to run in each mode"""

    num60K: int = Field(..., description="number of sequencers to run in 60000 mode")
    num40K: int = Field(..., description="number of sequencers to run in 40000 mode")

@tool
def z3_minimize_sequencers(scientist_constraints: str):
    """computes numbers of each of two modes to use for DNA sequencers"""

    print("DBGSC",scientist_constraints)
    llm = ChatOpenAI(model="gpt-4-turbo-2024-04-09")

    # convert scientist constraints to z3 constraints
    query = f"""
        We have defined these two z3 variables to represent the number of each type
        of DNA sequence machine mode we wish to use today:
            x = Int('x')
            y = Int('y')

        Please create a python list of z3 constraints for these requirements:
        {scientist_constraints}

        Do not write an entire python program; just create the list of z3 constraints.
        Do NOT write any thing other than the list of constraints.
        Do NOT write the python``` markers either.
        """
    response = llm.invoke(query)

    # create ints for numbers of machines of each mode to use
    x = Int('x')
    y = Int('y')

    solver = Optimize()
    print("DBGCONTENT",type(response.content),response.content)
    constraints = eval( response.content )  # eval can be bad :-)
    for constraint in constraints:
        print("DBG1",type(constraint),constraint)
        solver.add( constraint )
    solver.minimize(x)
    if solver.check() == sat:
        model = solver.model()
        print("DBG2",type(model[x]),model[x],type(model[y]),model[y])
        return str( (model[x].as_long(),model[y].as_long()) )
    else:
        return None

sample_scientist_directions = """
    1.  we have 22 sequencers, each of which can be configured in either of two modes
    2.  the first mode can sequence 60000 base pairs per hour
    3.  the second mode can sequence 40000 per hour
    4.  we prefer to use the second mode when possible because it is cheaper
    5.  we need to sequence 1000000 base pairs today
    """

tools = [z3_minimize_sequencers]

llm = ChatOpenAI(model="gpt-4-turbo-2024-04-09")
llm_with_tools = llm.bind_tools(tools)
llm_structured = llm.with_structured_output(Z3_values, method="json_mode")

query = f"""How many DNA sequencers of each mode should I use given these constraints:
         {sample_scientist_directions}
         Do NOT modify the constraints.
         Respond in JSON with `num60K` and `num40K` as keys.
         """
# chain = llm_with_tools | PydanticToolsParser(tools=tools)
# response = chain.invoke(query)
# response = llm_with_tools.invoke(query)
# response = llm_structured.invoke( query )
# print("DBG2",response)

# build new messages to send to llm for full query including tool invocations
messages = [HumanMessage(query)]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)
for tool_call in ai_msg.tool_calls:
    selected_tool = {"z3_minimize_sequencers": z3_minimize_sequencers}[tool_call["name"].lower()]
    tool_output = selected_tool.invoke(tool_call["args"])
    messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
print("DBGBEGMSGS")
for message in messages:
    print(type(message))
    print(message)
    print("-"*50)
print("DBGENDMSGS")
response = llm_structured.invoke(messages)
print("-"*50,"\nANSWER:")
print(response)

print("*** EXITING") ; exit(0)
