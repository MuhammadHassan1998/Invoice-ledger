FROM python:3.12-slim
# dbt-core requires Python <=3.12; 3.13+ breaks mashumaro serialisation

WORKDIR /dbt

RUN pip install --no-cache-dir dbt-duckdb==1.8.1

COPY . .

# Run seed + full model build, then exit.
# The resulting DuckDB file is written to the mounted /data volume.
CMD ["sh", "-c", "dbt seed --profiles-dir . && dbt run --profiles-dir ."]
