# Street-level crime pieline

Pipeline that collect crime data from select sources transforms it and loads to a Postgress DB.

## Architecture

Processing data from the following sources:
 - UK crime API (API call -> raw JSON files -> combined parquet -> loading to Postgres)
 - #### TODO
 
## Setup

1. Prerequsites:

    Python >= 3.11 with libraries listed in requirements.txt

2. Environmental variables defined in .env file:

| Variable name | Value |
| --- | --- |
| DB_NAME | name of the postgres dabase |
| DB_USER | username to log into the db |
| DB_PASSWORD | password |
| DB_HOST | localhost |
| DB_PORT  | 5432 or a different free one |
| DB_SCHEMA | DB schema to interact with |
| UK_CRIMES_TABLE | table name |

3. How to start


Idk help me out here


## Data sources

 - street-level crimes API by UK police [LINK](https://data.police.uk/docs/method/crime-street/)




