import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import seaborn
import numpy as np

seaborn.set()

def ms2hr(ms_val):
    return ms_val / (1000 * 60 * 60)

# def listen_time_per_day(df):
#     df['endTime'] = pd.to_datetime(df['endTime'])
#     df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime('%Y-%m-%d'))
#     df_time = df[['endTime', 'msPlayed']]
#     df_time_sum = df_time.groupby(['endTime'], as_index=False).agg({'msPlayed': 'sum'}) 
    
#     df_time_sum['hrPlayed'] = ms2hr(df_time_sum['msPlayed'])

#     fig, ax = plt.subplots(1,1)
#     ax.bar('endTime', 'hrPlayed', data=df_time_sum)
#     ax.set_title('Spotify Listening Time Per Day')
#     ax.set_xlabel('Date')
#     ax.set_ylabel('Hours Played')
#     fmt_month = mdates.MonthLocator(interval=1)
#     ax.xaxis.set_major_locator(fmt_month)
#     ax.grid(True)
#     fig.autofmt_xdate()

#     return df_time_sum

def load_over_time(df):
    # convert string datetime to datetime format
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date
    df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))

    # get only date and duration of stream
    df_time = df[['endTime', 'msPlayed']]

    # sum daily hours of spotify 
    df_time_sum = df_time.groupby(['endTime'], as_index=False).agg({'msPlayed': 'sum'})
    df_time_sum['hrPlayed'] = df_time_sum['msPlayed'] / (1000 * 60 * 60)

    #df_time_sum.info()
    return df_time_sum

def plot_df(df, x, y, title=None, y_label=None):
    fig, ax = plt.subplots(1, 1)
    ax.bar(x, y, data=df)

    if title is not None:
        ax.set_title(title)
    if y_label is not None:
        ax.set_ylabel(y_label)

    # Major ticks every 6 months.
    fmt_month = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_month)

    # Minor ticks every month.
    fmt_day = mdates.DayLocator()
    ax.xaxis.set_minor_locator(fmt_day)

    ax.grid(True)

    # Rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them.
    fig.autofmt_xdate()

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

def top_artists(df, top=10):
    print("Top Artists")
    df_top=df.groupby('artistName',as_index=False) \
        .agg({'endTime':'count','msPlayed':'sum'}) \
        .rename(columns={'endTime':'noStreams','msPlayed':'streamTimeMs'})
    df_top['streamTimeHr'] = ms2hr(df_top['streamTimeMs'])
    df_top = df_top.sort_values(by=['noStreams'], ascending=False)
    df_top = df_top.head(top)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    ax2.grid(False)

    width = 0.27
    ind = np.arange(len(df_top))

    bar1 = ax.bar(ind, df_top['noStreams'], width, color = 'r', label='No. of Streams')
    bar2 = ax2.bar(ind + width, df_top['streamTimeHr'], width, color = 'b', label='Stream Time (Hr)')
    fig.legend(loc='upper right')

    ax.set_xticks(ind + width)

    ax.set_xticklabels(df_top['artistName'])
    ax.set_title(f'Top {top} Artists by No. of Streams')
    ax.set_ylabel('No. of Streams')

    ax2.set_ylabel('Stream Time (Hr)')
    fig.autofmt_xdate()

    print(df_top)
    return df_top

def top_tracks(df, top=10):
    print("Top Tracks")
    df_top=df.groupby(['artistName','trackName'],as_index=False) \
        .agg({'endTime':'count','msPlayed':'sum'}) \
        .rename(columns={'endTime':'noStreams','msPlayed':'streamTimeMs'})
    df_top['streamTimeHr'] = ms2hr(df_top['streamTimeMs'])
    df_top = df_top.sort_values(by=['noStreams'],ascending=False)
    df_top = df_top.head(top)
    df_top['fullName'] = df_top['artistName'] + " - " + df_top['trackName']

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    ax2.grid(False)

    width = 0.27
    ind = np.arange(len(df_top))

    bar1 = ax.bar(ind,df_top['noStreams'], width, color = 'r', label='No. of Streams')
    bar2 = ax2.bar(ind + width, df_top['streamTimeHr'], width, color = 'b', label='Stream Time (Hr)')
    fig.legend(loc='upper right')

    ax.set_xticks(ind + width)
    ax.set_xticklabels(df_top['fullName'])
    ax.set_title(f'Top {top} Tracks by No. of Streams')
    ax.set_ylabel('No. of Streams')

    ax2.set_ylabel('Stream Time (Hr)')
    fig.autofmt_xdate()

    print(df_top)
    return df_top

