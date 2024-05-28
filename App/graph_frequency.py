import pandas as pd
import numpy as np
import scipy.stats as ss
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import settings
import feature as feature
def create_frequencydataframe():
    settings.frequencies_dataframe_array = []

    if "remove boundary" not in settings.frequencies_array:
        settings.frequencies_array = ['remove boundary']+settings.frequencies_array

    for freq in settings.frequencies_array:
        if freq != 'remove boundary':
            # mean_freq = settings.current_rawboundary_dataframe.copy()
            mean_freq = settings.frequency_dataframe.copy()
            try:
                mean_freq = mean_freq.groupby(pd.Grouper(key='utc', freq=freq)).mean().rename(columns={'eng_value':'mean'})
            except:
                print("Error because {} frequency is Wrong!!".format(freq))
                feature.preview_customfrequency()
            else:
                settings.frequencies_dataframe_array.append(mean_freq) 
        else:
            # remove_boundary_df = settings.current_rawboundary_dataframe.copy()
            remove_boundary_df = settings.frequency_dataframe.copy()
            remove_boundary_df = remove_boundary_df.rename(columns = {'eng_value':'mean'})
            remove_boundary_df = remove_boundary_df.sort_values(by=['utc'])
            remove_boundary_df = remove_boundary_df.set_index('utc')
            settings.frequencies_dataframe_array.append(remove_boundary_df)

def calculate_statistics(dfreq, row):
 
    num_c = dfreq.copy()
    # print('--  len  -- {}'.format(len(num_c)))
   
    if row == 0:
        num_len = len(settings.raw_dataframe)
        n_lost = num_len - len(num_c)
    else:
        num_len = len(num_c)
        n_lost = num_c.isna().sum()['mean']
    # print('--  lost mean  {} -- {}'.format(row, n_lost))
    n_nan = n_lost/num_len*100
    num_c = num_c[num_c['mean'].notna()]
    num_c = num_c['mean'].to_numpy()
    # print('-- num c -- {}'.format(num_c))
    n_max = np.max(num_c)
    n_min = np.min(num_c)
    n_std = np.std(num_c)
    n_mea = np.mean(num_c)
    n_med = np.median(num_c)
    n_mod = ss.mode(num_c)[0][0]
    n_skw = ss.skew(num_c)
    n_kur = ss.kurtosis(num_c)
    # print('Nan = ', n_nan, type(n_nan))
    # print('std = ', n_std)
    # print('mean = ', n_mea)
    # print('med = ', n_med)
    # print('mod = ', n_mod)
    # print('skew = ', n_skw)
    # print('kurtosis = ', n_kur)

    stat = ['lost(%)','min','max','mean', 'med', 'mode', 'std', 'skew', 'kurt']
    star_v = [n_nan,n_min,n_max, n_mea, n_mod, n_med, n_std, n_skw, n_kur]
    stat_des = "num of lost = {} from {} ".format(n_lost, num_len)
    hist_des = ""
    for s in range(len(stat)-2):
        stat_des = stat_des+stat[s]+" : {:.5f}".format(star_v[s])+"  "
    # print(stat_des)
    for h in range(len(stat)-2,len(stat)):
        hist_des = hist_des+stat[h]+" : {:.5f}".format(star_v[h])+"  "
    # print(hist_des)

    return stat_des,hist_des

def show_graphfrequency():
    remove_hist_edge = True
    
    fig = plt.figure(figsize=(15,10))
    plt.gcf().canvas.set_window_title('Frequency') 
    gs = GridSpec(nrows=len(settings.frequencies_dataframe_array), ncols=2, width_ratios=[3,1])

    for row in range(len(settings.frequencies_dataframe_array)):
        
        for col in range(2):
            ax = fig.add_subplot(gs[row,col])
            dfreq = settings.frequencies_dataframe_array[row].copy()
            
            if col == 0:
                if row == 0:
                    stat_des, hist_des = calculate_statistics(dfreq, row)
                else:
                    stat_des, hist_des = calculate_statistics(dfreq, row)
                stat_des = settings.frequencies_array[row]+" ({})".format(settings.tm_name.upper())+" ::> "+stat_des

                ax.plot(dfreq, label=settings.frequencies_array[row])
                ax.legend(loc='best')

                plt.title(r"{}".format(stat_des), size=9)

            if col == 1:
                # ax.hist(settings.frequencies_dataframe_array[row], bins=100)
                # settings.frequencies_dataframe_array = settings.frequencies_dataframe_array.dropna(subset=['mean'], inplace=True)
                if remove_hist_edge:
                    lower_quant = dfreq.quantile(settings.lower_hist_freq)['mean']
                    upper_quant = dfreq.quantile(settings.upper_hist_freq)['mean']
                    dfreq = dfreq[dfreq['mean']>lower_quant]
                    dfreq = dfreq[dfreq['mean']<upper_quant]
                
                dfreq = dfreq[dfreq['mean'].notna()]
                
                ax.hist(dfreq, bins=100)
                plt.title(r"{}".format(hist_des), size=9)

    fig.tight_layout(pad=.5, h_pad=1)
    plt.show()


