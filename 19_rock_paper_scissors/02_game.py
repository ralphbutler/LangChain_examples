import random

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
    return random.choice(legal_moves)

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

game_tools = [game_move_validator]

def create_game_agent(agent_name: str) -> AgentExecutor:
    agent_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"You are a strategic game-playing agent named {agent_name}."),
            ("human", human_template_string),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )
    agent_executor = AgentExecutor(
        agent=create_openai_functions_agent(
            llm=llm,
            prompt=agent_prompt,
            tools=game_tools,
        ),
        tools=game_tools,
        verbose=False,
    )
    return agent_executor

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

    # Create a dictionary to map agent executors to their names
    agent_names = {}

    # Create two game agents
    agent1 = create_game_agent('Agent1')
    agent_names[id(agent1)] = 'Agent1'
    agent1_score = 0

    agent2 = create_game_agent('Agent2')
    agent_names[id(agent2)] = 'Agent2'
    agent2_score = 0

    # Main game loop
    for turn in range(5):
        current_agent1 = agent1
        current_agent2 = agent2

        query = "Make your move in the game of Rock, Paper, Scissors."
        
        response1 = current_agent1.invoke({
            "query": query,
            "format_instructions": format_instructions,
            "agent_scratchpad": game_state,
        })
        move1 = pydantic_parser.parse(response1["output"]).move
        
        response2 = current_agent2.invoke({
            "query": query,
            "format_instructions": format_instructions,
            "agent_scratchpad": game_state,
        })
        move2 = pydantic_parser.parse(response2["output"]).move
        
        game_state['moves'].append((move1, move2))  # Append a tuple with both moves
        
        print(f"Turn {turn + 1}: {agent_names[id(current_agent1)]} made the move {move1} and {agent_names[id(current_agent2)]} made the move {move2}")
    # Determine the winner of the round and update the score
        if move1 == 'rock' and move2 == 'scissors':
            agent1_score += 1
        elif move1 == 'scissors' and move2 == 'paper':
            agent1_score += 1
        elif move1 == 'paper' and move2 == 'rock':
            agent1_score += 1
        elif move2 == 'rock' and move1 == 'scissors':
            agent2_score += 1
        elif move2 == 'scissors' and move1 == 'paper':
            agent2_score += 1
        elif move2 == 'paper' and move1 == 'rock':
            agent2_score += 1

    print("Game over. Moves made:", game_state['moves'])
    print("Final Score - Agent1:", agent1_score, "Agent2:", agent2_score)