def top_artists_history(df, top_artists_df=10):
    df_top = df[df['artistName'].isin(top_artists_df['artistName'])]
    df_top['endTime'] = pd.to_datetime(df_top['endTime'])

    df_top['date'] = pd.to_datetime(df_top['endTime'].dt.strftime('%Y-%m-%d'))
    df_top = df_top.groupby(['artistName','date'],as_index=False) \
        .agg({'endTime':'count'}) \
        .rename(columns={'endTime':'noStreams'})
    
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for artist in top_artists_df['artistName']:
        df_tmp = df_top[df_top['artistName'] == artist]
        ax.plot(df_tmp['date'],df_tmp['noStreams'],'-o',label=artist)
    ax.legend()
    ax.set_title(f'Top {len(top_artists_df)} Artists Streaming History')
    ax.set_ylabel("No. of Streams")

    return df_top

def file2df(stream_file_list):
    dfs = []
    for f_name in stream_file_list:
         with open(f_name, encoding="utf-8") as f:
            df_from_json = pd.json_normalize(json.loads(f.read()))
            dfs.append(df_from_json)

    df = pd.concat(dfs, sort=False)
    return df 

def top_artists_most_days(df, top=10):
    df = df.copy()
    df['endTime'] = pd.to_datetime(df['endTime'])
    df['date'] = pd.to_datetime(df['endTime'].dt.strftime('%Y-%m-%d'))
    df = df[['artistName', 'date']].drop_duplicates()

    df = df.groupby('artistName',as_index=False) \
        .agg({'date':'count'}) \
        .rename(columns={'date':'noDays'})
    df.sort_values(by=['noDays'],ascending=False,inplace=True)

    df = df.head(top)

    width = 0.7
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(f'Top {top} Artists by Most Days Listened')
    ax.set_ylabel('No. of Days')
    bar1 = ax.bar(df['artistName'],df['noDays'],width,color='r')
    fig.autofmt_xdate()
    
    return df
    
def main(stream_file_list):
    print(stream_file_list)
    df = file2df(stream_file_list)
    df.rename(columns={'ts':'endTime','master_metadata_album_artist_name':'artistName','master_metadata_track_name': 'trackName','ms_played':'msPlayed'}, inplace=True)
    print(df)
    df_listen_time = load_over_time(df)
    print(df_listen_time)
    plot_df(df_listen_time, 'endTime', 'hrPlayed',title=f"Listening time to Spotify streams per day: {df['endTime'].dt.strftime('%Y').iloc[1]} onwards",y_label='Hours [h]')
    df_avg_day = avg_day_load(df)
    print(df_avg_day)
    df_top_artists = top_artists(df,10)
    print(df_top_artists)
    df_top_tracks = top_tracks(df,10)
    print(df_top_tracks)
    df_top_artists_history = top_artists_history(df,df_top_artists.head(5))
    print(df_top_artists_history)
    df_top_artists_most_days = top_artists_most_days(df,10)
    print(df_top_artists_most_days)
    plt.show()

if __name__ == "__main__":
# TODO: Change json file fetching to get it from the Spotify Extended Streaming History folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir)
                 if f.startswith("Streaming_History_Audio") and f.lower().endswith('.json')]
    # print(f"All files found: {all_files}")
    if all_files:
        main(all_files)
    else:
        print(f"No JSON file found or no file with the naming conversion Streaming_History_Audio.json found")