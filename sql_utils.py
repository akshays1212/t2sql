"""SQL utilities module."""

import re


def clean_sql_output(text: str) -> str:
    """Clean and validate SQL output from LLM."""
    text = text.strip()
    
    # remove markdown code fences
    text = re.sub(r"^```(?:sql)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    text = text.strip()
    
    # remove a leading "SQL Query:" label if present
    text = re.sub(r"^(sql\s*query\s*:)\s*", "", text, flags=re.IGNORECASE)
    text = text.strip()
    
    # only strip OUTER wrapping quotes if the whole string starts AND ends with the same quote char,
    # and it's not just a SQL string literal ending in a quote (e.g. WHERE x = 'foo')
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"', '`'):
        # heuristic: a wrapped SQL query won't have that quote char appear again inside meaningfully,
        # or more reliably — check it's not a normal SQL statement (starts with SELECT/WITH/etc.)
        if not re.match(r"^\s*(SELECT|WITH|INSERT|UPDATE|DELETE)\b", text[1:-1], flags=re.IGNORECASE):
            pass  # ambiguous, leave as-is rather than risk corrupting valid SQL
        else:
            text = text[1:-1].strip()
    
    if text.upper().startswith("NO_VALID_QUERY"):
        return "NO_VALID_QUERY"
    
    return text.strip()
