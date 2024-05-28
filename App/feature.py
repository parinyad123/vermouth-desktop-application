from tabnanny import check
from rich.console import Console
from multiprocessing import Process
import rootpath
import sys
import re
import psycopg2
import pandas as pd

import settings
import main_menu
import graph_boundary as gboundary
import graph_frequency as gfrequency
import global_function as glofunc

sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as DBconn
from database import record_buffer as recordbuffer

def call_function(function_name):
    if function_name == 'manage_feature()':
        settings.delete_zero = True
        settings.delzero_dataframe = None

        # current dataframe (delete/Not delete 0 value)
        # global method_boundary, current_boundary, current_rawboundary_dataframe
        settings.method_boundary = "timeofmean"
        settings.current_boundary = 0
        settings.current_rawboundary_dataframe = None

        # show histogram
        # global remove_hist_edge, lower_hist_edge, upper_hist_edge
        settings.remove_hist_edge=True
        settings.lower_hist_edge=0.25
        settings.upper_hist_edge=0.75

        # times of mean boundary
        # global timeofmean, upper_bound_xtime, lower_bound_xtime, mean_cal, timeofmean_dataframe
        settings.timeofmean = 10
        settings.mean_cal = None
        settings.upper_bound_xtime = None
        settings.lower_bound_xtime = None
        settings.timeofmean_dataframe = None
        
        # custom own boundary
        # global upper_bound_own, lower_bound_own, upper_bound_custom, lower_bound_custom, custom_dataframe
        settings.upper_bound_own=.95
        settings.lower_bound_own=.05
        settings.upper_bound_custom = None
        settings.lower_bound_custom = None
        settings.custom_dataframe = None
        
        # --------  frequency  ------------
        # grouph by frequency
        # global frequencies_array, frequencies_dataframe_array, frequency_dataframe
        settings.frequencies_array = ["1H", "4H", "1D"]
        settings.frequencies_dataframe_array = []
        settings.frequency_dataframe = pd.DataFrame()
        
        # show histogram
        # global lower_hist_freq, upper_hist_freq
        settings.lower_hist_freq = 0.25
        settings.upper_hist_freq = 0.75

        # graph feature
        # global feature_frequency, feature_dataframe, feature_tablename
        settings.feature_frequency = "1D"
        settings.feature_dataframe = pd.DataFrame()
        settings.feature_tablename = None
    eval(function_name)

