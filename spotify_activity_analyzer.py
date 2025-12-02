import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn
import numpy as np

seaborn.set()

def ms2hr(ms_val):
    return ms_val / (1000 * 60 * 60)

def load_over_time(df):
    df['endTime'] = pd.to_datetime(df['endTime'])
    df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))

    df_time = df[['endTime', 'msPlayed']]

    df_time_sum = df_time.groupby(['endTime'], as_index=False).agg({'msPlayed': 'sum'})
    df_time_sum['hrPlayed'] = df_time_sum['msPlayed'] / (1000 * 60 * 60)

    return df_time_sum

def plot_df(df, x, y, title=None, y_label=None):
    fig, ax = plt.subplots(1, 1)
    ax.bar(x, y, data=df)

    if title is not None:
        ax.set_title(title)
    if y_label is not None:
        ax.set_ylabel(y_label)

    fmt_month = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_month)

    fmt_day = mdates.DayLocator()
    ax.xaxis.set_minor_locator(fmt_day)

    ax.grid(True)

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

    # print(df_week_sum)

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

def top_artists(df, top=10, date_desc=''):
    # print("Top Artists")
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
    ax.set_title(f'Top {top} Artists by No. of Streams {date_desc}')
    ax.set_ylabel('No. of Streams')

    ax2.set_ylabel('Stream Time (Hr)')
    fig.autofmt_xdate()

    # print(df_top)
    return df_top

def top_tracks(df, top=10, date_desc=''):
    # print("Top Tracks")
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
    ax.set_title(f'Top {top} Tracks by No. of Streams {date_desc}')
    ax.set_ylabel('No. of Streams')

    ax2.set_ylabel('Stream Time (Hr)')
    fig.autofmt_xdate()

    # print(df_top)
    return df_top

def top_artists_history(df, top_artists_df=10, date_desc=''):
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
    ax.set_title(f'Top {len(top_artists_df)} Artists Streaming History {date_desc}')
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

def top_artists_most_days(df, top=10, date_desc=''):
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
    ax.set_title(f'Top {top} Artists by Most Days Listened {date_desc}')
    ax.set_ylabel('No. of Days')
    bar1 = ax.bar(df['artistName'],df['noDays'],width,color='r')
    fig.autofmt_xdate()
    
    return df

def choose_date_range(df):
    while True:
        print("Choose Date Range for Analysis:")
        print("1. Full History")
        print("2. Choose a Date Range")
        print("3. Choose a Specific Year")
        print("4. Choose a Specific Month")
        print("5. Exit")
        choice = input("Select an option (1-5): ")
        df['endTime'] = pd.to_datetime(df['endTime'])
        if choice == '1':
            return 1,df,f'Full History'
        
        elif choice == '2':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            if start_date not in df['endTime'].dt.strftime('%Y-%m-%d').values:
                print("Error: Start date not in data range.")
                continue
            end_date = input("Enter end date (YYYY-MM-DD): ")
            if end_date not in df['endTime'].dt.strftime('%Y-%m-%d').values:
                print("Error: End date not in data range.")
                continue
            if start_date > end_date:
                print("Error: Start date must be before end date.")
                continue
            return 1,df[(df['endTime'] >= start_date) & (df['endTime'] <= end_date)],f'from {start_date} to {end_date}'
        
        elif choice == '3':
            year = input("Enter year (YYYY): ")
            if year not in df['endTime'].dt.strftime('%Y').values:
                print("Error: Year not in data range.")
                continue
            return 1,df[df['endTime'].dt.year == int(year)],f'for the year {year}'
        
        elif choice == '4':
            year = input("Enter year (YYYY): ")
            if year not in df['endTime'].dt.strftime('%Y').values:
                print("Error: Year not in data range.")
                continue
            month = input("Enter month (1-12): ")
            if month.zfill(2) not in df['endTime'].dt.strftime('%m').values[df['endTime'].dt.strftime('%Y') == year]:
                print("Error: Month not in data range for the specified year.")
                continue
            return 1,df[(df['endTime'].dt.year == int(year)) & (df['endTime'].dt.month == int(month))],f'for {year}-{month.zfill(2)}'
        
        elif choice == '5':
            print("Exiting...")
            return 0,df,''
    
def main(stream_file_list):
    while True:
        # print(stream_file_list)
        df = file2df(stream_file_list)
        df.rename(columns={'ts':'endTime','master_metadata_album_artist_name':'artistName',
                        'master_metadata_track_name': 'trackName','ms_played':'msPlayed'}, 
                        inplace=True)
        
        end, df_date, date_desc = choose_date_range(df)

        if end == 0:
            exit(0)
        else:
            # print(df)
            df_listen_time = load_over_time(df_date)
            # print(df_listen_time)
            plot_df(df_listen_time, 'endTime', 'hrPlayed',
                    title=f"Listening time to Spotify streams per day: {date_desc}",
                    y_label='Hours [h]')
            df_avg_day = avg_day_load(df_date)
            # print(df_avg_day)
            df_top_artists = top_artists(df_date,10, date_desc)
            # print(df_top_artists)
            df_top_tracks = top_tracks(df_date,10, date_desc)
            # print(df_top_tracks)
            df_top_artists_history = top_artists_history(df_date,df_top_artists.head(5), date_desc)
            # print(df_top_artists_history)
            df_top_artists_most_days = top_artists_most_days(df_date,10, date_desc)
            # print(df_top_artists_most_days)
            plt.show()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(base_dir, 'Spotify Extended Streaming History')
    all_files = [os.path.join(base_dir, f) for f in os.listdir(base_dir)
                 if f.startswith("Streaming_History_") and f.lower().endswith('.json')]
    # for file in all_files:
    #     print(f"File found: {file}")

    if all_files:
        main(all_files)
    else:
        print(f"No JSON file found or no file with the naming conversion Streaming_History_Audio.json found")