from os import getenv
import requests
from datetime import datetime

from psycopg2 import OperationalError
from psycopg2.pool import SimpleConnectionPool

# Divvy Feed link
DIVVY_URL = 'https://gbfs.divvybikes.com/gbfs/en/station_status.json'

# Add data into cloudsql
sql = """
INSERT INTO divvylivedata (
    last_updated,
    last_reported,
    stationid,
    num_bikes_available,
    num_docks_available,
    num_ebikes_available,
    num_bikes_disabled,
    num_docks_disabled,
    is_installed,
    is_renting, 
    is_returning
)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

# specify SQL connection details
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

# query live divvy station status data from divvy json feed
def get_live_divvy_data():
    # query data from divvy feeds
    res = requests.get(DIVVY_URL)
    
    # serialize data
    jsonres = res.json()
    
    # prepare data
    lst_updt = datetime.utcfromtimestamp(int(jsonres['last_updated'])).strftime('%Y-%m-%d %H:%M:%S')
    
    output_lst = []
    for station_dict in jsonres['data']['stations']:
        try:
            lst_rprt = datetime.utcfromtimestamp(int(station_dict['last_reported'])).strftime('%Y-%m-%d %H:%M:%S')
            stid = int(station_dict['station_id'])
            
            nba = int(station_dict['num_bikes_available'])
            nda = int(station_dict['num_docks_available'])
            nea = int(station_dict['num_ebikes_available'])
            nbd = int(station_dict['num_bikes_disabled'])
            ndd = int(station_dict['num_docks_disabled'])
            
            ifinstl = bool(int(station_dict['is_installed']))
            ifrent = bool(int(station_dict['is_renting']))
            ifrtrn = bool(int(station_dict['is_returning']))
            
            output_lst.append((lst_updt, lst_rprt, stid,
                               nba, nda, nea, nbd, ndd,
                               ifinstl, ifrent, ifrtrn))
            
        except (ValueError, KeyError):
            continue
    
    return output_lst

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


def feed_live_divvydata(request):
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
        divvy_data_lst = get_live_divvy_data()
        cur.executemany(sql, divvy_data_lst)
        conn.commit()
        pg_pool.putconn(conn)
        return str("Number of rows updated: {}\nLast update time: {}".format(len(divvy_data_lst), divvy_data_lst[0][0]))
