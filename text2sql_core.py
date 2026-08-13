import os
from typing import Optional

import torch
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

load_dotenv()

DB_URI = os.getenv("DB_URI", "sqlite:///chinook.db")
MAX_SCHEMA_CHARS = int(os.getenv("TEXT2SQL_MAX_SCHEMA_CHARS", "4000"))
MAX_RESPONSE_CHARS = int(os.getenv("TEXT2SQL_MAX_RESPONSE_CHARS", "2000"))


db = SQLDatabase.from_uri(DB_URI, sample_rows_in_table_info=0)


def get_schema(_):
    return truncate_text(db.get_table_info(), MAX_SCHEMA_CHARS)


def run_query(query):
    print(f"Query being run: {query} \n\n")
    return db.run(query)


def truncate_text(value, max_chars: int = MAX_RESPONSE_CHARS):
    text = value if isinstance(value, str) else str(value)
    return text[:max_chars]


def build_sql_prompt():
    template = """Based on the table schema below, write a SQL query that would answer the user's question:
    {schema}

    Question: {question}
    SQL Query:"""

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Given an input question, convert it to a SQL query. No pre-amble. "
                "You are working with a SQLite database. "
                "Always use SQLite syntax (e.g. LIMIT instead of TOP, no square brackets). "
                "Please do not return anything else apart from the SQL query, no prefix or suffix quotes, no sql keyword, nothing please",
            ),
            ("human", template),
        ]
    )


def build_answer_prompt():
    template = """Based on the SQL query and SQL response below, write a natural language response:

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}"""

    return ChatPromptTemplate.from_messages(
        [
            ("system", "Given an input question and SQL response, convert it to a natural language answer. No pre-amble."),
            ("human", template),
        ]
    )


def get_groq_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )


def get_hf_llm():
    model_id = "Qwen/Qwen2.5-Coder-3B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        device_map="cpu",
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.1,
        do_sample=True,
        return_full_text=False,
    )

    return HuggingFacePipeline(pipeline=pipe)


def get_llm():
    return get_groq_llm()


def write_sql_query(llm):
    return (
        RunnablePassthrough.assign(schema=get_schema)
        | build_sql_prompt()
        | llm
        | StrOutputParser()
    )


def answer_user_query(question, llm: Optional[object] = None):
    llm = llm or get_llm()
    sql_chain = write_sql_query(llm)

    full_chain = (
        RunnablePassthrough.assign(schema=get_schema, query=sql_chain)
        | RunnablePassthrough.assign(response=lambda x: truncate_text(run_query(x["query"])))
        | build_answer_prompt()
        | llm
    )

    return full_chain.invoke({"question": question})


def answer_user_query_with_sql(question, llm: Optional[object] = None):
    llm = llm or get_llm()
    sql_chain = write_sql_query(llm)

    query = sql_chain.invoke({"question": question})
    response = run_query(query)

    answer_chain = build_answer_prompt() | llm
    answer = answer_chain.invoke(
        {
            "question": question,
            "query": query,
            "response": truncate_text(response),
        }
    )

    return {"query": query, "response": response, "answer": answer}
