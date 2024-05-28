from logging import critical
from rich.console import Console
from multiprocessing import Process
from datetime import datetime
import rootpath
import sys
import os
import re
import psycopg2
import pandas as pd
import numpy as np
from ftplib import FTP
import torch
from torch import nn
from torch.autograd import Variable
import logging
handler = logging.basicConfig(level=logging.INFO)
lgr = logging.getLogger(__name__)

import settings
import main_menu
import graph_boundary as gboundary
import graph_frequency as gfrequcncy
import graph_model as gmodel
import global_function as glofunc
from models.model_auto_m1 import autoencoder
sys.path.append("".join([rootpath.detect(),"/database/config"]))
from setup_config import setup_service

sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as DBconn
from database import record_buffer as recordbuffer

def call_function(function_name):
    if function_name == 'manage_model()':
        settings.previewfeature_dataframe = None

        # -------- process detial ----------
        # global model_feature, createnewmodel, model_freq
        settings.model_feature = None
        settings.createnewmodel = True
        settings.model_freq = None 

        # --------- create model ------------
        # global avgfeature_dataframe, train_startpoint, train_endpoint, train_startdate, train_enddate
        settings.avgfeature_dataframe = None
        settings.train_startpoint = None
        settings.train_endpoint = None
        settings.train_startdate = None
        settings.train_enddate = None

        # --------- split train/test data -----
        # global dataset, train_data, test_data
        settings.train_data = None
        settings.test_data = None
        settings.dataset = None

        # --------- normalization ---------
        # global transform_method, max_value, min_value
        settings.transform_method = None
        settings.max_value = None
        settings.min_value = None

        # --------- rolling window --------
        # global look_back, rollingwindow_data_X
        settings.look_back = 10
        settings.rollingwindow_data_X = None

        # --------- train model ---------
        # global use_cuda, learingrate, trainmodel_epoch, model, optimizer
        settings.use_cuda = False
        settings.learingrate = 0.001
        settings.trainmodel_epoch = 500
        settings.model = None
        settings.optimizer = None

        # --------- recostruct ---------
        # global real, reco, diff, model_loss
        settings.real = None
        settings.reco = None
        settings.diff = None
        settings.model_loss = None

        # --------- EWMA --------
        # global ewma_method, ewma_weight, ewma_mean, ewma_std, anomaly_level
        settings.ewma_method = True
        settings.ewma_weight = 10
        settings.ewma_mean = None
        settings.ewma_std = None
        settings.anomaly_level = []

        # --------- select anomaly level ----
        # global selectanomaly_list, selectanomaly_lelvel
        settings.selectanomaly_list = []
        settings.selectanomaly_lelvel = []
        
        # --------- anomaly dataset -------
        # global anomalystate_dataframe, resultanomaly_dataframe
        settings.anomalystate_dataframe = None
        settings.resultanomaly_dataframe = None

        # --------- save model --------
        # global table_info, algorithm_name, model_name, model_address, anomaly_tablename, algorithm_path, model_address, nowdate
        settings.table_info = None
        settings.algorithm_name = None
        settings.model_name = None
        settings.model_address = None
        settings.anomaly_tablename = None
        settings.algorithm_path = None
        settings.model_address = None
        settings.nowdate = None

        # -------- Retrain model -------
        # global model_id
        settings.model_id = None

        # -------- preview result anomaly detection -----
        # global previewresult_dataframe 
        settings.previewresult_dataframe = None

    eval(function_name)

