from mysql.connector import Error, pooling
import numpy as np
from private import credentials

MYSQL_CONNECTIONS_COUNT = 7

TABLES = {
        1:"tables_data",
        2:"item_features",
        3:"bayesian_features"
    }


while 1:
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="recommendation_pool",
            pool_size=MYSQL_CONNECTIONS_COUNT,
            pool_reset_session=True,
            **credentials
        )
        print('mysql pool name: ', connection_pool.pool_name, 'mysql pool size: ', connection_pool.pool_size)
        conn = connection_pool.get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {TABLES[1]}")
        _tables_data = cur.fetchone()
        break
    except Error:
        print("MySQL pool failed to initialize")

def get_sql_manager(func):
    def inner(*args, **kwargs):
        try:
            conn, cur = None, None
            conn = connection_pool.get_connection()
            # if conn.is_connected():
            cur = conn.cursor()
            *query, _t = func(*args, **kwargs)
            cur.execute(*query)
            result = cur.fetchall()
            result = np.array(result).astype(_t)
        except Error as err:
            print("Connection to MySQL failed... Retrying...")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        return result
    return inner

def post_sql_manager(func):
    def inner(*args, **kwargs):
        try:
            conn, cur = None, None
            conn = connection_pool.get_connection()
            # if conn.is_connected():
            cur = conn.cursor()
            queries = func(*args, **kwargs)
            for q in queries:
                cur.execute(q)
            conn.commit()
        except Error as err:
            conn.rollback()
            print("Connection to MySQL failed... Retrying...", err)
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        return True
    return inner


class RecommenderDatabase:

    tables_data = None

    tables = None

    def __init__(self) -> None:
        self.tables_data = _tables_data
        self.tables = TABLES
        
    @get_sql_manager
    def get_all_products(self) -> np.ndarray:
        '''
        Query all products from the database (trained and untrained). # it is like we will work with only trained as no available features.
            :returns: the numpy array of all products (items) on the database.
        '''
        return (f"SELECT {','.join([f'i{i+1}' for i in range(self.tables_data[0])])} FROM {self.tables[2]}", np.float32)

    @get_sql_manager
    def get_beta_values(self) -> np.ndarray:
        '''
        Query the bayesian beta ('a' and 'b') for all product's.
            :returns: all the alpha and beta values of products (items) in the database.
        '''
        return (f'SELECT a, b from {self.tables[3]}',np.float64)

    @post_sql_manager
    def update_bayesian_db(self, *queries):
        '''
        updates the items alpha, beta, view count, click count and buy count to the database.
            :param queries: a tuple of queries to update the database.
            :returns: True if successful otherwise False.
        '''
        return queries

    @post_sql_manager
    def update_bayesian_items(self, item_id):
        '''
        Add's products to the database.
            :param item_id: the unique serial number of the product to add to the database.
            :returns: True if successful otherwise False
        '''
        return (f"INSERT INTO bayesian_features(id, a, b, viewCount, clickedCount, added2cartCount, boughtCount) VALUES ({item_id},1, 1, 0, 0, 0, 0)",)

    def get_last_user_id(self) -> int:
        '''
        Query the database for the last user id in the trained database table.
        '''
        return 0
    
    def get_user_features(self, user_id:int) -> list:
        '''
        Query the database for the features of a specific user.
        '''
        return [0, 0]
    

if __name__ == "__main__":
    from private import credentials
    db = RecommenderDatabase()
    a= db.get_beta_values()
    print(a)