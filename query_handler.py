"""Query handling module."""

from database import run_query
from sql_generator import write_sql_query


class RawResponse:
    """Response wrapper for raw SQL output."""
    def __init__(self, content):
        self.content = content


def answer_user_query(query, llm):
    """Answer a user's natural language query by generating and executing SQL."""
    sql_chain = write_sql_query(llm)

    try:
        sql_query = sql_chain.invoke({"question": query})
        print("DEBUG SQL:", repr(sql_query))

        if sql_query.strip().upper() == "NO_VALID_QUERY":
            sql_response = "No valid query could be generated for this question."
        else:
            sql_response = run_query(sql_query)

        # Return the raw SQL response directly to avoid LLM hallucinations
        return RawResponse(sql_response)
    
    except Exception as e:
        print("ERROR in answer_user_query:", repr(e))       
        raise
