
This is a prototype of using agents to guide querying data from 2 sources:
    SQL DBs (reactions and compounds)
        use sqlite3 to hold the tables
    text files
        use an ensemble retriever based on chroma vectordb and bm25 for keywords

The current version of the prototype code is in:
    v2.py          version 2 ; not perfect but a good step
    rmb_tools.py   supporting tools for the current version

PREPDATA
    contains data and code to massage the data to get it ready for
        use in the programs; we don't really need genomes.bm25 but 
        it was useful to have in a slimmer form

GOODCODE
    is just backups of code that have reached some reasonable milestone

OLDCODE
    is code no longer used but which we did not yet want to throw away
