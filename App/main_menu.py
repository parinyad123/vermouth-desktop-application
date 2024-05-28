import time
import py
from rich.console import Console
import sys

import settings
# from feature import *
import feature
import model
import global_function as glofunc
from db_record_management import main_db_management

def call_function(function_name):
    eval(function_name)

def show_mainmenu():
    settings.init()
    settings.tm_name = sys.argv[1]
    # print("argv = ", sys.argv)
    # print("--- IN main menu ----") 
    main_db_management()
    time.sleep(.5) # aviod print 'Done' in main_DB_record_management.py

    if settings.passmainmenu:
        glofunc.clear_console()

        # get data params and info table database as $tm_name
        settings.params = glofunc.query_paraminfo('analysis_params_theos_auto_m1')
        settings.infoma = glofunc.query_paraminfo('analysis_info_theos_auto_m1')

        console = Console()

        console.print("\nMAIN MENU\n", justify="center", style="bold")
        glofunc.show_tm_name(settings.tm_name)
        console.print("You are in step: 1 (already create feature)\n")

        console.print('1. All Feature', style='light_sea_green')
        glofunc.show_featurelist()

        console.print('2. All Model', style='light_sea_green')
        glofunc.show_modellist()

        mainmenu_options = [
            {'label': '➊  Manage Feature', 'func':'feature.manage_feature()'},
            {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
        ]
        if settings.params:
            # mainmenu_options.append({'label': '2. Manage Model', 'func':'manage_model()'})
            mainmenu_options = [
                {'label': '➊  Manage Feature', 'func':'feature.manage_feature()'},
                {'label': '➋  Manage Model', 'func':'model.manage_model()'},
                {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
        ]

        mainmenu_message = "Please choose"

        function = glofunc.select_option(mainmenu_message, mainmenu_options)
        # eval(function)+
        
        call_function(function)
        # print(function)
    else:
        print("____ return to window ______")
        glofunc.return_towindowapp()


if __name__ =="__main__":
    show_mainmenu()