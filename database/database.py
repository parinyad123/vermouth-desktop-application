import psycopg2
from psycopg2 import Error
from io import StringIO
import rootpath 

from config.setup_config import setup_service

def connect_database(serviceName):
    conf = setup_service(serviceName)
    hosts = conf.hosts
    databases = conf.databases
    users = conf.users
    passwords = conf.passwords
    ports = conf.ports
   
    try:
        connect = psycopg2.connect(
            host=hosts,
            database=databases,
            user=users,
            password=passwords,
            port=ports
        )

        return connect

    except (Exception, Error) as error:
        print("Error ",  error)

def record_buffer(connect, cursor, table_tmName, data_df):
    buffer = StringIO()
    data_df.to_csv(buffer, index_label="id", header=False)
    buffer.seek(0)
    try:
        cursor.copy_from(buffer, table_tmName, sep=",")
        connect.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while The data is being recorded into {} table in database".format(table_tmName))
        print("Error : {}".format(error))
        connect.rollback()
        return 1

# def send_ordersql(serviceName, ordersql, recordvalue, errormessage):
#     try:
#         connect = connect_database(serviceName)
#         cursor = connect.cursor()

#         if recordvalue is None:
#             cursor.execute(ordersql)
#         else:
#             cursor.execute(ordersql, recordvalue)
        
#         connect.commit() 

#     except (Exception, psycopg2.Error) as error:
#         print(errormessage, error)
#     finally:
#         if connect:
#             cursor.close()
#             connect.close()

def order_query(serviceName, ordersql_list):
    try:
        connect = connect_database(serviceName)
        cursor = connect.cursor()

        for i in ordersql_list:
            cursor.execute(i)
            connect.commit()

    except (Exception, psycopg2.Error) as error:
        print('Error while query : {}:'.format(i), error)
    finally:
        if connect:
            cursor.close()
            connect.close()

if __name__ == "__main__":
    print("".join([rootpath.detect(),""]))
    ss = connect_database('MIXERs2_tm_record_db')
    print(ss)