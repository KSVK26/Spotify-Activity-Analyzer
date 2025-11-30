import pandas as pd
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import seaborn

seaborn.set()

def ms2hr(ms_val):
    return ms_val / (1000 * 60 * 60)

def listen_time_per_day(df,plot=False):
    df['endTime'] = pd.to_datetime(df['endTime'])
    df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime('%Y-%m-%d'))
    df_time = df[['endTime', 'msPlayed']]
    df_time_sum = df_time.groupby(['endTime'], as_index=False)\
        .agg({'msPlayed': 'sum'}) 
    
    df_time_sum['hrPlayed'] = ms2hr(df_time_sum['msPlayed'])

    if plot:
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
    df2 = listen_time_per_day(df,plot=True)
    print(df2)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[1:])