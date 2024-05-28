from datetime import datetime
import pandas as pd
import sys, rootpath
import time, sys, rootpath, itertools, threading
import psycopg2

import global_function as globfunc
import settings
sys.path.append("".join([rootpath.detect(),"/database/config"]))
from setup_config import setup_service
sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as DBconn
from database import record_buffer as DBrec

# def exist_record_table(tm_record_table, cursor_tmrecord):
#     exist_table_sql = """select exists(select * from information_schema.tables where table_name='{}')""".format(
#         tm_record_table)
    
#     cursor_tmrecord.execute(exist_table_sql)
#     return cursor_tmrecord.fetchone()[0]

def create_tm_record_table(tm_record_table, cursor_tmrecord):
    try:
        create_table_sql = """CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY, name TEXT , generation_time numeric, eng_value numeric, utc TIMESTAMP)""".format(
            tm_record_table)
        # print(create_table_sql)
        cursor_tmrecord.execute(create_table_sql)
    except:
        print("Error while creating {} table in the tm_record database".format(tm_record_table))
    
def mixerQuery(serviceName, tmName, epoch_start, epoch_end): 
    # conn_posg_mixer = ConnectPosg(serviceName)
    # conn_mixer_dw,_ = conn_posg_mixer.database_connection()
    conn_mixer_dw = DBconn(serviceName)
    all_DW_sql = "SELECT name, generation_time, eng_value FROM tm_param_afs WHERE name = \'{}\' AND generation_time BETWEEN {} AND {};".format(tmName, epoch_start, epoch_end)
    # print(all_DW_sql)
    querydata = pd.read_sql(all_DW_sql, conn_mixer_dw)
    # print(querydata)
    conn_mixer_dw.close()
    return querydata

def convertDATE_strTOepoch(str_date):
    date = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
    epoch = int(date.timestamp()*1e9)
    return epoch

def convert_generationtimetoutc(epoch): 
    # epoch = (epoch/1e9).astype(int)
    epoch = int(epoch/1e9)
    # print('epoch')
    date_str = datetime.utcfromtimestamp(
        epoch).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

def all_mixer_to_DataFrame(tmName):
    data_dw = pd.DataFrame(columns=['name', 'generation_time', 'eng_value'])
    print("\nNow, The application is querying the data from mixer dw database")
    DWdate = setup_service('MIXERs_DW_date')
    epoch_start = convertDATE_strTOepoch(DWdate.date_start)
    epoch_end = convertDATE_strTOepoch(DWdate.date_end)
    raw_mixer_data = mixerQuery('MIXERs_DW_db', tmName, epoch_start, epoch_end)
    data_dw = data_dw.append(raw_mixer_data, ignore_index=True)
    # print("---MIXERs_DW_db---")
    # print("exist df = ", data_dw.empty)
    # print(data_dw)
    if raw_mixer_data.empty:
        print("\nWarning!!, no found {} telemetry in mixer dw database".format(tmName))

    print("\nNow, The application is querying the data from mixer 2021 dw database")
    DWdate = setup_service('MIXERs2021_DW_date')
    epoch_start = convertDATE_strTOepoch(DWdate.date_start)
    epoch_end = int(datetime.now().timestamp()*1e9)
    raw_mixer2_data = mixerQuery('MIXERs2021_DW_db', tmName, epoch_start, epoch_end)
    data_dw = data_dw.append(raw_mixer2_data, ignore_index=True)
    # print("---MIXERs2021_DW_db---")
    # print("exist df = ", data_dw.empty)
    # print(data_dw)
    if raw_mixer2_data.empty:
        print("\nWarning!!, no found {} telemetry in mixer dw database".format(tmName))

    # except:
    #     print("Error while query the data from MIXERs 2021")
    # print(data_dw)
    return data_dw

def update_mixer_to_DataFrame(last_time_plus, tmName):
    data_dw = pd.DataFrame(columns=['name', 'generation_time', 'eng_value'])
    epoch_end = int(datetime.now().timestamp()*1e9)
    raw_data = mixerQuery('MIXERs2021_DW_db', tmName, last_time_plus, epoch_end)
    # aviod raw_data is empty dataframe
    if raw_data.empty == False:
        data_dw = data_dw.append(raw_data, ignore_index=True)
    
    return data_dw


def clean_mixer(data_dw):
    # print('Processing clean data')
    data_dw["eng_value"] = pd.to_numeric(data_dw["eng_value"], errors='coerce')
    # delete Nan data
    # print('drop nan')
    data_dw = data_dw.dropna()
    # print(data_dw)
    # delete duplicate generation_time
    # print('drop duplication')
    # data_dw = data_dw.drop_duplicates(subset='generation_time', keep=False)
    data_dw = data_dw.drop_duplicates()
    # print(data_dw)
    # sort genertion time
    # print('sort')
    data_dw = data_dw.sort_values(by=['generation_time'])
    # print(data_dw)
    # reset index
    # print('reset index')
    data_dw.reset_index(inplace=True)
    # print(data_dw)
    # drop index column
    # print('drop index')
    data_dw = data_dw.drop(["index"], axis=1)
    # print(data_dw)
    # print('Clean complete')
    return data_dw

