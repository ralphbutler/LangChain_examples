
import sys, os, json, sqlite3

os.system("rm -f cpd_rxn.db")

conn = sqlite3.connect("cpd_rxn.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS compounds (
        COMPOUND_ID TEXT PRIMARY KEY,
        METACYC TEXT,
        SMILES TEXT,
        INCHI TEXT,
        INCHIKEY TEXT,
        FORMULA TEXT
)
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS reactions (
        REACTION_ID TEXT PRIMARY KEY,
        EC TEXT
)
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS reaction_to_compounds (
        REACTION_ID TEXT,
        COMPOUND_ID TEXT,
        PRIMARY KEY (REACTION_ID, COMPOUND_ID)
)
""")

with open("combined_cpdrxn.jsonl") as infile:
    for line in infile:
        try:
            d = json.loads(line)
        except Exception as error:
            print(line)
            print(error)
            exit(-1)
        if d["ModelSEED ID"].startswith("cpd"):
            if "MetaCyc" not in d  or  "SMILES" not in d  or  "InChI" not in d \
            or "InChIKey" not in d  or  "Formula" not in d:
                continue
            cursor.execute("""
                INSERT INTO compounds (COMPOUND_ID, METACYC, SMILES, INCHI, INCHIKEY, FORMULA)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (d["ModelSEED ID"], d["MetaCyc"], d["SMILES"], 
                  d["InChI"], d["InChIKey"], d["Formula"]) )
        elif d["ModelSEED ID"].startswith("rxn"):
            if "EC" not in d  or  "metabolites" not in d:
                continue
            cursor.execute("""
                INSERT INTO reactions (REACTION_ID, EC)
                VALUES (?, ?)
            """, (d["ModelSEED ID"], d["EC"]) )
            for metabolite in d["metabolites"]:
                cursor.execute("""
                    INSERT INTO reaction_to_compounds (REACTION_ID, COMPOUND_ID)
                    VALUES (?, ?)
                """, (d["ModelSEED ID"], metabolite) )
        else:
            print("UNKNOWN ****", d)
            exit(-1)

conn.commit()
conn.close()
