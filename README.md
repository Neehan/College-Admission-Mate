# College Admission Mate

An MCP (Model Context Protocol) server that exposes a college admissions database to LLMs, enabling AI assistants to answer questions about college admissions across USA, Canada, UK, China, and Japan.

## Features

The server provides two tools:
- `read_schema`: Returns the database schema
- `query_database`: Executes read-only SQL queries against the admissions database

## Coverage

- **USA**: SAT, TOEFL, essays, ECAs
- **Canada**: University requirements and programs
- **UK**: A-Level, IELTS requirements
- **China**: Gaokao requirements
- **Japan**: EJU, entrance exams

## Status

This project is under active development. See [TODOs.md](TODOs.md) for the development roadmap.
