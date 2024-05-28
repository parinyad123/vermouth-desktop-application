import psycopg2
import pandas as pd
# from database import database as DB
# from database.database import connect_database as DBconn
# from database import database as db
import sys, rootpath
# sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as DBconn



# print(database)
def updateprogressid(tmName, progid):
    try:
        connect = DBconn('MIXERs2_tm_analysis_db')
        cursor = connect.cursor()

        # search_tmProgres_sql = """SELECT id FROM th1_tmprogress WHERE tmname = \'{}\';""".format(tmName)
        # cursor.execute(search_tmProgres_sql)

        # # prog_list = 
        # for prog in  cursor.fetchall():
        #     print(prog[0])

        # # print(cursor.fetchall())
        
        #     update_tmProgres_sql = "UPDATE th1_tmprogress SET progress_id = {} WHERE id = {}".format(progid,prog[0])
        #     cursor.execute(update_tmProgres_sql)
        #     connect.commit()

        # updateprogressid_sql = "UPDATE th1_tmprogress SET progress_id = {} WHERE tmname = \'{}\'".format(progid,tmName)
        # cursor.execute(updateprogressid_sql)
        # connect.commit()

        # check_progressid_sql = "SELECT progress_id FROM th1_tmprogress WHERE tmname = \'{}\'".format(tmName)
        # cursor.execute(check_progressid_sql)
        # status = cursor.fetchone()[0]
        # print("status = ", status)

        # check = "select count(*) from analysis_info_theos_auto_m1 where tm_name = 'TRXA' and freq = '1D';"
        # cursor.execute(check)
        # status = cursor.fetchone()[0]
        # print("status = ", status)
        # conn_mixer_dw = DBconn('MIXERs2021_DW_db')
        # all_DW_sql = "SELECT name, generation_time, eng_value FROM tm_param_afs WHERE name = \'{}\' AND generation_time BETWEEN {} AND {};".format(tmName, epoch_start, epoch_end)
        # print(all_DW_sql)
        # querydata = pd.read_sql(all_DW_sql, conn_mixer_dw)
        # print(querydata)
        # conn_mixer_dw.close()

        # if status == False:
        #     print("False")
        # elif status == True:
        #     print("True")

        anomalytable_sql = "SELECT anomaly_result_table FROM analysis_info_theos_auto_m1 ;"
        cursor.execute(anomalytable_sql)
        anomalytable = cursor.fetchall()
        print(anomalytable)

    except (Exception, psycopg2.Error) as error:
        print('Error while UPDATE progress', error)
    finally:
        if connect:
            cursor.close()
            connect.close()

if __name__ == "__main__":
    updateprogressid("OMEGA_3", 0)