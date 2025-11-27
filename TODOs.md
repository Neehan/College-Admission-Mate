# College Admission Mate - Development TODOs

## Goal
Create an MCP (Model Context Protocol) server that exposes a college admissions database to LLMs. The server provides two tools:
- `read_schema`: Returns the database schema
- `query_database`: Executes read-only SQL queries

## General Guidelines
- Use Python modules for organization such as `scrapers/`, `db/`, etc
- Use OOP and DRY principles; fail fast and fail early; do not attempt try catch unless required.
- Put all constants in `config/config.yml` and secrets in `.env`
- Use uv or conda for environment management
- Add docstrings to all functions
- **The database user account must have read-only permissions so that the schema and the data cannot be modified.**
- use asyncio
- have an lru cache for mcp tool calls (https://github.com/aio-libs/async-lru)

## Development Steps

1. **Environment Setup**
   - Set up uv/conda environment
   - Install dependencies

2. **PostgreSQL in Docker**
   - Create docker-compose.yml
   - Start PostgreSQL container

3. **Database Schema**
   - Read dbschema.md
   - Create Alembic migrations
   - Run migrations

4. **Data Loading**
   - Research the college admission systems in USA, Canada, UK, China, and Japan. Find out the requirements (SAT, TOEFL, IELTS, A-Level, Gaokao, EJU, entrance exams, essays, ECAs etc. For each country, you can do deep research with both Perplexity and ChatGPT)
   - Find trusted, aggregated data sources for college data for these countries. You can find them in US News, QS Ranking, etc. Download college data for these countries.
   - It's fine not to write scrapers if that adds complexity. For each country at least mention the data source where you downloaded the data from, then process the data to csv files as described in the db schema. 
   - **We will open-source this dataset for future use. So, reproducibility, and citing sources is extremely important.**
   - Load the data into a local database for the rest of the steps.

5. **Create Evaluation**
   - Write 10 representative questions per country (50 total) and expected, correct answers
   - Install the mcp server in Claude Desktop / Cursor and ask the llm to answer the same questions.
   - Create a judge script that compares the expected answer with LLM generated one, and scores for completeness, correctness, relevance.

6. **Implement MCP Server**
   - Write `read_schema` tool
   - Write `query_database` tool (with safety checks)
   - Use config/config.yml for all constants except secrets

7. **Test & Document**
   - Test with Claude Desktop
   - Add README with setup instructions