def manage_feature():
    glofunc.clear_console()
    settings.params = glofunc.query_paraminfo('analysis_params_theos_auto_m1')

    console = Console()
    console.print("\nFEATURE\n", justify="center", style="bold")
    glofunc.show_tm_name(settings.tm_name)
    console.print('All Feature', style='light_sea_green')
    glofunc.show_featurelist()

    feature_options = [
        {'label': '📝 Create new Feature', 'func':'create_boundary()'},
        {'label': '⏪ Back to Main Menu', 'func':'main_menu.show_mainmenu()'},
        {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
    ]
    if settings.params:
        feature_options = [
            {'label': '📝 Create new Feature', 'func':'create_boundary()'},
            {'label': '🗑  Delete your Feature', 'func':'delete_feature()'},
            {'label': '⏪ Back to Main Menu', 'func':'main_menu.show_mainmenu()'},
            {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
    ]
    feature_message = "Please choose"

    function = glofunc.select_option(feature_message, feature_options)
    # print(function)
    call_function(function)

def create_boundary():
    if not settings.current_boundary: 
        gboundary.export_tmrecord()
        show_default_graphboundary()
        show_currentboundary("timeofmean")
    process_graphbound = Process(target=gboundary.show_graphboundary,)
    process_graphbound.start()
 
    glofunc.clear_console()
    # print('FreQuency Dataframe ========= ')
    # print(settings.frequency_dataframe)
    console = Console()
    console.print("\nFEATURE\n", justify="center", style="bold")
    console.print("Telemetry name : {}".format(settings.tm_name.upper()))
    console.print("Create new Feature (Create Boundary)")
    console.print("  Your current boundary: [bolt]Default[/] {} (Lower = {}, Upper = {}) \n  Delete zero values: {}\n".format(
                settings.current_boundary['boundary_title'], settings.current_boundary['boundary_lower'], 
                settings.current_boundary['boundary_upper'], settings.current_boundary['zero_value']
    ))
   
    boundary_message = "Please choose"
    boundary_options = [
        {'label': '✅ Confirm selected boundary ({})'.format(settings.current_boundary['boundary_title']), 'func': 'create_frequency("graphfrequency")'},
        {'label': '› Custom your new time of Mean ⛭', 'func': 'custom_boundarybytimeofmean()'},
        {'label': '› Custom your own lower and upper ⛭', 'func': 'custom_boundarybyupperlower()'},
        {'label': '› Change the default boundary ⛭', 'func': 'confirm_selectboundary()'},
        {'label': '• Set the zero values from raw data ⛭', 'func': 'set_zerovaluerawdata()'},
        {'label': '• Change the preview of histogram percentile (Lower: {}, Upper: {}) ⛭'.format(settings.lower_hist_edge*100, settings.upper_hist_edge*100), 'func': 'change_histpercentileboundary()'},
        {'label': '⏪ Back to Manage Feature', 'func': 'manage_feature()'}
        # {'label': '7. Back to Main Menu', 'func':'main_menu.show_mainmenu()'},
    ]
    function = glofunc.select_option(boundary_message, boundary_options)
    # print(function)
    call_function(function) 

def show_currentboundary(method_boundary):
    # print('method_boundary', method_boundary)
    if method_boundary == "timeofmean":
        settings.method_boundary = "timeofmean"
        settings.current_boundary = {"boundary_title": "{} Times of Mean".format(settings.timeofmean),
                            "boundary_lower": '{:.5f}'.format(settings.lower_bound_xtime),
                            "boundary_upper": "{:.5f}".format(settings.upper_bound_xtime),
                            "zero_value": settings.delete_zero}
        settings.frequency_dataframe = settings.timeofmean_dataframe.copy()
    elif method_boundary == "customupperlower":
        settings.method_boundary = "customupperlower"
        settings.current_boundary = {"boundary_title": "Customized Lower and Upper",
                            "boundary_lower": "{:.5f}".format(settings.lower_bound_custom),
                            "boundary_upper": "{:.5f}".format(settings.upper_bound_custom),
                            "zero_value": settings.delete_zero}
        settings.frequency_dataframe = settings.custom_dataframe.copy()

def show_default_graphboundary():
    
    gboundary.delete_zerovalue()

    gboundary.calculate_boundarybytimeofmean()
    settings.timeofmean_dataframe = gboundary.delete_boundary(settings.upper_bound_xtime, settings.lower_bound_xtime)
    
    settings.upper_bound_custom, settings.lower_bound_custom = gboundary.calculate_boundarybyquantile(settings.upper_bound_own, settings.lower_bound_own)
    settings.custom_dataframe = gboundary.delete_boundary(settings.upper_bound_custom, settings.lower_bound_custom)

def custom_boundarybytimeofmean():
    console = Console()
    timeofmean = console.input("[[bold yellow]?[/]] Enter your new times of Mean?: ")
    if timeofmean != "":
        try:
            timeofmean = float(timeofmean)
        except:
            print('\n{} is not Number! Please, enter your new times of Mean again'.format(timeofmean))
            custom_boundarybytimeofmean()
        else:
            if timeofmean <= 0:
                print("\nTimes of Mean must be more then zero.")
                custom_boundarybytimeofmean()

            settings.timeofmean = timeofmean # avoid error converstion
            gboundary.calculate_boundarybytimeofmean()
            settings.timeofmean_dataframe = gboundary.delete_boundary(settings.upper_bound_xtime, settings.lower_bound_xtime)
            show_currentboundary('timeofmean')
    create_boundary()

def custom_boundarybyupperlower():
    def question_upperbound(min,max):
        console = Console()
        upper = console.input("[[bold yellow]?[/]] Enter you own Upper bound (min: {}, max: {})?: ".format(min, max))
        if upper != "":
            try:
                upper = float(upper)
                # print('Upper = ',upper)           
            except:
                print("\n{} is not Number! Please, enter your new own Upper bound again".format(upper))
                question_upperbound()
            else:
                # settings.upper_bound_custom = upper
                return upper
        else:
            return settings.upper_bound_custom

    def question_lowerbound(min,max):
        console = Console()
        lower = console.input("[[bold yellow]?[/]] Enter you own Lower bound (min: {}, max: {})?: ".format(min, max))
        if lower != "":
            try:
                lower = float(lower)
                # print("Lower = ", lower)
            except:
                print("\n{} is not Number! Please, enter your new own Lower bound again".format(lower))
                question_lowerbound()
            else:
                # settings.lower_bound_custom = lower
                return lower
        else:
            return settings.lower_bound_custom

    min = settings.current_rawboundary_dataframe['eng_value'].min()
    max = settings.current_rawboundary_dataframe['eng_value'].max()
    lower = question_lowerbound(min,max)
    upper = question_upperbound(min,max)
    
    # if settings.upper_bound_custom < settings.lower_bound_custom:
    #     settings.upper_bound_custom = lower
    #     settings.lower_bound_custom = upper
    # # print("custom up low ",settings.upper_bound_custom, settings.lower_bound_custom)
    # elif settings.lower_bound_custom == settings.upper_bound_custom:
    #     print("\nUpper and Lower bound should not equal.")
    #     custom_boundarybyupperlower()

    if upper < lower:
        real_upper = lower
        lower = upper
        upper = real_upper
        # settings.upper_bound_custom = lower
        # settings.lower_bound_custom = upper
    # print("custom up low ",settings.upper_bound_custom, settings.lower_bound_custom)
    elif upper == lower:
        print("\Lower: {} and Upper: {} bound should not equal.".format(lower, upper))
        custom_boundarybyupperlower()

    if (upper>max and lower>max) or (upper<min and lower<min):
        print("\Lower: {} and Upper: {} bound is not range of data ({} to {}) ".format(lower, upper, min, max)) 
        custom_boundarybyupperlower()
    
    settings.upper_bound_custom = upper
    settings.lower_bound_custom = lower
    settings.custom_dataframe = gboundary.delete_boundary(settings.upper_bound_custom, settings.lower_bound_custom)
    
    show_currentboundary("customupperlower")
    create_boundary()

def confirm_selectboundary():
    console = Console()
    console.print("Your all boundary",style="bold red")
    console.print("  [bolt]1. {} Times of Mean[/] (Lower = {:.5f}, Upper = {:.5f}) Delete zero values: {}".format(
        settings.timeofmean, settings.lower_bound_xtime, settings.upper_bound_xtime, settings.delete_zero))
    console.print("  [bolt]2. Custom own Lower and Upper[/] (Lower = {:.5f}, Upper = {:.5f}) Delete zero values: {}\n".format(
        settings.lower_bound_custom, settings.upper_bound_custom, settings.delete_zero))

    confirm_message = "Please select to confirm your boundary"
    confirm_options = [
        {"label": "1. {} Times of Mean".format(settings.timeofmean), "func": "show_currentboundary('timeofmean')"},
        {"label": "2. Custom own Lower and Upper", "func": "show_currentboundary('customupperlower')"}
    ]
    function = glofunc.select_option(confirm_message, confirm_options)
    call_function(function)
    create_boundary()
    
def set_zerovaluerawdata():
    setzero_message = "Please select to Delete or No delete the zero values from the raw data"
    setzero_options = [
        {"label": "1. Delete the zero values", "func": "delete_subzerovalues(True)"},
        {"label": "1. No delete the zero values", "func": "delete_subzerovalues(False)"}
    ]
    function = glofunc.select_option(setzero_message, setzero_options)
    call_function(function)
    gboundary.calculate_boundarybytimeofmean()
    settings.timeofmean_dataframe = gboundary.delete_boundary(settings.upper_bound_xtime, settings.lower_bound_xtime)
    settings.custom_dataframe = gboundary.delete_boundary(settings.upper_bound_custom, settings.lower_bound_custom)
    show_currentboundary(settings.method_boundary)
    create_boundary()

def delete_subzerovalues(delete_zero):
        settings.delete_zero = delete_zero
        
        if delete_zero == True:
            settings.current_rawboundary_dataframe = settings.delzero_dataframe.copy()
        elif delete_zero == False:
            settings.current_rawboundary_dataframe = settings.raw_dataframe.copy()

def change_histpercentileboundary():
    def question_upperhistogrambound():
        console = Console()
        histupper = console.input("[[bold yellow]?[/]] Enter your own Upper histogram percentile[0-100]?: ")
        if histupper != "":
            try:
                histupper = float(histupper)/100.0
            except:
                print("\n{} is not Number! Please, enter your new own Upper histogram percentile again".format(histupper))
                question_upperhistogrambound()
            else:
                if histupper > 100 or histupper < 0:
                    print("{} is not between 0 to 100.".format(histupper))
                    question_upperhistogrambound()    
                settings.upper_hist_edge = histupper
                return histupper
        else:
            return settings.upper_hist_edge

    def question_lowerhistogrambound():
        console = Console()
        histlower = console.input("[[bold yellow]?[/]] Enter you own Lower histogram percentile[0-100]?: ")
        if histlower != "":
            try:
                histlower = float(histlower)/100.0
            except:
                print("\n{} is not Number! Please, enter your new own Lower histogram percentile again".format(histlower))
                question_lowerhistogrambound()
            else:
                if histlower > 100 or histlower < 0:
                    print("{} is not between 0 to 100.".format(histlower))
                    question_lowerhistogrambound()
                settings.lower_hist_edge = histlower
                return histlower
        else:
            return settings.lower_hist_edge 

    histlower = question_lowerhistogrambound()
    histupper = question_upperhistogrambound()
    
    if settings.upper_hist_edge < settings.lower_hist_edge:
        settings.upper_hist_edge = histlower
        settings.lower_hist_edge = histupper
    elif settings.upper_hist_edge == settings.lower_hist_edge:
        print("\nLower and Upper histogram percentile should not equal.")
        change_histpercentileboundary()

    create_boundary()

def delete_feature():
    glofunc.clear_console()
    settings.params = glofunc.query_paraminfo('analysis_params_theos_auto_m1')

    console = Console()
    console.print("\nFEATURE\n", justify="center", style="bold")
    console.print("Telemetry name : {}".format(settings.tm_name.upper()))
    # console.print("Delete Feature")
    console.print('All Feature (Delete Feature)', style='light_sea_green')
    glofunc.show_featurelist()

    deletefeature_options = [
        {'label': str(i+1)+'. ' + feature_table[3], 'func':'delete_subfeature('+"\'"+feature_table[3]+"\'"+')'} for i, feature_table in enumerate(settings.params)
    ]
    deletefeature_options.append({'label': str(len(deletefeature_options)+1)+ '. Back to Manage Feature', 'func': 'manage_feature()'})
    # deletefeature_options.append({'label': str(len(deletefeature_options)+2)+ '. Back to Main Menu', 'func': 'main_menu.show_mainmenu()'}) 

    delete_message = "Please select feature do you want to delete"
 
    function = glofunc.select_option(delete_message, deletefeature_options)
    call_function(function)

def delete_subfeature(feature_table):
    delete_rowparamstable_sql = "DELETE FROM analysis_params_theos_auto_m1 WHERE feature_table = '{}'".format(feature_table)
    drop_analysistable_sql = 'DROP TABLE {}'.format(feature_table)
    confirm1_message = "Do you confirm to delete Feature {}".format(feature_table)

    confirm1 = glofunc.confirm_option(confirm1_message)

    if confirm1:
        try:
            connect = DBconn('MIXERs2_tm_analysis_db')
            cursor = connect.cursor()

            checkexistmodel_sql = "SELECT count(*) FROM analysis_info_theos_auto_m1 WHERE feature_table = \'{}\';".format(feature_table)
            cursor.execute(checkexistmodel_sql)
            checkexistmodel = cursor.fetchone()[0]

            if checkexistmodel == True:
                print("\nThe Feature was used to create model. If you want delete the Feature , its Model will also be delete.")
                confirm2_message = "Do you confirm to delete Feature and Model?".format(feature_table)
                confirm2 = glofunc.confirm_option(confirm2_message)

                if confirm2 == True:
                    anomalytable_sql = "SELECT anomaly_result_table FROM analysis_info_theos_auto_m1 WHERE feature_table = \'{}\';".format(feature_table)
                    cursor.execute(anomalytable_sql)
                    anomalytable = cursor.fetchone()[0]

                    delete_rowinfotable_sql = "DELETE FROM analysis_info_theos_auto_m1 WHERE anomaly_result_table = \'{}\'".format(anomalytable) 
                    drop_anomalytable_sql = 'DROP TABLE {}'.format(anomalytable)

                    for i in [delete_rowparamstable_sql, drop_analysistable_sql, delete_rowinfotable_sql, drop_anomalytable_sql]:
                        cursor.execute(i)
                        connect.commit()
                                    
            elif checkexistmodel == False:
                for i in [delete_rowparamstable_sql, drop_analysistable_sql]:
                    cursor.execute(i)
                    connect.commit()

            # update progress id
            countparam_sql = "SELECT count(*) FROM analysis_params_theos_auto_m1 WHERE tm_name = \'{}\'".format(settings.tm_name.upper()) 
            cursor.execute(countparam_sql)
            countparam = cursor.fetchone()[0]
            if countparam == 0:
                glofunc.updateprogressid(1)

        except (Exception, psycopg2.Error) as error:
            print('Error while query: {}:'.format(i), error)
        finally:
            if connect:
                cursor.close()
                connect.close()
    
    manage_feature()

def create_frequency(graph_name):
    glofunc.clear_console()

    if graph_name == "graphfrequency":
        gfrequency.create_frequencydataframe()
        process_graphfrequency = Process(target=gfrequency.show_graphfrequency)
        process_graphfrequency.start()
    elif graph_name == "graphfeature":
        gfrequency.calculate_featuredataframe()
        process_graphfeature = Process(target=gfrequency.show_graphfeature)
        process_graphfeature.start()

    console = Console()
    console.print("\nFEATURE\n", justify="center", style="bold")
    console.print("Telemetry name : {}".format(settings.tm_name.upper()))
    console.print("Create new Feature (Create Frequency)")
    console.print("  You current Frequency : [bolt]Default[/] [bold red]{}[/]".format(settings.feature_frequency))
    console.print("  Select Frequency (Ex: 2D, 30min, 1D)")
    console.print("  [M = month, D = Day, Y = Year, H = Hour, min = minutes, s = second]\n")

    boundary_message = "Please choose"
    boundary_options = [
        {'label': '➊ Preview customized Frequency ⛭', 'func': 'preview_customfrequency()'},
        {'label': '➋ Choose your new Frequency ⛭', 'func': 'choose_newfrequency()'},
        {'label': '✅ Confirm your current frequency', 'func': 'confirm_frequency()'},
        {'label': '•  Change the preview of histogram percentile (Lower: {}, Upper: {}) ⛭'.format(settings.lower_hist_freq*100, settings.upper_hist_freq*100), 'func': 'change_histpercentilefrequency()'},
        {'label': '⏪ Recreate your current Boundary ⛭', 'func': 'create_boundary()'},
        {'label': '⏮  Back to Manage Feature', 'func': 'manage_feature()'}
        # {'label': '6. Back to Main Menu', 'func': 'main_menu.show_mainmenu()'},
    ]
    function = glofunc.select_option(boundary_message, boundary_options)
    # print(function)
    call_function(function)

def check_unitoftime(frequencies_array):
    big_timeunit = ["M", "D", "Y", "H"]
    small_timeunit = ["S", "MIN"]
    freq_array = []

    # print("freq array = ",frequencies_array)

    if frequencies_array == [""]:
        create_frequency("graphfrequency")
    else:
        for fr in frequencies_array:
            temp = re.compile("([0-9]+)([a-zA-Z]+)")
            # print('----> ', fr)
            errorscore = 0
            try:
                res = temp.match(fr).groups()
                freq_int = str(int(res[0]))
                freq_str = str(res[1]).upper()
                for bunit in big_timeunit:
                    if freq_str == bunit:
                        # freq = freq_int+freq_str
                        # print('result = ',freq)
                        freq_array.append(freq_int+freq_str)
                        errorscore += 1
                        break
                for sunit in small_timeunit:       
                    if freq_str == sunit:
                        # freq = freq_int+freq_str.lower()
                        # print('result = ',freq)
                        freq_array.append(freq_int+freq_str.lower())
                        errorscore += 1
                        break
                if errorscore == 0:
                    print("Error because the {} frequency is Wrong!!".format(fr))
                    preview_customfrequency()
             
            except:
                print("Error because the {} frequency is Wrong!!".format(fr))
                preview_customfrequency()

    return freq_array

def preview_customfrequency():
    console = Console()
    frequencies_array = console.input("[[bold yellow]?[/]] Enter Frequencies you want to Preview?: ").replace(" ", "").split(",")
    settings.frequencies_array = check_unitoftime(frequencies_array)
    create_frequency("graphfrequency")

def choose_newfrequency():
    console = Console()
    feature_frequency = console.input("[[bold yellow]?[/]] Enter your new selected Frequency?: ").replace(" ", "").split(",")
    
    if len(feature_frequency) == 1:
        feature_frequency = check_unitoftime(feature_frequency)
        settings.feature_frequency = feature_frequency[0]
        # print(feature_frequency)

        create_frequency("graphfeature")
    else:
        print("Error because the {} frequency is Wrong!!".format(feature_frequency))

        choose_newfrequency()

def confirm_frequency():
    
    confirm_frequencymessage = "Do you confirm to save {} to be your Frequency?".format(settings.feature_frequency) 
    confirm_freq = glofunc.confirm_option(confirm_frequencymessage)
    # print("save model = ",settings.feature_dataframe)
    # print(confirm_freq)
    
    # if settings.feature_dataframe == None:
    if settings.feature_dataframe.empty == True:
        gfrequency.calculate_featuredataframe()

    # process_graphfeature = Process(target=gfrequency.show_graphfeature)
    # process_graphfeature.start()

    if confirm_freq == True:        
        # check exist analysis table 
        settings.feature_tablename = "analysis_theos_{}_{}".format(settings.tm_name.lower(), settings.feature_frequency.lower())
        # exist_analysistable_sql = """SELECT EXISTS (select * from information_schema.tables where table_name='{}')""".format(settings.feature_tablename)
        exist_analysistable_sql = "SELECT COUNT(1) FROM analysis_params_theos_auto_m1 WHERE feature_table = \'{}\';".format(settings.feature_tablename)
        last_idanalysistable_sql = "SELECT max(id) FROM analysis_params_theos_auto_m1"

        record_params_sql = "INSERT INTO analysis_params_theos_auto_m1 \
            (id,tm_name,freq,feature_table,lower_bound,upper_bound,delete_0value)\
            VALUES (%s,%s,%s,%s,%s,%s,%s);"

        create_analysistable_sql = """CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY, utc TIMESTAMP, 
            avg numeric(15,5), std numeric(15,5), count numeric(15,5), min numeric(15,5), max numeric(15,5), 
            q1 numeric(15,5), q2 numeric(15,5), q3 numeric(15,5), 
            skew numeric(15,5), lost_state boolean, epoch_ten numeric, name TEXT);""".format(
                settings.feature_tablename)

        try:
            connect = DBconn('MIXERs2_tm_analysis_db')
            
        except:
            print("Error while check to exist {} telemetry in {}".format(settings.tm_name, settings.feature_frequency))
        else:
            cursor = connect.cursor()
            cursor.execute(exist_analysistable_sql)
            exist_table = cursor.fetchone()[0]
        
        if exist_table == 1:
            confirm_save_analysismesaage = "{} telemetry in {} has been existing, Do you want to replace?".format(settings.tm_name, settings.feature_frequency)
            confirm_save_analysistable = glofunc.confirm_option(confirm_save_analysismesaage)

            if confirm_save_analysistable:
                
                delete_rowparamstable_sql = "DELETE FROM analysis_params_theos_auto_m1 WHERE feature_table = '{}'".format(settings.feature_tablename)
                drop_analysistable_sql = 'DROP TABLE {}'.format(settings.feature_tablename)
                
                try:
                    connect = DBconn('MIXERs2_tm_analysis_db')
                    cursor = connect.cursor()
            
                    cursor.execute(delete_rowparamstable_sql)
                    connect.commit()

                    cursor.execute(drop_analysistable_sql)
                    connect.commit()

                    exist_table = 0

                except (Exception, psycopg2.Error) as error:
                    print('Error while query record analysis table: ', error)
                finally:
                    if connect:
                        cursor.close()
                        connect.close()
            else:
                create_frequency("")

        if exist_table == 0:
            # print(" feature ")
            # print(settings.feature_dataframe)
            settings.feature_dataframe['epoch_ten'] = settings.feature_dataframe.apply(lambda x: glofunc.create_epochten(x['utc']), axis=1)
            settings.feature_dataframe.index += 1 
            settings.feature_dataframe['name'] = settings.tm_name.upper()
               
            # print("feature dataframe")
            # print(settings.feature_dataframe)
            try:
                connect = DBconn('MIXERs2_tm_analysis_db')
                cursor = connect.cursor()

            except (Exception, psycopg2.Error) as error:
                    print('Error while query record analysis table: ', error)

            else:
                cursor.execute(last_idanalysistable_sql)
                last_idanalysistable = cursor.fetchone()
                connect.commit()
                
                record_paras_values = (int(last_idanalysistable[0])+1, settings.tm_name, settings.feature_frequency, 
                            settings.feature_tablename, settings.current_boundary["boundary_lower"],
                            settings.current_boundary["boundary_upper"], settings.current_boundary["zero_value"])
                cursor.execute(record_params_sql, record_paras_values)
                connect.commit()

                cursor.execute(create_analysistable_sql)
                connect.commit()

                recordbuffer(connect, cursor, settings.feature_tablename, settings.feature_dataframe)

                # update progress id
                countinfo_sql = "SELECT count(*) FROM analysis_info_theos_auto_m1 WHERE tm_name = \'{}\'".format(settings.tm_name.upper()) 
                cursor.execute(countinfo_sql)
                countinfo = cursor.fetchone()[0]
                if countinfo == 0:
                    countparam_sql = "SELECT count(*) FROM analysis_params_theos_auto_m1 WHERE tm_name = \'{}\'".format(settings.tm_name.upper()) 
                    cursor.execute(countparam_sql)
                    countparam = cursor.fetchone()[0]
                    if countparam > 0:
                        glofunc.updateprogressid(2)
                    elif countparam == 0:
                        glofunc.updateprogressid(1)

            finally:
                if connect:
                    cursor.close()
                    connect.close()
    else:
        create_frequency("")
    manage_feature()

def change_histpercentilefrequency():
    def question_upperhistogramfreq():
        console = Console()
        histupper = console.input("[[bold yellow]?[/]] Enter your own Upper histogram percentile[0-100]?: ")
        if histupper != "":
            try:
                histupper = float(histupper)/100.0
            except:
                print("\n{} is not Number! Please, enter your new own Upper histogram percentile again".format(histupper))
                question_upperhistogramfreq()
            else:
                if histupper > 100 or histupper < 0:
                    print("{} is not between 0 to 100.".format(histupper))
                    question_upperhistogramfreq()
                settings.upper_hist_freq = histupper
                return histupper
        else:
            return settings.upper_hist_freq

    def question_lowerhistogramfreq():
        console = Console()
        histlower = console.input("[[bold yellow]?[/]] Enter you own Lower histogram percentile[0-100]?: ")
        if histlower != "":
            try:
                histlower = float(histlower)/100.0
            except:
                print("\n{} is not Number! Please, enter your new own Lower histogram percentile again".format(histlower))
                question_lowerhistogramfreq()
            else:
                if histlower > 100 or histlower < 0:
                    print("{} is not between 0 to 100.".format(histlower))
                    question_lowerhistogramfreq()
                settings.lower_hist_freq = histlower
                return histlower
        else:
            return settings.lower_hist_freq

    histlower = question_lowerhistogramfreq()
    histupper = question_upperhistogramfreq()

    if settings.upper_hist_freq < settings.lower_hist_freq:
        settings.upper_hist_freq = histlower
        settings.lower_hist_freq = histupper
    elif settings.upper_hist_freq == settings.lower_hist_freq:
        print("\nUpper and Lower histogram percentile should not equal.")
        change_histpercentilefrequency()

    create_frequency("graphfrequency")

