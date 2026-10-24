import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def check_connection() -> str:
    """Verify the configured Neo4j credentials and selected database."""
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    missing = [
        name
        for name, value in (
            ("NEO4J_URI", uri),
            ("NEO4J_USERNAME", username),
            ("NEO4J_PASSWORD", password),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required Neo4j settings: {', '.join(missing)}")

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 AS ok").single()
            if result is None or result["ok"] != 1:
                raise RuntimeError("Neo4j connection check returned an unexpected result.")
    finally:
        driver.close()

    return "Neo4j connection successful."
