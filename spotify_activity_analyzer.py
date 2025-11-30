import pandas as pd
import os
import re
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import seaborn

seaborn.set()

def ms2hr(ms_val):
    return ms_val / (1000 * 60 * 60)

def listen_time_per_day(df):
    df['endTime'] = pd.to_datetime(df['endTime'])
    df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime('%Y-%m-%d'))
    df_time = df[['endTime', 'msPlayed']]
    df_time_sum = df_time.groupby(['endTime'], as_index=False).agg({'msPlayed': 'sum'}) 
    
    df_time_sum['hrPlayed'] = ms2hr(df_time_sum['msPlayed'])

    fig, ax = plt.subplots(1,1)
    ax.bar('endTime', 'hrPlayed', data=df_time_sum)
    ax.set_title('Spotify Listening Time Per Day')
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours Played')
    fmt_month = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_month)
    ax.grid(True)
    fig.autofmt_xdate()

    return df_time_sum

def avg_day_load(df):
    df['endTime'] = pd.to_datetime(df['endTime'])
    df['date'] = pd.to_datetime(df['endTime'].dt.strftime('%Y-%m-%d'))
    df = df.groupby(['date'],as_index=True).agg({'endTime':'count', 'msPlayed':'sum'})
    df = df.asfreq('D',fill_value=0)
    df.reset_index(level=0,inplace=True)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day_types = pd.CategoricalDtype(categories=days, ordered=True)
    df['weekday'] = df['date'].dt.day_name()
    df['weekday2'] = df['weekday'].astype(day_types)
    df['weekday'] = df['weekday'].astype(day_types)

    df_week_sum = df.groupby('weekday',as_index=True) \
        .agg({'weekday2':'count','endTime':'sum','msPlayed':'sum'}) \
        .rename(columns={'endTime':'noStreams','weekday2':'dayCount'})
    
    df_week_sum['hrPlayed'] = df_week_sum['msPlayed'] / (1000 * 60 * 60)
    df_week_sum['hrPlayedAvg'] = df_week_sum['hrPlayed'] / df_week_sum['dayCount']
    df_week_sum['noStreamsAvg'] = df_week_sum['noStreams'] / df_week_sum['dayCount']
    df_week_sum['lenStreamsAvgMin'] = df_week_sum['msPlayed'] / df_week_sum['noStreams'] / (1000 * 60)

    print(df_week_sum)

    df_week_sum = df_week_sum.drop(columns=['msPlayed','hrPlayed','noStreams','dayCount'])

    fig = plt.figure()
    ax = fig.add_subplot(231)
    ax2 = fig.add_subplot(232)
    ax3 = fig.add_subplot(233)

    ax.axis('equal')
    ax.pie(df_week_sum['hrPlayedAvg'],labels=days,autopct='%1.2f%%')
    ax.set_title('Avg Stream Time per Day')

    ax2.axis('equal')
    ax2.pie(df_week_sum['noStreamsAvg'],labels=days,autopct='%1.2f%%')
    ax2.set_title('Avg No. of Streams per Day')

    ax3.axis('equal')
    ax3.pie(df_week_sum['lenStreamsAvgMin'],labels=days,autopct='%1.2f%%')
    ax3.set_title('Avg Stream Length per Day')

    axb = fig.add_subplot(234)
    axb.bar(days,df_week_sum['hrPlayedAvg'])
    axb.set_ylabel('Hours Played')

    axb2 = fig.add_subplot(235)
    axb2.bar(days,df_week_sum['noStreamsAvg'])
    axb2.set_ylabel('No. of Streams')

    axb3 = fig.add_subplot(236)
    axb3.bar(days,df_week_sum['lenStreamsAvgMin'])
    axb3.set_ylabel('Avg Stream Length (Min)')
    fig.autofmt_xdate()

    return df_week_sum

def file2df(stream_file_list):
    dfs = []
    for f_name in stream_file_list:
         with open(f_name, encoding="utf-8") as f:
            df_from_json = pd.json_normalize(json.loads(f.read()))
            dfs.append(df_from_json)

    df = pd.concat(dfs, sort=False)
    return df 

def main(stream_file_list):
    print(stream_file_list)
    df = file2df(stream_file_list)
    df.rename(columns={'ts':'endTime','ms_played':'msPlayed'}, inplace=True)
    print(df)
    df2 = listen_time_per_day(df)
    print(df2)
    df3 = avg_day_load(df)
    print(df3)
    plt.show()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir)
                 if f.startswith("Streaming_History_Audio") and f.lower().endswith('.json')]
    print(f"All files found: {all_files}")
    if all_files:
        main(all_files)
    else:
        print(f"No JSON file found or no file with the naming conversion StreamingHistory_.json found")