def calculate_featuredataframe():
    # print("-- start graph feature --")
    # rawboundary_dataframe = settings.current_rawboundary_dataframe.copy()
    rawboundary_dataframe = settings.frequency_dataframe.copy()
    data_feature = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).mean().rename(columns={'eng_value':'avg'})
    data_feature['std'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).std()
    data_feature['count'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).count()
    data_feature['min'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).min()
    data_feature['max'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).max()
    data_feature['q1'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).quantile(.25)
    data_feature['q2'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).quantile(.5)
    data_feature['q3'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).quantile(.75)
    data_feature['skew'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=settings.feature_frequency)).skew()
    # data_feature['kurtosis'] = rawboundary_dataframe.groupby(pd.Grouper(key='utc', freq=freq)).apply(pd.DataFrame.kurtosis)
    data_feature['lost_state'] = pd.isna(data_feature['avg'])
    # print(data_feature)

    # change Nan to -9999
    # data_feature['avg'] = data_feature['avg'].fillna(-9999)
    # data_feature['count'] = data_feature['count'].replace(0,-9999)
    # data_feature['std'] = data_feature['std'].fillna(-9999)
    # data_feature['min'] = data_feature['min'].fillna(-9999)
    # data_feature['max'] = data_feature['max'].fillna(-9999)
    # data_feature['q1'] = data_feature['q1'].fillna(-9999)
    # data_feature['q2'] = data_feature['q2'].fillna(-9999)
    # data_feature['q3'] = data_feature['q3'].fillna(-9999)
    # data_feature['skew'] = data_feature['skew'].fillna(-9999)
    # data_feature['kurtosis'] = data_feature['kurtosis'].fillna(-9999)

    # interporation
    orders = 1
    data_feature['avg'] = data_feature['avg'].interpolate(method='polynomial', order=orders)
    data_feature['count'] = data_feature['count'].replace(0,np.nan)
    data_feature['count'] = data_feature['count'].interpolate(method='polynomial', order=orders)
    data_feature['std'] = data_feature['std'].interpolate(method='polynomial', order=orders) # std ใช้ n-1 ดังนั้น n=1,0 std=nan
    data_feature['min'] = data_feature['min'].interpolate(method='polynomial', order=orders)
    data_feature['max'] = data_feature['max'].interpolate(method='polynomial', order=orders)
    data_feature['q1'] = data_feature['q1'].interpolate(method='polynomial', order=orders)
    data_feature['q2'] = data_feature['q2'].interpolate(method='polynomial', order=orders)
    data_feature['q3'] = data_feature['q3'].interpolate(method='polynomial', order=orders)
    data_feature['skew'] = data_feature['skew'].interpolate(method='polynomial', order=orders) # skew = nan เมื่อ n=1,0

    # change Nan to -9999 : for the case, index is 0 -> count=1 so std is nan 
    data_feature['std'] = data_feature['std'].fillna(0)
    data_feature['skew'] = data_feature['skew'].fillna(0)

    data_feature = data_feature.reset_index()
    settings.feature_dataframe = data_feature

    # print("---- data feature ----")
    # print(data_feature)

def show_graphfeature():
    data_feature = settings.feature_dataframe.copy()
    rawboundary_dataframe = settings.current_rawboundary_dataframe.copy()
    
    data_feature = data_feature.sort_values(by=['utc'])
    rawboundary_dataframe = rawboundary_dataframe.sort_values(by=['utc'])
    fig = plt.figure(figsize=(15,10))
    plt.gcf().canvas.set_window_title('Statistical Feature') 
    gs = GridSpec(nrows=4, ncols=1, height_ratios=[1,1,.5,.5])

    ax0 = fig.add_subplot(gs[0,0])
    ax0.plot(rawboundary_dataframe['utc'],rawboundary_dataframe['eng_value'], label='raw data : {}'.format(settings.tm_name.upper()))
    ax0.legend(loc='best')

    ax1 = fig.add_subplot(gs[1,0])
    ax1.plot(data_feature['utc'], data_feature['avg'], label='avg {}'.format(settings.feature_frequency))
    ax1.legend(loc='best')

    color = 'tab:red'
    ax2 = fig.add_subplot(gs[2,0])
    ax2.plot(data_feature['utc'], data_feature['std'], color=color, alpha=0.7,  label='std')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper left')

    color = 'tab:blue'
    ax3 = ax2.twinx()
    ax3.plot(data_feature['utc'], data_feature['count'], color=color, alpha=0.7, label='count')
    ax3.tick_params(axis='y', labelcolor=color)
    ax3.legend(loc='upper right')


    ax4 = fig.add_subplot(gs[3,0])
    ax4.plot(data_feature['utc'], data_feature['q1'], label='q1')
    ax4.plot(data_feature['utc'], data_feature['q2'], label='q2')
    ax4.plot(data_feature['utc'], data_feature['q3'], label='q3')
    ax4.plot(data_feature['utc'], data_feature['max'], label='max')
    ax4.plot(data_feature['utc'], data_feature['min'], label='min')
    ax4.legend(loc='best')

    fig.tight_layout(pad=.5, h_pad=2)
    plt.show()

