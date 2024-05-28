from unittest import result
import pandas as pd

def init():

# ====== db management ======
    global passmainmenu
    passmainmenu = True
# ====== feature.py =========
    # --------  boundary  ------------
    global tm_name, raw_dataframe
    tm_name = ""
    raw_dataframe = None

    # get data params and info table database as $tm_name
    global params, infoma
    params = None
    infoma = None

    # delete 0 value & dataframe
    global delete_zero, delzero_dataframe
    delete_zero = True
    delzero_dataframe = None

    # current dataframe (delete/Not delete 0 value)
    global method_boundary, current_boundary, current_rawboundary_dataframe
    method_boundary = "timeofmean"
    current_boundary = 0
    current_rawboundary_dataframe = None

    # show histogram
    global remove_hist_edge, lower_hist_edge, upper_hist_edge
    remove_hist_edge=True
    lower_hist_edge=0.25
    upper_hist_edge=0.75

    # times of mean boundary
    global timeofmean, upper_bound_xtime, lower_bound_xtime, mean_cal, timeofmean_dataframe
    timeofmean = 10
    mean_cal = None
    upper_bound_xtime = None
    lower_bound_xtime = None
    timeofmean_dataframe = None
    
    # custom own boundary
    global upper_bound_own, lower_bound_own, upper_bound_custom, lower_bound_custom, custom_dataframe
    upper_bound_own=.95
    lower_bound_own=.05
    upper_bound_custom = None
    lower_bound_custom = None
    custom_dataframe = None
    
    # --------  frequency  ------------
    # grouph by frequency
    global frequencies_array, frequencies_dataframe_array, frequency_dataframe
    frequencies_array = ["1H", "4H", "1D"]
    frequencies_dataframe_array = []
    frequency_dataframe = pd.DataFrame()
    
    # show histogram
    global lower_hist_freq, upper_hist_freq
    lower_hist_freq = 0.25
    upper_hist_freq = 0.75

    # graph feature
    global feature_frequency, feature_dataframe, feature_tablename
    feature_frequency = "1D"
    feature_dataframe = pd.DataFrame()
    feature_tablename = None


# ======= model.py =========== 
    # -------- preview feature graph -------
    global previewfeature_dataframe
    previewfeature_dataframe = None

    # -------- process detial ----------
    global model_feature, createnewmodel, model_freq
    model_feature = None
    createnewmodel = True
    model_freq = None 

    # --------- create model ------------
    global avgfeature_dataframe, train_startpoint, train_endpoint, train_startdate, train_enddate
    avgfeature_dataframe = None
    train_startpoint = None
    train_endpoint = None
    train_startdate = None
    train_enddate = None

    # --------- split train/test data -----
    global dataset, train_data, test_data
    train_data = None
    test_data = None
    dataset = None

    # --------- normalization ---------
    global transform_method, max_value, min_value
    transform_method = None
    max_value = None
    min_value = None

    # --------- rolling window --------
    global look_back, rollingwindow_data_X
    look_back = 10
    rollingwindow_data_X = None

    # --------- train model ---------
    global use_cuda, learingrate, trainmodel_epoch, model, optimizer
    use_cuda = False
    learingrate = 0.001
    trainmodel_epoch = 500
    model = None
    optimizer = None

    # --------- recostruct ---------
    global real, reco, diff, model_loss
    real = None
    reco = None
    diff = None
    model_loss = None

    # --------- EWMA --------
    global ewma_method, ewma_weight, ewma_mean, ewma_std, anomaly_level
    ewma_method = True
    ewma_weight = 10
    ewma_mean = None
    ewma_std = None
    anomaly_level = []

    # --------- select anomaly level ----
    global selectanomaly_list, selectanomaly_lelvel
    selectanomaly_list = []
    selectanomaly_lelvel = []
    
    # --------- anomaly dataset -------
    global anomalystate_dataframe, resultanomaly_dataframe
    anomalystate_dataframe = None
    resultanomaly_dataframe = None

    # --------- save model --------
    global table_info, algorithm_name, model_name, model_address, anomaly_tablename, algorithm_path, model_address, nowdate
    table_info = None
    algorithm_name = None
    model_name = None
    model_address = None
    anomaly_tablename = None
    algorithm_path = None
    model_address = None
    nowdate = None

    # -------- Retrain model -------
    global model_id
    model_id = None

    # -------- preview result anomaly detection -----
    global previewresult_dataframe 
    previewresult_dataframe = None