def convert_type(data_dw):
    # print('Processing convert type of dataframe')
    data_dw["generation_time"] = pd.to_numeric(
        data_dw["generation_time"], errors='coerce')
    data_dw["eng_value"] = pd.to_numeric(
        data_dw["eng_value"], errors='coerce')
    # data_dw.dropna(inplace=True)
    return data_dw


# def change_progres_status(cursor_tmrecord, tmName, status_num):
#     search_tmProgres_sql = "SELECT * FROM th1_tmprogress WHERE tmname = \'{}\';".format(tmName)
#     cursor_tmrecord.execute(search_tmProgres_sql)
#     id, _, prog =  cursor_tmrecord.fetchone()
    
#     update_tmProgres_sql = "UPDATE th1_tmprogress SET progress_id = {} WHERE id = {}".format(status_num,id)
#     cursor_tmrecord.execute(update_tmProgres_sql)
    
def search_lastID(cursor_tmrecord, tm_record_table):
    last_id_sql = """select max(id), max(generation_time) from {} ;""".format(tm_record_table)
    cursor_tmrecord.execute(last_id_sql)
    return cursor_tmrecord.fetchone()

def main_db_management():  
    tmName = settings.tm_name
    data_dw = pd.DataFrame()
    tm_record_table = 'record_theos_'+tmName.lower()
    # change_progres = False
    done=False      

    def animation_loading():
        time.sleep(0.5)
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\rProcessing.... ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     ')

    try:
        conn_tmrecord = DBconn("MIXERs2_tm_record_db")
        cursor_tmrecord = conn_tmrecord.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from the tm_record database in the DB record management process : ", error)
        
    else:
        globfunc.clear_console()

        # Check progress id
        check_progressid_sql = "SELECT progress_id FROM th1_tmprogress WHERE tmname = \'{}\'".format(tmName)
        cursor_tmrecord.execute(check_progressid_sql)
        progressid = cursor_tmrecord.fetchone()[0]

        # exist_table = exist_record_table(tm_record_table, cursor_tmrecord)

        # Check exist table
        exist_table_sql = """select exists(select * from information_schema.tables where table_name='{}')""".format(tm_record_table)
        cursor_tmrecord.execute(exist_table_sql)
        exist_table = cursor_tmrecord.fetchone()[0]
        
        if exist_table==False and progressid == 0:
            print("\n{} telemetry have not been imported into the tm_record database".format(tmName))
            print("{} telemetry is being imported into the tm_record database".format(tmName))

            t = threading.Thread(target=animation_loading)
            t.start()
            data_dw = all_mixer_to_DataFrame(tmName)
            done=True

            if data_dw.empty == False:
                data_dw = clean_mixer(data_dw)
                data_dw = convert_type(data_dw)
                data_dw.index += 1

                # change_progres = True
                # update progress id = 1
                if data_dw.empty == False:
                    create_tm_record_table(tm_record_table, cursor_tmrecord)
                    conn_tmrecord.commit()
                    globfunc.updateprogressid(1)
                elif data_dw.empty == True: # if data empty = telemetry cannot be analyzed (progress id=91)
                    globfunc.updateprogressid(91)
                    print("\n{} telemetry cannot be analyzed".format(tmName))
                    settings.passmainmenu = False
            elif data_dw.empty == True:  # if data empty = No record telemetry in MIXERS/MIXERS-II (progress id=90)
                globfunc.updateprogressid(90)
                print("\n{} telemetry be not record telemetry in MIXERS/MIXERS-II".format(tmName))
                settings.passmainmenu = False

        elif exist_table==True and progressid > 0:
            print("\n{} telemetry was imported into the tm_record database".format(tmName))
            last_id, last_time = search_lastID(cursor_tmrecord, tm_record_table)
         
            print("Update the data from mixer 2021 dw to {} table".format(tm_record_table))
            done = False
            t = threading.Thread(target=animation_loading)
            t.start()
            data_dw = update_mixer_to_DataFrame(str(last_time+1), tmName)
            # aviod raw_data is empty dataframe
            if data_dw.empty == False:
                data_dw = clean_mixer(data_dw)
                data_dw = convert_type(data_dw)
                data_dw.index = data_dw.index + last_id + 1

            done=True
        else:
            print('Error while checking {} table in the tm_record database for DB record management process'.format(tm_record_table))
            settings.passmainmenu = False

        if data_dw.empty == False:
            print("{} telemetry is being recorded into the {} table in the tm_record database".format(tmName, tm_record_table))
            done=False
            t = threading.Thread(target=animation_loading)
            t.start()
            data_dw['utc'] = data_dw.apply(
                lambda x: convert_generationtimetoutc(x['generation_time']), axis=1)
            DBrec(conn_tmrecord, cursor_tmrecord, tm_record_table, data_dw)
            done = True  

        # if change_progres:
        #     change_progres_status(cursor_tmrecord, tmName, 1)
        #     conn_tmrecord.commit()

    finally:
        if conn_tmrecord:
            cursor_tmrecord.close()
            conn_tmrecord.close()