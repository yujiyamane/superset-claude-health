FROM apache/superset:5.0.0
USER root
RUN pip install psycopg2-binary flask-cors --target=/app/.venv/lib/python3.10/site-packages/
USER superset
