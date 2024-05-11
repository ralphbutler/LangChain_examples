
rm -rf data/*     # start over

docker run \
    --rm -it \
    -p 7474:7474 -p 7687:7687 \
    -v $PWD/data:/data -v $PWD/plugins:/plugins \
    --name neo4j-apoc \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4J_PLUGINS=\[\"apoc\"\] \
    -e NEO4J_AUTH=neo4j/foobar_neo4j \
    neo4j

#     -e NEO4J_dbms_security_procedures_unrestricted=gds.* \
# dbms.security.procedures.unrestricted=gds.*
# -e NEO4J_dbms_security_procedures_unrestricted=algo\.\* \

# chrome http://localhost:7474
