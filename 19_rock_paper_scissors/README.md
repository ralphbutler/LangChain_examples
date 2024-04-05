# rock\_paper\_scissors
These files were used to experiment using Aider and CursorAI to build software agents via AI-enabled software.  Below are the comments that I sent to some folks about how they were used and developed.

Ross and Gordon are going to run an experiment helping some acquaintances learn to “program” by using the new AI technologies.
So, I decided to try a version of that experiment on myself.  There are 3 programs attached and described below.
One note - LLMs are not usually up on the current version of LangChain.  So, I had a choice of feeding in a mountain of LC docs,
or to just simply provide an example program with examples of stuff the way I like it.

### 00\_agent\_template.py  
This is a program that I told Aider to use as a base, i.e. that this program represents the techniques I use most when building
agents with LangChain, including using Pydantic to get structured results.  It has one agent.  Then I told Aider to take that template 
program and use it as a guide to build a new program that has two agents that play rock-paper-scissors.   
Aider did as I requested and produced the next program.

### 01\_game.py
I did not touch this program but just left it alone in case I had to come back to it.
However, I did copy it to the next program to begin hacking on.

### 02\_game.py
I opened this program in CusorAI and realized that there were quite a few changes that I wanted to make to it.
For example, I wanted the game play to occur in rounds where each player selects a move in each round and we keep score.
I made it a point to never do any edits by hand.  I always used the cmd-K option to type in a sentence about what I wanted
to do next, and sometimes provided a little extra comment on details of what I wanted.
One interesting thing that happened during this phase was that I ran out of my free GPT-4 uses inside CursorAI.  LOL
It switched over to GPT-3.5 (and I think I may have had another choice or two, but don’t recall).  Using 3.5 Cursor made one error 
that I can remember, and I told it to fix that error, and it did.