def manage_model():
    glofunc.clear_console()

    # get data params and info table database as $tm_name
    settings.params = glofunc.query_paraminfo('analysis_params_theos_auto_m1')
    settings.infoma = glofunc.query_paraminfo('analysis_info_theos_auto_m1')

    console = Console()

    console.print("\nMODEDL\n", justify="center", style="bold")
    glofunc.show_tm_name(settings.tm_name)
    console.print("You are in step: 2 (already create model)\n")

    console.print('1. All Feature', style='light_sea_green')
    glofunc.show_featurelist()

    console.print('2. All Model', style='light_sea_green')
    glofunc.show_modellist()

    mainmenu_options = [
        {'label': '•  Preview Graph of your Feature ⛭', 'func':'preview_graphfeature()'},
        {'label': '📝 Create new Model ⛭', 'func':'create_newmodel()'},
        # {'label': '3. Delete your Model', 'func':'delete_model()'},
        {'label': '⏪ Back to Main Menu', 'func':'main_menu.show_mainmenu()'},
        {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
    ]
    if settings.infoma:
        mainmenu_options = [
            {'label': '•  Preview Graph of your Feature ⛭', 'func':'preview_graphfeature()'},
            {'label': '📝 Create new Model ⛭', 'func':'create_newmodel()'},
            {'label': '🔄 Retrain your Model ⛭', 'func':'recreate_model()'},
            {'label': '•  Preview Graph of your result Model ⛭', 'func':'preview_graphanomalydetection()'},
            {'label': '🗑  Delete your Model', 'func':'delete_model()'},
            {'label': '⏪ Back to Main Menu', 'func':'main_menu.show_mainmenu()'},
            {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
    ]
    param_featurelist = [p[3] for p in settings.params]
    infom_featurelist = [i[3] for i in settings.infoma]
    param_featurelist.sort()
    infom_featurelist.sort()
    if settings.infoma and (param_featurelist == infom_featurelist):
        mainmenu_options = [
            {'label': '•  Preview Graph of your Feature ⛭', 'func':'preview_graphfeature()'},
            # {'label': '2. Create new Model', 'func':'create_newmodel()'},
            {'label': '📝 Retrain your Model ⛭', 'func':'recreate_model()'},
            {'label': '•  Preview Graph of your result Model ⛭', 'func':'preview_graphanomalydetection()'},
            {'label': '🗑  Delete your Model', 'func':'delete_model()'},
            {'label': '⏪ Back to Main Menu', 'func':'main_menu.show_mainmenu()'},
            {'label': '📡 Select new Telemetry', 'func':'glofunc.return_towindowapp()'}
    ]
    mainmenu_message = "Please Feature"
    function = glofunc.select_option(mainmenu_message, mainmenu_options)    
    call_function(function)

def preview_graphfeature():
    gboundary.export_tmrecord()
    preiewfeature_message = "Please select your Feature to Preview"
    previewfeature_options = [
        {'label': str(i+1)+'. ' + feature_table[3], 'func':'preview_subgraphfeature('+"\'"+feature_table[3]+"\'"+')'} for i, feature_table in enumerate(settings.params)
    ]
    # previewfeature_options.append({'label': str(len(previewfeature_options)+1)+'. exit', 'func': 'manage_model()'})

    function = glofunc.select_option(preiewfeature_message, previewfeature_options)
    # print(function)
    call_function(function)

# def export_tmanalysis(feature_tablename):
#     feature_sql = "SELECT * FROM {};".format(feature_tablename)
#     try:
#         connect = DBconn('MIXERs2_tm_analysis_db')
#         settings.feature_dataframe = pd.read_sql(feature_sql, connect)

#     except (Exception, psycopg2.Error) as error:
#         print('Error while query: {}:'.format(feature_sql), error)
#     finally:
#         if connect:
#             connect.close()
    
def preview_subgraphfeature(feature_tablename):
    # export_tmanalysis(feature_tablename)
    feature_sql = "SELECT * FROM {};".format(feature_tablename)
    try:
        connect = DBconn('MIXERs2_tm_analysis_db')
        settings.feature_dataframe = pd.read_sql(feature_sql, connect)

    except (Exception, psycopg2.Error) as error:
        print('Error while query: {}:'.format(feature_sql), error)
    finally:
        if connect:
            connect.close()
    # filter param's feature_tablename == feature_tablename that user select
    for param in settings.params:
        if param[3] == feature_tablename:
            break
    temp = re.compile("([0-9]+)([a-zA-Z]+)")
    res = temp.match(param[2]).groups()
    unit = res[1]
    if unit != 'min':
        unit = unit.upper()
    settings.feature_frequency = res[0]+unit       

    if param[6] == True:
       gboundary.delete_zerovalue() 
    settings.current_rawboundary_dataframe = gboundary.delete_boundary(param[5], param[4])

    process_graphfeature = Process(target=gfrequcncy.show_graphfeature)
    process_graphfeature.start()

    manage_model()

def create_newmodel():
    gboundary.export_tmrecord()

    # filter freature != model
    featuretable_list = [f[3] for f in settings.params]
    for m in settings.infoma:
        for f in featuretable_list:
            if m[3] == f:
                featuretable_list.remove(f)
    selectfeature_message = "Please select your Feature for your new Model"
    
    selectfeature_options = [
        # {'label': str(i+1)+'. ' + feature_table[3], 'func':'select_traindata('+"\'"+feature_table[3]+"\'"+')'} for i, feature_table in enumerate(settings.params)
        {'label': str(i+1)+'. '+featuretable, 'func':"select_traindata(\'"+featuretable+"\')"} for i, featuretable in  enumerate(featuretable_list)
    ]

    function = glofunc.select_option(selectfeature_message, selectfeature_options)
    # print(function)
    settings.model_feature  = function.split("'")[1]
    settings.model_freq = settings.model_feature.split("_")[-1].upper()
    
    # for p in settings.params:
    #     if p[3] == settings.model_feature:
    #         settings.createmodel_title = 'Create new Model'
    #         settings.model_freq = p[2]
    #         break
    
    # print(function.split("'")[1])
    # print(p)
    # print(settings.createmodel_title, settings.model_feature, settings.model_freq)
    call_function(function)

def recreate_model():
    settings.createnewmodel = False # change create new model status
    selectfeature_message = "Please select your Feature for Retrain Model"
    selectfeature_options = [
        # {'label': str(i+1)+'. '+featuretable[3], 'func':"select_traindata(\'"+featuretable[3]+"\')"} for i, featuretable in enumerate(settings.infoma)
        {'label': str(i+1)+'. '+info[3], 'func':str(info[0])+","+info[3]+","+info[2]} for i, info in enumerate(settings.infoma)
    ]
    info = glofunc.select_option(selectfeature_message, selectfeature_options)
    # settings.model_feature  = function.split("'")[1]
    # settings.model_freq = settings.model_feature.split("_")[-1].upper()

    # search id from model
    # for info in settings.infoma:
    #     if info[3] == settings.model_feature:
    #         settings.model_id = info[0]
    #         break
    # print(function, settings.model_id, info)
    info = info.split(",")
    settings.model_id = int(info[0])
    settings.model_feature = info[1]
    settings.model_freq = info[2]
    function = "select_traindata('{}')".format(settings.model_feature)
    # print("function == retian ", function)
    call_function(function)

def select_traindata(feature_tablename):
    feature_sql = "SELECT id, name, utc, epoch_ten, avg FROM {};".format(feature_tablename)
    try:
        connect = DBconn('MIXERs2_tm_analysis_db')
        settings.avgfeature_dataframe = pd.read_sql(feature_sql, connect)

    except (Exception, psycopg2.Error) as error:
        print('Error while query: {}:'.format(feature_sql), error)
    finally:
        if connect:
            connect.close()

    process_graphselecttraindata = Process(target=gmodel.show_graphselecttraindata)
    process_graphselecttraindata.start()

    lentraindata = len(settings.avgfeature_dataframe)

    def select_starttrainpoint():
        console = Console()
        startpoint = console.input("[[bold yellow]?[/]] Enter your Training point[1-{}]: Start?: ".format(lentraindata))
        try:
            startpoint = int(startpoint)
            if startpoint == 0:
                startpoint = 1
        except:
            print("\n{} is not Number (1-{})! Please, enter your new train Start point again".format(startpoint, lentraindata))
            select_starttrainpoint()
        else:
            settings.train_startpoint = startpoint
            return startpoint

    def select_endtrainpoint():
        console = Console()
        endpoint = console.input("[[bold yellow]?[/]] Enter your Training point[1-{}]: End?: ".format(lentraindata))
        try:
            endpoint = int(endpoint)
            if endpoint == 0:
                endpoint = 1
        except:
            print("\n{} is not Number (1-{})! Please, enter your new train End point again".format(endpoint, lentraindata))
            select_endtrainpoint()
        else:
            settings.train_endpoint = endpoint
            return endpoint

    startpoint = select_starttrainpoint()
    endpoint = select_endtrainpoint()

    if settings.train_endpoint < settings.train_startpoint:
        settings.train_startpoint = endpoint
        settings.train_endpoint = startpoint

    settings.train_startdate = settings.avgfeature_dataframe['utc'][settings.train_startpoint-1]
    settings.train_enddate = settings.avgfeature_dataframe['utc'][settings.train_endpoint-1]

    print(settings.train_startpoint, settings.train_endpoint)
    print(settings.train_startdate, settings.train_enddate)

    settings.dataset = settings.avgfeature_dataframe['avg'].values.astype('float32')
    settings.train_data = settings.dataset[settings.train_startpoint-1:settings.train_endpoint-1]
    settings.test_data = settings.dataset[settings.train_endpoint-1:]

    # Normolization
    settings.max_value = np.max(settings.train_data)
    settings.min_value = np.min(settings.test_data)
    scalar = settings.max_value - settings.min_value
    settings.dataset = list(map(lambda x: (x - settings.min_value)/scalar, settings.dataset))
    settings.train_data = list(map(lambda x: (x - settings.min_value)/scalar, settings.train_data))
    settings.test_data = list(map(lambda x: (x - settings.min_value)/scalar, settings.test_data))

    # create_rollingwindow(settings.train_data)
    train_model()

def create_rollingwindow(dataset):
    # Rolling window
    settings.rollingwindow_data_X = []
    for i in range(len(dataset) - settings.look_back):
        datarw = dataset[i:(i+settings.look_back)]
        settings.rollingwindow_data_X.append(list(datarw)) 
    settings.rollingwindow_data_X = np.array(settings.rollingwindow_data_X)
    settings.rollingwindow_data_X = settings.rollingwindow_data_X.reshape(-1,1,settings.look_back)

def calculate_anomalyscore(train_x, model):
    # Prediction
    var_data = Variable(train_x)
    pred_train = model(var_data)
    pred_train = pred_train.view(-1, settings.look_back).data.cpu().numpy()

    # Reconstruct train_x and pred_train to become real and reco
    # Create real data by using train_x
    data = train_x.view(-1, settings.look_back).data.cpu().numpy()
    settings.real = np.append(data[:,1], data[len(data)-1])
    # print('data --- ', len(data))
    # print(data)
    # print("rel ---", len(settings.real))
    # print(settings.real)
    
    # Create reconsturct data (reco) by using pred_train
    reco = np.append(pred_train[:,1], pred_train[len(pred_train)-1])
    # print("reco---", len(reco))
    # print(reco)
    reco = np.insert(reco, 0, reco[0])
    # print("reco insert --", len(reco))
    # print(reco)
    settings.reco = np.delete(reco, len(reco)-1)
    # print("reco delect --", len(settings.reco))
    # print(settings.reco)
    # Create score (diff)
    settings.diff = np.abs(np.subtract(settings.real,settings.reco))

def reselect_anomalylevel():
    process_graphreconstruct = Process(target=gmodel.show_graphreconstruct)
    process_graphreconstruct.start()
    settings.selectanomaly_list = [0]
    console = Console()
    console.print("Please enter 3 Anomaly Levels from 1 to 10")
    for line in ['1st', '2nd', '3rd']:
        passed = 0
        while passed == 0:
            levelinput = console.input("[[bold yellow]?[/]] Enter {} anomaly level [1-10]?: ".format(line))

            # Check number
            try: 
                levelinput = int(levelinput)
                checknum = True
            except:
                print("{} is not Number!.".format(levelinput))
                checknum = False
                checkrate = False

            # Check rate
            if checknum:
                checkrate = 0 < levelinput and 11 > levelinput
                if checkrate==False:
                    print("{} is not between 1 to 10.".format(levelinput))
            
            # Check duplicate
            if checkrate and checknum:
                if levelinput not in settings.selectanomaly_list:
                    settings.selectanomaly_list.append(levelinput) 
                    passed = 1
                else:
                    print("{} is duplicate.".format(levelinput))

    settings.selectanomaly_list.remove(0)
    settings.selectanomaly_list.sort()
    settings.selectanomaly_lelvel = [settings.anomaly_level[i-1] for i in settings.selectanomaly_list]

    create_rollingwindow(settings.dataset)

    if settings.use_cuda:
        dataset_x = torch.from_numpy(settings.rollingwindow_data_X).float().cuda()
    else:
        dataset_x = torch.from_numpy(settings.rollingwindow_data_X).float()

    calculate_anomalyscore(dataset_x, settings.model.eval())

    # create anomaly status dataframe
    # settings.diff = np.insert(settings.diff, 0, 0)
    # settings.diff = np.delete(settings.diff, len(settings.diff)-1)
    data = {'real':settings.real, 'score':settings.diff}
    anomalystate_dataframe = pd.DataFrame(data=data)
    anomalystate_dataframe['anomaly_state'] = anomalystate_dataframe.apply(lambda x:  0 if x['score']<settings.selectanomaly_lelvel[0] else (1 if x['score']<settings.selectanomaly_lelvel[1] else (2 if x['score']<settings.selectanomaly_lelvel[2] else 3)), axis=1)
    anomalystate_dataframe['id'] = anomalystate_dataframe.index
    settings.anomalystate_dataframe = anomalystate_dataframe.copy()

    process_graphanomalydetection = Process(target=gmodel.show_graphanomalydetection)
    process_graphanomalydetection.start()

    confirmanomalyresult_message = "\nDo you confirm the result of anomaly detection"
    confirm_anomalyresult = glofunc.confirm_option(confirmanomalyresult_message)

    if confirm_anomalyresult:
        confirmsavemodel_message = "Do you save model and result of anomaly detection"
        confirm_savamodel = glofunc.confirm_option(confirmsavemodel_message)
        if confirm_savamodel:
            save_anomalydetection()
    else:
        retrian_message = "Please select:"
        retrain_options = [
                {'label': '🔁 Retrain ⛭', 'func': 'train_model()'},
                {'label': '◀ Back to select 3 Anomaly Levels again ⛭', 'func': 'reselect_anomalylevel()'},
                {'label': '⏪ Back to custom Training points again ⛭', 'func': 'select_traindata("{}")'.format(settings.model_feature)},
                {'label': '⏮ Back to Manage Model', 'func': 'manage_model()'}
        ]
        function = glofunc.select_option(retrian_message, retrain_options)
        call_function(function)
  

def train_model():
    create_rollingwindow(settings.train_data)

    glofunc.clear_console()
    console = Console()
    console.print("\nMODEDL\n", justify="center", style="bold")
    glofunc.show_tm_name(settings.tm_name)
    console.print("You are in step: 2 (Training Model)\n")
    # console.print("{} of {} telemetry in {} frequency".format(settings.createmodel_title, settings.tm_name, settings.model_freq))
    console.print("Training Model report by using [bold green]{}[/] feature:\n".format(settings.model_feature))

    
    if settings.use_cuda:
        train_x = torch.from_numpy(settings.rollingwindow_data_X).float().cuda()
    else:
        train_x = torch.from_numpy(settings.rollingwindow_data_X).float()

    settings.model = autoencoder(settings.look_back)

    criterion = nn.MSELoss()
    settings.optimizer = torch.optim.Adam(settings.model.parameters(), lr=settings.learingrate)
    if settings.use_cuda:
        lgr.info("Using the GPU")
        settings.model.cuda()
        criterion.cudo()

    settings.model_loss = []
    # train model
    for e in range(settings.trainmodel_epoch):
        var_x = Variable(train_x)
        out = settings.model(var_x)
        loss = criterion(out, var_x)
        settings.optimizer.zero_grad()
        loss.backward()
        settings.optimizer.step()
        settings.model_loss.append(loss.item())

        if (e+1) % 50 == 0:
                print('   Epoch: {}, Loss: {:.10f}'.format(e+1, loss.item()))
  
    model = settings.model.eval()

    calculate_anomalyscore(train_x, model)

    # # Prediction
    # var_data = Variable(train_x)
    # pred_train = model(var_data)
    # pred_train = pred_train.view(-1, settings.look_back).data.cpu().numpy()

    # # Reconstruct train_x and pred_train to become real and reco
    # # Create real data by using train_x
    # data = train_x.view(-1, settings.look_back).data.cpu().numpy()
    # settings.real = np.append(data[:,1], data[len(data)-1])
    # # Create reconsturct data (reco) by using pred_train
    # reco = np.append(pred_train[:,1], pred_train[len(pred_train)-1])

    # reco = np.insert(reco, 0, reco[0])
    # # print('reco =', len(reco))
    # settings.reco = np.delete(reco, len(reco)-1)
    # # print('reco =', len(reco))

    # # Create score (diff)
    # settings.diff = np.abs(np.subtract(settings.real,settings.reco))

    # EWMA
    if settings.ewma_method:
        diff_df = pd.DataFrame(settings.diff, columns=['diff'])
        diff_df['EWMA'] = diff_df['diff'].ewm(span=settings.ewma_weight, adjust=False).mean()
        ewma = diff_df['EWMA'].to_numpy()
    else:
        # No nasa method
        ewma = settings.diff

    settings.ewma_mean = ewma.mean()
    settings.ewma_std = ewma.std()
    settings.anomaly_level = [settings.ewma_mean+(i*settings.ewma_std) for i in range(1,11)]

    process_graphreconstruct = Process(target=gmodel.show_graphreconstruct)
    process_graphreconstruct.start()

    confirmtrainmodel_message = "Do you confirm to use this model"
    confirm_trainmodel = glofunc.confirm_option(confirmtrainmodel_message)

    if confirm_trainmodel:
        # select anomaly level
        # select_anomalylevel()
        console = Console()
        settings.selectanomaly_list = [0]
        console.print("Please enter 3 Anomaly Levels from 1 to 10")
        for line in ['1st', '2nd', '3rd']:
            passed = 0
            while passed == 0:
                levelinput = console.input("[[bold yellow]?[/]] Enter {} anomaly level [1-10]?: ".format(line))

                # Check number
                try: 
                    levelinput = int(levelinput)
                    checknum = True
                except:
                    print("{} is not Number!.".format(levelinput))
                    checknum = False
                    checkrate = False

                # Check rate
                if checknum:
                    checkrate = 0 < levelinput and 11 > levelinput
                    if checkrate==False:
                        print("{} is not between 1 to 10.".format(levelinput))
                
                # Check duplicate
                if checkrate and checknum:
                    if levelinput not in settings.selectanomaly_list:
                        settings.selectanomaly_list.append(levelinput) 
                        passed = 1
                    else:
                        print("{} is duplicate.".format(levelinput))

        settings.selectanomaly_list.remove(0)
        settings.selectanomaly_list.sort()
        settings.selectanomaly_lelvel = [settings.anomaly_level[i-1] for i in settings.selectanomaly_list]

        create_rollingwindow(settings.dataset)

        if settings.use_cuda:
            dataset_x = torch.from_numpy(settings.rollingwindow_data_X).float().cuda()
        else:
            dataset_x = torch.from_numpy(settings.rollingwindow_data_X).float()

        calculate_anomalyscore(dataset_x, model)

        # create anomaly status dataframe
        # settings.diff = np.insert(settings.diff, 0, 0)
        # settings.diff = np.delete(settings.diff, len(settings.diff)-1)
        data = {'real':settings.real, 'score':settings.diff}
        anomalystate_dataframe = pd.DataFrame(data=data)
        anomalystate_dataframe['anomaly_state'] = anomalystate_dataframe.apply(lambda x:  0 if x['score']<settings.selectanomaly_lelvel[0] else (1 if x['score']<settings.selectanomaly_lelvel[1] else (2 if x['score']<settings.selectanomaly_lelvel[2] else 3)), axis=1)
        anomalystate_dataframe['id'] = anomalystate_dataframe.index
        settings.anomalystate_dataframe = anomalystate_dataframe.copy()

        process_graphanomalydetection = Process(target=gmodel.show_graphanomalydetection)
        process_graphanomalydetection.start()

        confirmanomalyresult_message = "\nDo you confirm the result of anomaly detection"
        confirm_anomalyresult = glofunc.confirm_option(confirmanomalyresult_message)

        if confirm_anomalyresult:
            confirmsavemodel_message = "Do you save model and result of anomaly detection"
            confirm_savamodel = glofunc.confirm_option(confirmsavemodel_message)
            if confirm_savamodel:
                save_anomalydetection()
        #     else:
        #         retrian_message = "Please select:"
        #         retrain_options = [
        #                 {'label': '1. Retrain', 'func': 'train_model()'},
        #                 {'label': '2. Back to custom Training points again', 'func': 'select_traindata("{}")'.format(settings.model_feature)},
        #                 {'label': '3. Back to select 3 Anomaly Levels again', 'func': 'reselect_anomalylevel()'},
        #                 {'label': '4. Back to Manage Model', 'func': 'manage_model()'}
        #         ]
        #         function = glofunc.select_option(retrian_message, retrain_options)
        #         call_function(function)
        # else:
        #     retrian_message = "Please select:"
        #     retrain_options = [
        #             {'label': '1. Retrain', 'func': 'train_model()'},
        #             {'label': '2. Back to custom Training points again', 'func': 'select_traindata("{}")'.format(settings.model_feature)},
        #             {'label': '3. Back to select 3 Anomaly Levels again', 'func': 'reselect_anomalylevel()'},
        #             {'label': '4. Back to Manage Model', 'func': 'manage_model()'}
        #     ]
        #     function = glofunc.select_option(retrian_message, retrain_options)
        #     call_function(function)
        if confirm_anomalyresult == False or confirm_savamodel == False:
            retrian_message = "Please select:"
            retrain_options = [
                {'label': '🔁 Retrain ⛭', 'func': 'train_model()'},
                {'label': '◀ Back to select 3 Anomaly Levels again ⛭', 'func': 'reselect_anomalylevel()'},
                {'label': '⏪ Back to custom Training points again ⛭', 'func': 'select_traindata("{}")'.format(settings.model_feature)},
                {'label': '⏮  Back to Manage Model', 'func': 'manage_model()'}
            ]
            function = glofunc.select_option(retrian_message, retrain_options)
            call_function(function)
    else:     
        retrian_message = "Please select:"
        retrain_options = [
            {'label': '🔁 Retrain ⛭', 'func': 'train_model()'},
            {'label': '⏪ Back to custom Training points again ⛭', 'func': 'select_traindata("{}")'.format(settings.model_feature )},
            {'label': '⏮  Back to Manage Model', 'func': 'manage_model()'}
        ]
        function = glofunc.select_option(retrian_message, retrain_options)
        call_function(function)

def save_anomalydetection():
    if settings.createnewmodel == False:
        confirmsavemodel_message = "The Model and the Result of anomaly detection is exist, Do you replace"
        confirm_savamodel = glofunc.confirm_option(confirmsavemodel_message)
        if confirm_savamodel == False:
            manage_model()
    
    settings.table_info = 'analysis_info_theos_auto_m1'
    settings.anomaly_tablename = 'anomaly_theos_'+settings.tm_name.lower()+'_'+settings.model_freq.lower()+'_auto_m1'
    settings.transform_method = 'normalization'
    settings.algorithm_name = 'model_auto_m1'
    settings.model_name = settings.algorithm_name+'_'+settings.tm_name.lower()+'_'+settings.model_freq.lower()+'.pt'           
    # settings.model_address = "/home/mmgs/WindowsVermouth/App/models/model/"
    # settings.algorithm_path = "/home/mmgs/WindowsVermouth/App/models/"
    #settings.model_address = "model_auto_m1/model/"
    settings.model_address = "/home/mmgs/model_auto_m1/model"
    settings.algorithm_path = "model_auto_m1/algorithm/"
    settings.nowdate = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    remote_model = settings.model_address+settings.model_name
    local_model = rootpath.detect()+"/App/models/model/"+settings.model_name

    # create infomation of model
    model_state = {
        'algorithm_name': settings.algorithm_name,
        'algorithm_address' : settings.algorithm_path,
        'epoch' : settings.trainmodel_epoch,
        'state_dict': settings.model.state_dict(),'optimizer' : settings.optimizer.state_dict(),
        'input': settings.look_back,
        'tm_name': settings.tm_name,
        'freq': settings.model_freq,
        'feature_table': settings.model_feature,
        'anomaly_result_table': settings.anomaly_tablename,
        'model_address' : settings.model_address,

        'train_startpoint': settings.train_startpoint,
        'train_endpoint': settings.train_endpoint,
        'train_startdate': settings.train_startdate,
        'train_enddate': settings.train_enddate,

        'model_name': settings.model_name,
        'transform_method' : [settings.transform_method, [settings.min_value, settings.max_value]],
        'ewma_params': [settings.ewma_mean, settings.ewma_std],
        'anomaly_level' : settings.selectanomaly_list,
        'anomaly_value' : settings.selectanomaly_lelvel,
        'create_date' : settings.nowdate
    }

    try:

        # save model
        torch.save(model_state, local_model)

        # config ftp
        confftp = setup_service('MMGS_server1_server')
        with FTP(confftp.hosts) as ftp:
            ftp.login(user=confftp.users, passwd=confftp.passwords)
            # upload file
            with open(local_model, "rb") as file:
                ftp.storbinary('STOR %s' % remote_model, file)
                file.close()

        # remove model from local
        os.remove(local_model)

    except:
        # print("Error while save model to {}".format(settings.model_address))
        print("Error while upload {} model to server".format(settings.model_name))

    # create result anomaly dataframe
    anomalystate_list = settings.anomalystate_dataframe['anomaly_state'].tolist()
    anomalystate_list = [0]+anomalystate_list
    del anomalystate_list[-1]
    settings.resultanomaly_dataframe = settings.avgfeature_dataframe.copy()
    # settings.resultanomaly_dataframe['anomaly_state_auto_m1'] = settings.anomalystate_dataframe['anomaly_state']
    settings.resultanomaly_dataframe['anomaly_state_auto_m1'] = anomalystate_list
    settings.resultanomaly_dataframe = settings.resultanomaly_dataframe.set_index("id")

    # print(settings.resultanomaly_dataframe)
    try:
        connect = DBconn('MIXERs2_tm_analysis_db')
        cursor = connect.cursor()
    except (Exception, psycopg2.Error) as error:
        print('Error while connect for  record result of anomaly detection ', error)
    else:

        if settings.createnewmodel: # for create new model

        # try:
        #     # print(" --- connect")
        #     connect = DBconn('MIXERs2_tm_analysis_db')
        #     cursor = connect.cursor()
        # except (Exception, psycopg2.Error) as error:
        #     print('Error while connect for  record result of anomaly detection ', error)
        # else:
            # search last id from analysis_info_theos_auto_m1 table
            last_idinfotable_sql = "SELECT max(id) FROM {};".format(settings.table_info)
            cursor.execute(last_idinfotable_sql)
            last_idinfotable = cursor.fetchone()
            connect.commit()
            
            # record to analysis_info_theos_auto_m1 table
            # print(settings.train_startpoint, settings.train_endpoint, settings.train_startdate, settings.train_enddate)
            insert_infovalues = (int(last_idinfotable[0])+1, settings.tm_name.upper(), settings.model_freq, settings.model_feature, 
                    settings.transform_method, settings.algorithm_name, settings.model_address, settings.model_name, 
                    settings.nowdate, settings.nowdate, settings.anomaly_tablename, settings.train_startpoint, settings.train_endpoint, settings.train_startdate, settings.train_enddate)

            insert_info_sql = '''INSERT INTO {} (id, tm_name, freq, feature_table, transform_method, algorithm_name, model_address, model_name, 
                    create_date, update_date, anomaly_result_table, start_trainpoint, end_trainpoint, start_traindate, end_traindate) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''.format(settings.table_info)

            cursor.execute(insert_info_sql, insert_infovalues)
            connect.commit()

            # create anomaly table
            create_anomaly_result_table_sql = '''CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY,name TEXT, utc TIMESTAMP, epoch_ten numeric(15,0),
                    avg numeric(15,5), anomaly_state_auto_m1 integer);'''.format(settings.anomaly_tablename)
            cursor.execute(create_anomaly_result_table_sql)
            connect.commit()
            
            # record anomaly data to db table
            recordbuffer(connect, cursor, settings.anomaly_tablename, settings.resultanomaly_dataframe)
                    
            # finally:
            #     if connect:
            #         connect.close()
            #         cursor.close()
            
        elif settings.createnewmodel == False: # for retrain model
        # try:
        #     connect = DBconn('MIXERs2_tm_analysis_db')
        #     cursor = connect.cursor()
        # except (Exception, psycopg2.Error) as error:
        #     print('Error while connect for  record result of anomaly detection ', error)
        # else:
        #     print("----------- replace model -------------")
            # update infomation for analysis_info_theos_auto_m1 table
            update_infovalues = (settings.nowdate, settings.train_startpoint, settings.train_endpoint, settings.train_startdate, settings.train_enddate)
            update_info_sql = "UPDATE {} SET update_date=%s, \
                    start_trainpoint=%s, end_trainpoint=%s, \
                    start_traindate=%s, end_traindate=%s WHERE id = {}".format(settings.table_info, settings.model_id)

            cursor.execute(update_info_sql, update_infovalues)
            connect.commit()

            # drop result anomaly table
            print("drop result anomaly table")
            dropanomalytable_sql = '''DROP TABLE {}'''.format(settings.anomaly_tablename)
            cursor.execute(dropanomalytable_sql)
            connect.commit()
            print("drop result anomaly table")

            # create anomaly table
            create_anomaly_result_table_sql = '''CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY,name TEXT, utc TIMESTAMP, epoch_ten numeric(15,0),
                    avg numeric(15,5), anomaly_state_auto_m1 integer);'''.format(settings.anomaly_tablename)
            cursor.execute(create_anomaly_result_table_sql)
            connect.commit()
            
            # record anomaly data to db table
            recordbuffer(connect, cursor, settings.anomaly_tablename, settings.resultanomaly_dataframe)

        # update progress id
        countinfo_sql = "SELECT count(*) FROM analysis_info_theos_auto_m1 WHERE tm_name = \'{}\'".format(settings.tm_name.upper()) 
        cursor.execute(countinfo_sql)
        if cursor.fetchone()[0] > 0:
            glofunc.updateprogressid(3)

    finally:
        if connect:
            connect.close()
            cursor.close()

    manage_model()

def preview_graphanomalydetection():
    # Preview Graph of your result Model
    selectfeature_message = "Please select to Preview Graph of your result Model"
    selectfeature_options = [
        {'label': str(i+1)+'. '+info[3], 'func':info[3]+","+info[10]} for i, info in enumerate(settings.infoma)
    ]
    info = glofunc.select_option(selectfeature_message, selectfeature_options)
    # settings.model_feature  = function.split("'")[1]

    # for info in settings.infoma:
    #     if info[3] == settings.model_feature:
    #         anomaly_tablename = info[10]
    #         analysis_tablename = info[3]
    #         break

    info = info.split(",")
    anomaly_tablename = info[1]
    analysis_tablename = info[0]

    feature_sql = "SELECT * FROM {};".format(analysis_tablename)
    anomaly_sql = "SELECT utc, avg, anomaly_state_auto_m1 FROM {} WHERE anomaly_state_auto_m1 != 0;".format(anomaly_tablename)
    # feature_sql = """
    #     SELECT ANA.*, ANO.anomaly_state_auto_m1 
    #     FROM {} AS ANO 
    #     LEFT JOIN {} AS ANA
    #     ON ANO.id = ANA.id;
    # """.format(anomaly_tablename, analysis_tablename)
    try:
        connect = DBconn('MIXERs2_tm_analysis_db')
        settings.feature_dataframe = pd.read_sql(feature_sql, connect)
        settings.previewresult_dataframe = pd.read_sql(anomaly_sql, connect)

    except (Exception, psycopg2.Error) as error:
        print('Error while query', error)
    finally:
        if connect:
            connect.close()

    process_graphanomalyfeature = Process(target=gmodel.show_graphanomalyfeature)
    process_graphanomalyfeature.start()

    manage_model()

def delete_model():
    selectfeature_message = "Please select to delete your result Model"
    selectfeature_options = [
        {'label': str(i+1)+'. '+info[3], 'func':info[3]+","+info[10]} for i, info in enumerate(settings.infoma)
    ]
    function = glofunc.select_option(selectfeature_message, selectfeature_options)
    function = function.split(",")
    anomaly_tablename = function[1]
    analysis_tablename = function[0]

    # print(function)
    console = Console()
    console.print("The Model and Result of [bold green]{} feature [/] [bold red]will be Delete[/]".format(analysis_tablename))
    confirmdelete_message = "Do you confirm to Delete the feature"
    confirm_delete = glofunc.confirm_option(confirmdelete_message)

    if confirm_delete:
        drop_anomalytable_sql = "DROP TABLE {};".format(anomaly_tablename)
        delete_anomalyinfo_sql = "DELETE FROM analysis_info_theos_auto_m1 WHERE anomaly_result_table = \'{}\'".format(anomaly_tablename)

        try:
            connect = DBconn('MIXERs2_tm_analysis_db')
            cursor = connect.cursor()

            for i in [delete_anomalyinfo_sql, drop_anomalytable_sql]:
                cursor.execute(i)
                connect.commit()

        except (Exception, psycopg2.Error) as error:
            print('Error while query', error)

        else:
            countinfo_sql = "SELECT count(*) FROM analysis_info_theos_auto_m1 WHERE tm_name = \'{}\'".format(settings.tm_name.upper()) 
            cursor.execute(countinfo_sql)
            if cursor.fetchone()[0] == 0:
                glofunc.updateprogressid(2)

        finally:
            if connect:
                connect.close()

    manage_model()



# def record_dbnewcreatemodel():
#     # connect = DBconn('MIXERs2_tm_analysis_db')
#     print("---record DB -----")
#     try:
#         print(" --- connect")
#         connect = DBconn('MIXERs2_tm_analysis_db')
#         cursor = connect.cursor()
#     except (Exception, psycopg2.Error) as error:
#         print('Error while connect for  record result of anomaly detection ', error)
#     else:
#         # try:
#         #     print(" --- search last ID")
#         # search last id from analysis_info_theos_auto_m1 table
#         last_idinfotable_sql = "SELECT max(id) FROM analysis_params_theos_auto_m1"
#         cursor.execute(last_idinfotable_sql)
#         last_idinfotable = cursor.fetchone()
#         connect.commit()
#             # print("last id ", last_idinfotable, last_idinfotable[0])
#         # except:
#             # print("Error while search last id from analysis_info_theos_auto_m1 table")

#         # try:
#         # print(" --- record analysis_info_theos_auto_m1")
#         # record to analysis_info_theos_auto_m1 table
#         # now = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
#         print(settings.train_startpoint, settings.train_endpoint, settings.train_startdate, settings.train_enddate)
#         insert_infovalues = (int(last_idinfotable[0])+1, settings.tm_name.upper(), settings.model_freq, settings.model_feature, 
#                 settings.transform_method, settings.algorithm_name, settings.model_address, settings.model_name, 
#                 settings.nowdate, settings.nowdate, settings.anomaly_tablename, settings.train_startpoint, settings.train_endpoint, settings.train_startdate, settings.train_enddate)
# # start_trainpoint
#         insert_info_sql = '''INSERT INTO {} (id, tm_name, freq, feature_table, transform_method, algorithm_name, model_address, model_name, 
#                 create_date, update_date, anomaly_result_table, start_trainpoint, end_trainpoint, start_traindate, end_traindate) 
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''.format(settings.table_info)

#         print(insert_info_sql)
#         cursor.execute(insert_info_sql, insert_infovalues)
#         connect.commit()
#         # except:
#         #     print("Error while record infomation to analysis_info_theos_auto_m1 table")

#         # try:
#         #     print(" --- create table")
#             # create anomaly table
#         create_anomaly_result_table_sql = '''CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY,name TEXT, utc TIMESTAMP, epoch_ten numeric(15,0),
#                 avg numeric(15,5), anomaly_state_auto_m1 integer);'''.format(settings.anomaly_tablename)
#         cursor.execute(create_anomaly_result_table_sql)
#         connect.commit()
#         print(" --- record ")
#         # record anomaly data to db table
#         recordbuffer(connect, cursor, settings.anomaly_tablename, settings.resultanomaly_dataframe)
#         # except:
#         #     print("Error while record new anomaly table")

        
#     finally:
#         if connect:
#             connect.close()
#             cursor.close()
