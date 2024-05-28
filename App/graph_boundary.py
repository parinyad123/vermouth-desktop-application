from matplotlib.gridspec import GridSpec
import sys
import rootpath
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
# from plotly.subplots import make_subplots
# import plotly.express as px
# import plotly.graph_objects as go

# ---------------------------
# import matplotlib
# matplotlib.use('Qt5Agg')

from PySide6.QtWidgets import QMainWindow, QApplication

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
# ---------------------------

import settings
sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as DBconn

def export_tmrecord():
    table_name = "record_theos_"+settings.tm_name.lower()
    sql = '''SELECT utc, eng_value FROM {};'''.format(table_name)
    
    try:
        connect = DBconn('MIXERs2_tm_record_db')
        raw_data = pd.read_sql(sql, connect)
        settings.raw_dataframe = raw_data      
    except (Exception, psycopg2.Error) as error:
        print("Error while export data from {} table".format(table_name), error)
    finally:
        if connect:
            connect.close()

def delete_zerovalue():
    settings.delzero_dataframe = settings.raw_dataframe.copy()
    index_name =  settings.delzero_dataframe[ settings.delzero_dataframe['eng_value'] == 0 ].index
    settings.delzero_dataframe =  settings.delzero_dataframe.drop(index_name)
    
    settings.current_rawboundary_dataframe = settings.delzero_dataframe.copy()

def calculate_boundarybytimeofmean():
    settings.mean_cal = settings.current_rawboundary_dataframe['eng_value'].mean(skipna=True)

    if settings.mean_cal > 0:
        settings.upper_bound_xtime = settings.mean_cal*(settings.timeofmean+1)
        settings.lower_bound_xtime = settings.mean_cal*(1-settings.timeofmean)
    elif settings.mean_cal < 0:
        settings.upper_bound_xtime = -1*settings.mean_cal*(settings.timeofmean+1)
        settings.lower_bound_xtime = -1*settings.mean_cal*(1-settings.timeofmean)

def calculate_boundarybyquantile(quant_up, quant_low):
    # print("--------")
    # print(settings.current_rawboundary_dataframe)
    lower_bound_quantile = settings.current_rawboundary_dataframe.quantile(quant_low)['eng_value']
    upper_bound_quantile = settings.current_rawboundary_dataframe.quantile(quant_up)['eng_value']
    return upper_bound_quantile, lower_bound_quantile

def delete_boundary(upper_bound, lower_bound):
    # print("delete boundary ----")
    # print(settings.current_rawboundary_dataframe)
    bound_data = settings.current_rawboundary_dataframe.copy()
    index_name = bound_data[bound_data['eng_value'] > upper_bound].index
    bound_data = bound_data.drop(index_name)
    index_name = bound_data[bound_data['eng_value'] < lower_bound].index
    bound_data = bound_data.drop(index_name)
    # reset index
    bound_data.reset_index(inplace=True)
    # drop index column
    bound_data = bound_data.drop(["index"], axis=1)
 
    return bound_data

def create_graphtitle(labels_params):
    titles = [
        'raw data {}'.format(labels_params['tm_name'].upper()),
        'remove eng vulue by {}x of avg {} :: upper: {} lower: {}'.format(labels_params['timeofmean'],labels_params['x_mean'],labels_params['x_mean_up'],labels_params['x_mean_low']),
        'remove eng value by assign yourself :: upper: {} lower: {}'.format(labels_params['own_up'], labels_params['own_low'])
    ]
    return titles   

