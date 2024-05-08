
# using langchain_experimental for tools with ollama

from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.schema import SystemMessage, HumanMessage
from langchain.chains import create_extraction_chain

def multiply_large_numbers(number1,number2):
    return number1 * number2

llm = OllamaFunctions(
    model="mistral",
    format="json",
    temperature=0,
)
llm = llm.bind_tools(   # llm = llm.bind( functions=
    tools=[
        {
            "name": "multiply_large_numbers",
            "description": "accept two large numbers and compute their result",
            "parameters": {
                "type": "object",
                "properties": {
                    "number1": {
                        "type": "int",
                        "description": "the first number",
                    },
                    "number2": {
                        "type": "int",
                        "description": "the second number",
                    },
                },
                "required": ["number1","number2"],
            },
        }
    ],
    function_call={"name": "multiply_large_numbers"},
)

query = """What is the result of multiplying 123456*654321 ?"""
result1 = llm.invoke(query)
print(result1)
print(type(result1))
print(result1.additional_kwargs["function_call"])
funcinfo = result1.additional_kwargs["function_call"]
funcname = funcinfo["name"]
import json
args = json.loads(funcinfo["arguments"])
print("DBG",type(args))
print(funcname, args)
func = globals()[funcname]
bignum = func(**args)
print(bignum)

