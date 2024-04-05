from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain.output_parsers import PydanticOutputParser
from typing import List, Dict

@tool
def game_move_validator(move: str) -> bool:
    """Validate if the move is legal in the game context"""
    # This is a placeholder for actual game logic
    legal_moves = ('rock', 'paper', 'scissors')
    return move in legal_moves

llm = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0.0)

human_template_string = """
You are a strategic game-playing agent. Your goal is to win the game by making smart moves.
Use the formatting instructions below to provide your move.

QUERY:
{query}

FORMATTING_INSTRUCTIONS:
{format_instructions}
If you can not decide on a move, then assign it the value "None".
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a strategic game-playing agent."),
        ("human", human_template_string),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

checker_tools = [game_move_validator]

def create_game_agent(agent_name: str) -> AgentExecutor:
    agent_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"You are a strategic game-playing agent named {agent_name}."),
            ("human", human_template_string),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )
    return AgentExecutor(
        agent=create_openai_functions_agent(
            llm=llm,
            prompt=agent_prompt,
            tools=checker_tools,
        ),
        tools=checker_tools,
        verbose=False,
    )

if __name__ == '__main__':
    from pydantic import BaseModel
    class GameMove(BaseModel):
        move: str
    pydantic_parser = PydanticOutputParser(pydantic_object=GameMove)
    format_instructions = pydantic_parser.get_format_instructions()

    # Define the game state and the agents
    game_state = {
        'moves': []
    }

    # Create two game agents
    agent1 = create_game_agent('Agent1')
    agent2 = create_game_agent('Agent2')

    # Main game loop
    for turn in range(10):  # Simulate 10 turns
        current_agent = agent1 if turn % 2 == 0 else agent2
        query = "Make your move in the game of Rock, Paper, Scissors."
        response = current_agent.invoke({
            "query": query,
            "format_instructions": format_instructions,
            "agent_scratchpad": game_state,
        })
        move = pydantic_parser.parse(response["output"]).move
        game_state['moves'].append(move)
        # print(f"Turn {turn + 1}: {current_agent.agent.prompt.messages[0][1]} made the move {move}")
        print(f"Turn {turn + 1}: made the move {move}")

    print("Game over. Moves made:", game_state['moves'])
