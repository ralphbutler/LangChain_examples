
from z3 import *

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

curr_readings = None  # init

class Z3_safe_value(BaseModel):
    """provide a bool that tells if the state is safe based on values of gauges"""

    state: str = Field(..., description="indicate if state of the gauges is safe")

@tool
def z3_determine_if_state_is_safe(scientist_constraints: str):
    """determine if the values of gauges indicate that the state is safe"""

    print("DBGSC",scientist_constraints)
    llm = ChatOpenAI(model="gpt-4-turbo-2024-04-09")

    # convert scientist constraints to z3 constraints
    query = f"""
        We have defined these four z3 variables to represent the value on each of
        four gauges.  We use those values to determine if the current state is safe.
        of DNA sequence machine mode we wish to use today:
            G1 = Int('G1')
            G2 = Int('G2')
            G3 = Int('G3')
            G4 = Int('G4')

        Please create a python list of z3 constraints for these requirements:
        {scientist_constraints}

        Do not write an entire python program; just create the list of z3 constraints.
        Do NOT write any thing other than the list of constraints.
        Do NOT write the python``` markers either.
        """
    response = llm.invoke(query)

    G1 = Int('G1')
    G2 = Int('G2')
    G3 = Int('G3')
    G4 = Int('G4')
    gauges = {'G1': G1, 'G2': G2, 'G3': G3, 'G4': G4}

    solver = Solver()
    print("CONTENT",type(response.content),response.content)
    constraints = eval( response.content )  # eval can be bad :-)
    for constraint in constraints:
        print("DBG1",type(constraint),constraint)
        solver.add( constraint )
    print("SOLVER BEFORE:", solver)
    assumptions = [gauges[gauge] == value for (gauge,value) in curr_readings.items()]

    if solver.check(assumptions) == sat:   ## assumptions ( unusual use of check() ? )
        print("SOLVER AFTER:", solver)
        model = solver.model()
        print("MODEL:", model)
        return "safe"  # readings are safe
    else:
        return "unsafe" # readings are not safe

sample_scientist_directions = """
    1.  If G1 goes over 50, G2 must be below 30.
    2.  If G1 goes over 70, G3 must be below 40.
    3.  If either G2 or G3 goes over 35, G4 must be below 80.
    4.  All Gauges must be between 0 and 100.
"""

gauge_readings = [
    {'G1': 66, 'G2': 22, 'G3': 38, 'G4': 70},  # safe
    {'G1': 40, 'G2': 88, 'G3': 38, 'G4': 70},  # safe
    {'G1': 111, 'G2': 88, 'G3': 38, 'G4': 70}, # UNsafe
]

tools = [z3_determine_if_state_is_safe]

llm = ChatOpenAI(model="gpt-4-turbo-2024-04-09")
llm_with_tools = llm.bind_tools(tools)
llm_structured = llm.with_structured_output(Z3_safe_value, method="json_mode")

done = False
for timeidx in range(len(gauge_readings)):   # loop monitoring the gauges over time
    curr_readings = gauge_readings[timeidx]

    query = f"""Is the system in a safe state given these constraints:
             {sample_scientist_directions}
             Do NOT modify the constraints.
             Respond in JSON with `state` as the key.
             """
    # build new messages to send to llm for full query including tool invocations
    messages = [HumanMessage(query)]
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    for tool_call in ai_msg.tool_calls:
        selected_tool = {"z3_determine_if_state_is_safe": z3_determine_if_state_is_safe}[tool_call["name"].lower()]
        tool_output = selected_tool.invoke(tool_call["args"])
        messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
    print("DBGBEGMSGS")
    for message in messages:
        print(type(message))
        print(message)
        print("-"*50)
    print("DBGENDMSGS")
    response = llm_structured.invoke(messages)
    print("-"*50,"\nSTATE for TIME",timeidx, response)

print("*** EXITING") ; exit(0)
