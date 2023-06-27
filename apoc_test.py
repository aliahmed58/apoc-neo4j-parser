import os
from neo4j import GraphDatabase
import apoc_parser as apoc_parser
import pprint

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("", ""))

with driver.session() as session:
    propeties = "{stream: true}"
    result = session.run(f'CALL apoc.export.json.all(null,{propeties} )') #{label}/
    data = result.data()[0]['data']
    apoc_parser.parse_data_to_json(data)
    

driver.close()