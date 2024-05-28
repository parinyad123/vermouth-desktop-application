import os
import sys
import rootpath
import inquirer
import psycopg2
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
from datetime import timezone

import settings

sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as DBconn

sys.path.append("".join([rootpath.detect(),"/App/console/main_menu"]))

clear_console = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def query_paraminfo(table):
    tm_name = settings.tm_name.upper()
    table_sql = f"""SELECT * FROM {table} WHERE tm_name = \'{tm_name}\';"""

    try:
        connect_analysis_db = DBconn('MIXERs2_tm_analysis_db')
        curs = connect_analysis_db.cursor()
        curs.execute(table_sql)
        parinf = curs.fetchall()
        return parinf
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from {} table".format(table), error)
    finally:
        if connect_analysis_db:
            connect_analysis_db.close()
            curs.close()


def show_featurelist():
    console = Console()
    table = Table(box=box.HORIZONTALS,show_header=True, header_style='bold #2070b2')
    table.add_column('', justify='right')
    table.add_column('Feature Name', justify='left')
    table.add_column('Frequency', justify='center')
    table.add_column('Lower Bound', justify='right')
    table.add_column('Upper Bound', justify='right')
    table.add_column('Delete 0 value', justify='center')

    if not settings.params:
        # table.add_row('-', '-','-', '-', '-')
        table.add_row()
    else:
        for n, param in enumerate(settings.params):
            table.add_row(str(n+1),str(param[3]), str(param[2]), str(param[4]), str(param[5]),  str(param[6]))
    
    console.print(table)
    console.print('\n')

def show_modellist():
    console = Console()
    table = Table(box=box.HORIZONTALS,show_header=True, header_style='bold #2070b2')
    table.add_column('', justify='right')
    table.add_column('Model Name', justify='left')
    table.add_column('Feature Name', justify='left')
    table.add_column('Frequency', justify='center')
    table.add_column('Timeline', justify='center')
    table.add_column('Last Updated', justify='right')
    

    if not settings.infoma:
        # table.add_row('-', '-','-', '-', '-')
        table.add_row()
    else:
        for n, inf in enumerate(settings.infoma):
            table.add_row(str(n+1),str(inf[7].split(".")[0]), str(inf[3]), str(inf[2]), 
            str(inf[11])+"-"+str(inf[12])+"\n("+str(inf[13])+" to "+str(inf[14])+")", str(inf[9]))
    
    console.print(table)
    console.print('\n')

def select_option(message, options):
    question = [
    inquirer.List('label',
                message=message,
                choices=[i['label'] for i in options],
            ),
        ]
    label = inquirer.prompt(question)
    # print(label)
    for i in options:
        if i['label'] == label['label']:
            function = i['func']
            # print(function)
    
    return function

def confirm_option(message):
    question = [
        inquirer.Confirm("continue", message=message)
    ]
    answer = inquirer.prompt(question)
    return answer["continue"]

def show_tm_name(tm_name):
    console = Console()
    console.print("Telemetry name : {}".format(tm_name.upper()))

def create_epochten(date_time):
        date_time = datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S')
        epoch = date_time.replace(tzinfo=timezone.utc).timestamp()
        return int(epoch)

def return_towindowapp():
    # clear_console()
    console = Console()
    console.print("Please select new telemetry from TM window...")

def updateprogressid(progid):
    try:
        connect = DBconn('MIXERs2_tm_record_db')
        cursor = connect.cursor()

        updateprogressid_sql = "UPDATE th1_tmprogress SET progress_id = {} WHERE tmname = \'{}\'".format(progid,settings.tm_name.upper())
        cursor.execute(updateprogressid_sql)
        connect.commit()

    except (Exception, psycopg2.Error) as error:
        print('Error while UPDATE progress id', error)
    finally:
        if connect:
            cursor.close()
            connect.close()