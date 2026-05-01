import os
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def add_contract(self, contract_id, contract_type, jurisdiction):
        query = """
        MERGE (c:Contract {id: $contract_id})
        SET c.type = $contract_type, c.jurisdiction = $jurisdiction
        RETURN c
        """
        with self.driver.session() as session:
            result = session.run(query, contract_id=contract_id, contract_type=contract_type, jurisdiction=jurisdiction)
            return result.single()[0]

    def add_clause(self, contract_id, clause_id, heading, start_offset, end_offset, raw_text):
        query = """
        MATCH (c:Contract {id: $contract_id})
        MERGE (cl:Clause {id: $clause_id})
        SET cl.heading = $heading, cl.start_offset = $start_offset, cl.end_offset = $end_offset, cl.raw_text = $raw_text
        MERGE (c)-[:HAS_CLAUSE]->(cl)
        RETURN cl
        """
        with self.driver.session() as session:
            result = session.run(query, contract_id=contract_id, clause_id=clause_id, 
                                 heading=heading, start_offset=start_offset, end_offset=end_offset, raw_text=raw_text)
            return result.single()[0]

    def add_cross_reference(self, clause_id, referenced_clause_id):
        query = """
        MATCH (cl1:Clause {id: $clause_id})
        MATCH (cl2:Clause {id: $referenced_clause_id})
        MERGE (cl1)-[:REFERENCES]->(cl2)
        """
        with self.driver.session() as session:
            session.run(query, clause_id=clause_id, referenced_clause_id=referenced_clause_id)

    # Useful for tests and wipeout
    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)

neo4j_client = Neo4jClient()
