# Street-level crime pieline

Pipeline that collect crime data from select sources transforms it and loads to a Postgress DB.

## Architecture

Processing data from the following sources:
 - UK crime API (API call -> raw JSON files -> combined parquet -> loading to Postgres)
 - #### TODO
 
## Setup

1. Prerequsites:

    - Python >= 3.11 with libraries listed in requirements.txt
    - Docker

2. Environmental variables defined in .env file:

| Variable name | Value |
| --- | --- |
| POSTGRES_DB| name of the postgres dabase |
| POSTGRES_USER | username to log into the db |
| POSTGRES_PASSWORD | password |
| POSTGRES_HOST | localhost |
| POSTGRES_PORT  | 5432 or a different free one |
| POSTGRES_SCHEMA | DB schema to interact with |
| UK_CRIMES_TABLE | table name |

3. How to start

- Local:
1. `cd path/to/repo`
2. Set up a .venv:
    - `python -m venv .venv`
    - `.venv\Scripts\activate`
    - `pip install -r requirements.txt`
3. ` pip install -e .` - install the pipeline as a module for consistent imports
4. `docker compose up -d` - start DB
5. python pipeline_uk_crime.py

- Docker:
1. `docker compose --profile apps up` - starts both pipeline and db


## Data sources

 - street-level crimes API by UK police [LINK](https://data.police.uk/docs/method/crime-street/)




