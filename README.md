# 🗄️ t2sql: Text-to-SQL on the Chinook Database

An AI-powered **Text-to-SQL** converter that translates natural language questions into executable SQL queries against the **Chinook** digital media store database using Large Language Models (LLMs).

---

## 📌 Overview

Querying databases often requires knowledge of SQL syntax and complex schema relationships. **`t2sql`** bridges this gap by allowing non-technical users to ask questions in plain English and automatically receiving accurate, structured SQL queries along with their execution results.

This project uses the **Chinook Sample Database**, which models a digital media store (including tracks, albums, artists, customers, employees, and invoices).

---

## ✨ Features

* **Natural Language Processing:** Translates complex English prompts into valid SQL statements.
* **Schema-Aware Prompting:** Automatically injects Chinook's relational context (tables, foreign keys, data types) to reduce hallucinations.
* **Multi-Table Joins & Aggregations:** Accurately builds queries involving `JOIN`, `GROUP BY`, `ORDER BY`, `HAVING`, and subqueries.
* **Database Execution:** Executes the generated query on `chinook.db` and displays the query result in real time.
* **SQL Validation:** Checks generated SQL for syntax correctness prior to execution.

---

## 📊 Chinook DB Schema Overview

The Chinook database simulates a media store and contains 11 main tables:
