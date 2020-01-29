from os import getenv
import requests
from datetime import datetime

from psycopg2 import OperationalError
from psycopg2.pool import SimpleConnectionPool

# Add data into cloudsql
sql = """
SELECT 
	created_at, stationid, num_bikes_available, num_docks_available
FROM
	divvylivedata
WHERE
	stationid in (%s) AND created_at >= NOW() - INTERVAL '7 DAYS'
;
"""

# TODO(developer): specify SQL connection details
CONNECTION_NAME = getenv(
  'INSTANCE_CONNECTION_NAME',
  'divvy-bike-shari-1562130131708:us-central1:divvyfeed')
DB_USER = getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = getenv('POSTGRES_PASSWORD', 'Mervyn1937')
DB_NAME = getenv('POSTGRES_DATABASE', 'postgres')

pg_config = {
  'user': DB_USER,
  'password': DB_PASSWORD,
  'dbname': DB_NAME
}

# Connection pools reuse connections between invocations,
# and handle dropped or expired connections automatically.
pg_pool = None

def __connect(host):
    """
    Helper function to connect to Postgres
    """
    global pg_pool
    pg_config['host'] = host
    pg_pool = SimpleConnectionPool(1, 1, **pg_config)

def sql_query_parser(raw_cursors):
    return "\n".join(map(lambda cur: ','.join(map(lambda c: str(c), cur)), raw_cursors))

def postgres_query(request):
    """
    Return sql queries upon request
    """
    # request argument
    request_json = request.get_json()
    if request_json:
        stid = request_json.get('stationid', '192')
    else:
        stid = '192'
    
    global pg_pool
    # Initialize the pool lazily, in case SQL access isn't needed for this
    # GCF instance. Doing so minimizes the number of active SQL connections,
    # which helps keep your GCF instances under SQL connection limits.
    if not pg_pool:
        try:
            __connect(f'/cloudsql/{CONNECTION_NAME}')
        except OperationalError:
            # If production settings fail, use local development ones
            __connect('localhost')

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. pg_pool) for later reuse.
    with pg_pool.getconn() as conn:
        cur = conn.cursor()
        cur.execute(sql %(stid))
        results = cur.fetchall()
        pg_pool.putconn(conn)
        return sql_query_parser(results)