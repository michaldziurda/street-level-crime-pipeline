select schemaname as table_schema,
       relname as table_name,
       pg_size_pretty(pg_relation_size(relid)) as data_size
from pg_catalog.pg_statio_user_tables
order by pg_relation_size(relid) desc;

select schemaname, relname, pg_size_pretty(pg_relation_size(relid)) from pg_catalog.pg_statio_user_tables;



set search_path to db;


\pset columns 5;

psql -U pipeline_user -d pipeline_db