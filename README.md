# LangChain_examples
LangChain examples for AuroraGPT

The main examples here have names that begin with a number and an underscore,
e.g. 01_quickstart.ipynb
They are simple examples (snippets of code with some text), not full tutorials.

The examples numbered 01 - 15 are in the form of ipynb files and we used that format
because they can be loaded into VSCode and cells run there.  They can also be exported
as stand-alone python programs if desired.

However, examples numbered 16 and beyond are simple python programs.  We have shifted
to that format because VSCode can treat a block of code as a cell if it is preceded 
by the magical #%% comment.  And, so individual "cells" can still be run using the 
Jupyter extensions.

Perhaps more important is the fact that examples numbered 16 and beyond were built 
using newer LangChain versions (0.1+) which had many changes and updates, and which
deprecated a lot of the older code.
