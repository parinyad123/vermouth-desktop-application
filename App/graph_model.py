import pandas as pd
import numpy as np
import scipy.stats as ss
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import settings
import feature as feature

def show_graphselecttraindata():
    # dataset = settings.avgfeature_dataframe['avg'].values.astype('float32')
    # print(type(dataset))
    dataset = settings.avgfeature_dataframe['avg']
    dataset.index+=1
    # print(dataset)
    fig = plt.figure(figsize=(15,10))
    plt.gcf().canvas.set_window_title('Average') 
    plt.plot(dataset, label='{} {}'.format(settings.tm_name,settings.model_freq))
    plt.legend(loc='best')
    fig.tight_layout(pad=.5, h_pad=2)
    plt.show()

def show_graphreconstruct():
    color_level = ['#FCF3CF','#F7DC6F', '#F1C40F', '#F5B041', '#F39C12', '#AF601A', '#E74C3C', '#CB4335', '#943126', '#641E16']
    fig = plt.figure(figsize=(15,10))
    gs = GridSpec(nrows=2, ncols=2, width_ratios=[3,1], height_ratios=[1,1])
    plt.gcf().canvas.set_window_title('Train Model') 
    ax0 = fig.add_subplot(gs[0,0])
    ax0.plot(settings.real, label='real')
    ax0.plot(settings.reco, 'r', label='reconstruction')
    ax0.legend(loc='best')

    ax1 = fig.add_subplot(gs[1,0])
    ax1.plot(settings.diff, label='score') 
    for i in range(len(settings.anomaly_level)):
        ax1.axhline(y=settings.anomaly_level[i], label=str(i+1), color=color_level[i])
    ax1.legend(loc='best')

    ax2 = fig.add_subplot(gs[0,1])
    ax2.plot(settings.model_loss, label='model error')
    ax2.legend(loc='best')

    ax3 = fig.add_subplot(gs[1,1])
    ax3.hist(settings.diff, bins=100, label='score')
    for i in range(len(settings.anomaly_level)):
        ax3.axvline(x=settings.anomaly_level[i], label=str(i+1), color=color_level[i])
    ax3.legend(loc='best')


    # plt.suptitle('result')
    fig.tight_layout(pad=.5, h_pad=2)
    plt.show()


def show_graphanomalydetection():
    tmname_freq = settings.model_feature.split("_")
    tmname_freq = tmname_freq[2].upper() + ' ' + '({})'.format(tmname_freq[3].upper())
    color_line = ['#F9E79F','#F5B041','#E74C3C']

    fig = plt.figure(figsize=(15,10))
    plt.gcf().canvas.set_window_title('Anomaly Detection') 
    gs = GridSpec(nrows=3, ncols=2, width_ratios=[3,1])

    ax0 = fig.add_subplot(gs[0,0])
    ax0.plot(settings.real, label='{}'.format(tmname_freq))
    ax0.plot(settings.reco, 'r', label='reconstruction')
    ax0.legend(loc='best')

    ax1 = fig.add_subplot(gs[1,0])
    ax1.plot(settings.diff, label='score') 
    for i in range(len(settings.selectanomaly_lelvel)):
        ax1.axhline(y=settings.selectanomaly_lelvel[i], label='anomaly level '+str(i+1), color=color_line[i])
    ax1.legend(loc='best')

    ax2 = fig.add_subplot(gs[2,0])
    ax2.plot(settings.real, label='{}'.format(tmname_freq))
    for i in range(len(settings.selectanomaly_lelvel)):
        ax2.scatter(settings.anomalystate_dataframe[settings.anomalystate_dataframe['anomaly_state']==i+1]['id'], settings.anomalystate_dataframe[settings.anomalystate_dataframe['anomaly_state']==i+1]['real'], label='anomaly level '+str(i+1), color = color_line[i])
    ax2.legend(loc='best')

    ax3 = fig.add_subplot(gs[:,1])
    ax3.hist(settings.diff, bins=100, label='score')
    for i in range(len(settings.selectanomaly_lelvel)):
        ax3.axvline(x=settings.selectanomaly_lelvel[i], label='anomaly level '+str(i+1), color=color_line[i])
    ax3.legend(loc='best')

    fig.tight_layout(pad=.5, h_pad=2)
    plt.show()

def show_graphanomalyfeature():
    color_line = ['#F9E79F','#F5B041','#E74C3C']
    feature_dataframe = settings.feature_dataframe.copy()
    result_dataframe = settings.previewresult_dataframe.copy()
    # rawboundary_dataframe = settings.current_rawboundary_dataframe.copy()
    
    feature_dataframe = feature_dataframe.sort_values(by=['utc'])
    result_dataframe = result_dataframe.sort_values(by=['utc'])
    # rawboundary_dataframe = rawboundary_dataframe.sort_values(by=['utc'])
    fig = plt.figure(figsize=(15,10))
    plt.gcf().canvas.set_window_title('Anomaly Detection and Statistical Feature') 
    gs = GridSpec(nrows=3, ncols=1, height_ratios=[1,1,1])

    # ax0 = fig.add_subplot(gs[0,0])
    # ax0.plot(rawboundary_dataframe['utc'],rawboundary_dataframe['eng_value'], label='raw data : {}'.format(settings.tm_name.upper()))
    # ax0.legend(loc='best')

    ax1 = fig.add_subplot(gs[0,0])
    ax1.plot(feature_dataframe['utc'], feature_dataframe['avg'], label='avg {}'.format(settings.feature_frequency))
    for i in range(3):
        ax1.scatter(result_dataframe[result_dataframe['anomaly_state_auto_m1']==i+1]['utc'], 
                    result_dataframe[result_dataframe['anomaly_state_auto_m1']==i+1]['avg'], 
                    label='anomaly level '+str(i+1), color = color_line[i])
    ax1.legend(loc='best')

    color = 'tab:red'
    ax2 = fig.add_subplot(gs[1,0])
    ax2.plot(feature_dataframe['utc'], feature_dataframe['std'], color=color, alpha=0.7,  label='std')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper left')

    color = 'tab:blue'
    ax3 = ax2.twinx()
    ax3.plot(feature_dataframe['utc'], feature_dataframe['count'], color=color, alpha=0.7, label='count')
    ax3.tick_params(axis='y', labelcolor=color)
    ax3.legend(loc='upper right')


    ax4 = fig.add_subplot(gs[2,0])
    ax4.plot(feature_dataframe['utc'], feature_dataframe['q1'], label='q1')
    ax4.plot(feature_dataframe['utc'], feature_dataframe['q2'], label='q2')
    ax4.plot(feature_dataframe['utc'], feature_dataframe['q3'], label='q3')
    ax4.plot(feature_dataframe['utc'], feature_dataframe['max'], label='max')
    ax4.plot(feature_dataframe['utc'], feature_dataframe['min'], label='min')
    ax4.legend(loc='best')

    fig.tight_layout(pad=.5, h_pad=2)
    plt.show()