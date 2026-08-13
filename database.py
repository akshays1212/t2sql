"""Database utilities module."""

from langchain_community.utilities import SQLDatabase


# Initialize database
db = SQLDatabase.from_uri("sqlite:///Chinook.db", sample_rows_in_table_info=0)


def get_schema(_=None):
    """Get the database schema information."""
    return db.get_table_info()


def run_query(query):
    """Execute a SQL query against the database."""
    print(f'Query being run: {query}\n')
    return db.run(query)
