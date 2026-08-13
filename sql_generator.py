"""SQL query generation module."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from database import get_schema
from sql_utils import clean_sql_output


def write_sql_query(llm):
    """Create a chain that generates SQL queries from natural language questions."""
    template = """Based on the table schema below, write a SQL query that would answer the user's question:
    {schema}

    Question: {question}
    SQL Query:"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
                "Given an input question, convert it to a SQL query. No pre-amble. "
                "You are working with a SQLite database. "
                "Use only tables and columns that appear in the schema. "
                "CRITICAL: If the question mentions a specific name, value, or entity (e.g. an artist name, a "
                "customer name, a genre, a date), your query MUST include a WHERE clause filtering on that value. "
                "Do not return an unfiltered SELECT over an entire table when the question asks about a specific "
                "entity — that is always wrong. "
                "You may join tables by chaining FOREIGN KEY relationships declared in the schema, even across "
                "multiple joins (e.g. Track -> Album -> Artist). "
                "You must NOT join tables using columns with no declared FOREIGN KEY relationship. "
                "Only return NO_VALID_QUERY if there is truly no way to answer the question from this schema.\n\n"
                "Example:\n"
                "Question: Give some tracks by the artist name Audioslave\n"
                "SQL: SELECT Track.Name FROM Track JOIN Album ON Track.AlbumId = Album.AlbumId "
                "JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE Artist.Name = 'Audioslave'\n\n"
                "Do NOT add LIMIT unless explicitly requested. "
                "Return ONLY the raw SQL query (or NO_VALID_QUERY). No prefix/suffix, no markdown, no label."),
            ("human", template),
        ]
    )

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
        | clean_sql_output
    )