def show_graphboundary():
    # print('In function show graph')
    labels_params = {
        'tm_name': settings.tm_name,
        'timeofmean': settings.timeofmean,
        'x_mean': settings.mean_cal,
        'x_mean_low': settings.lower_bound_xtime,
        'x_mean_up': settings.upper_bound_xtime,
        'own_low': settings.lower_bound_custom,
        'own_up': settings.upper_bound_custom
    }

    titles = [
        'raw data {}'.format(labels_params['tm_name'].upper()),
        'remove eng vulue by {} times of mean {} :: lower: {} upper: {}'.format(labels_params['timeofmean'],labels_params['x_mean'],labels_params['x_mean_low'] ,labels_params['x_mean_up']),
        'remove eng value by custom own Upper and Lower :: lower: {} upper: {}'.format(labels_params['own_low'], labels_params['own_up'])
    ]

    df= [settings.current_rawboundary_dataframe, settings.timeofmean_dataframe, settings.custom_dataframe]
    
    fig = plt.figure(figsize=(15,10))
    plt.gcf().canvas.set_window_title('Boundary') 
    gs = GridSpec(nrows=len(df), ncols=2, width_ratios=[3,1])
 
    for row in range(len(df)):
        for col in range(2):
            ax = fig.add_subplot(gs[row,col])
            df_pro = df[row].copy()
            df_pro = df_pro.sort_values('utc')
            
            if col == 0:
                ax.plot(df_pro['utc'], df_pro['eng_value'])
                # print(df_pro['utc'], df_pro['eng_value'])
                plt.title(titles[row], size=9)
                # ax.legend(loc='best')
            if col == 1:
                if settings.remove_hist_edge:
                    lower_hist = df_pro.quantile(settings.lower_hist_edge)['eng_value']
                    upper_hist = df_pro.quantile(settings.upper_hist_edge)['eng_value']
                    df_pro = df_pro[df_pro['eng_value']>lower_hist]
                    df_pro = df_pro[df_pro['eng_value']<upper_hist]
                df_pro = df_pro[df_pro['eng_value'].notna()]
                ax.hist(df_pro['eng_value'], bins=100)

    fig.tight_layout(pad=.5, h_pad=1)
    # print("-- start show ---")
    plt.show()
    # print("-- end show ---")
    

# def show_plotgraphbpundary():

#     titles = [
#         'Raw data {}'.format(settings.tm_name.upper()),
#         'Delete eng vulue by {} times of mean {:.5f} (upper: {:.5f} lower: {:.5f})'.format(settings.timeofmean,settings.mean_cal,settings.upper_bound_xtime,settings.lower_bound_xtime),
#         'Delete eng value by assign yourself (upper: {:.5f} lower: {:.5f})'.format(settings.upper_bound_custom, settings.lower_bound_custom)
#     ]

#     fig = make_subplots(rows=3, cols=2,
#                         column_widths=[0.8, 0.2],
#                         subplot_titles=(titles[0], " ", titles[1], "", titles[2]),
#                         horizontal_spacing = 0.03, vertical_spacing=0.06)

#     df= [settings.current_rawboundary_dataframe, settings.timeofmean_dataframe, settings.custom_dataframe]
    
#     for row in range(1,4):
#         for col in range(1,3):
#             df_pro = df[row-1].copy()
#             df_pro = df_pro.sort_values('utc')
#             if col == 1:
#                 fig.add_trace(go.Scatter(x=df_pro['utc'], y=df_pro['eng_value'], mode='lines'),
#                                     row=row, col=col)
#             elif col == 2:
#                 if settings.remove_hist_edge:
#                     lower_hist = df_pro.quantile(settings.lower_hist_edge)['eng_value']
#                     upper_hist = df_pro.quantile(settings.upper_hist_edge)['eng_value']
#                     df_pro = df_pro[df_pro['eng_value']>lower_hist]
#                     df_pro = df_pro[df_pro['eng_value']<upper_hist]
#                 df_pro = df_pro[df_pro['eng_value'].notna()]
#                 df_pro = df_pro.reset_index(drop=True)
#                 fig.add_trace(go.Histogram(x=df_pro['eng_value'].to_numpy()), row=row, col=col)   
#         print('graph row', datetime.now())    
#     fig.update_layout(template='plotly_white', showlegend=False, 
#                         font=dict(family="Helvetica, sans-serif", size=12),
#                         margin=dict(l=5, r=5, t=20, b=5))
#     fig.show()

