import sqlite3

conn = sqlite3.connect('cpd_rxn.db')
cursor = conn.cursor()

query = "SELECT * FROM reactions WHERE EC='3.2.1.35' "  # 5 of these

cursor.execute(query)
records = cursor.fetchall()
print("retrieved records for reactions:")
for record in records:
    print(record)
print("-"*50)

#########
query = "SELECT name FROM sqlite_master WHERE type='table'"
cursor.execute(query)
table_names = cursor.fetchall()
print(table_names)  # list of table names
print("-"*50)

# query to select the CREATE TABLE statements
query = "SELECT sql FROM sqlite_master WHERE type='table'"

cursor.execute(query)
table_definitions = cursor.fetchall()
print("Table definitions in CREATE format:")
for table_definition in table_definitions:
    print(table_definition[0])
#########

conn.close()
