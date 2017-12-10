'''
Created on Dec 1, 2017

@author: Clark
'''

import urllib.request, urllib.parse
import os, time
import argparse

from datetime import datetime
import pandas as pd
import numpy as np

# def getFacebook (df_f, date, company):
#     likes = 0
#     dislikes = 0
#     result = df_f.loc[(df_f.index.get_level_values('date') == date) & (df_f.index.get_level_values('company') == company)]
#     if (result.empty != True):
#         likes = result['likes']
#         dislikes = result['dislikes']
# 
#     return likes, dislikes

def getFacebook (df_f, index):
    likes = 0
    dislikes = 0
    try:
        result = df_f.loc[index,:]
        if (result.empty != True):
            likes = result['likes']
            dislikes = result['dislikes']
        return likes, dislikes
    except KeyError:
        return likes, dislikes


def getTwitter (df_t, index):
    likes = 0
    try:
        result = df_t.loc[index,:]
        if (result.empty != True):
            likes = result['likes']
        return likes
    except KeyError:
        return likes    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--price', help='price file')
    parser.add_argument('-f', '--facebook', help='facebook file')
    parser.add_argument('-t', '--twitter', help='twitter')   

         
    # ^DJI, MMM, AXP, AAPL, BA, CAT, CVX, CSCO, KO, DWDP, XOM, GE, GS, HD, IBM, INTC, JNJ, JPM, MCD, MRK, MSFT, NKE, PFE, PG, TRV, UNH, UTX, VZ, V, WMT, DIS
    parser.print_help()

    args = parser.parse_args()

    price = str(args.price)
    facebook = str(args.facebook)
    twitter = str(args.twitter)

    start_time = datetime.now()
    print('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') )
        
    df_p = pd.read_csv(price, encoding = "utf-8", parse_dates=["date"],
    date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
#     df_p = df_p.set_index('date', drop=False)
    df_p.set_index(['date', 'company'], inplace=True)
    df_p = df_p.sort_index()
#     df_p = df_p.sort_values(['date', 'company'], ascending=True)
    
    df_f = pd.read_csv(facebook, encoding = "utf-8", parse_dates=["date"],
    date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    df_f.set_index(['date', 'company'], inplace=True)
    df_f = df_f.groupby(['date', 'company']).sum()
#     df_f = df_f.sort_index()       
#     df_f = df_f.sort_values(['date', 'company'], ascending=True)
    
    df_t = pd.read_csv(twitter, encoding = "utf-8", parse_dates=["date"],
    date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    df_t.set_index(['date', 'company'], inplace=True)
    df_t = df_t.groupby(['date', 'company']).sum()
#     df_t = df_t.sort_index()
#     df_t = df_t.sort_values(['date', 'company'], ascending=True)
    
    df_p['fblikes'] = 0
    df_p['fbdislikes'] = 0
    df_p['twittelikes'] = 0

    for index, row in df_p.iterrows():
#         fblikes, fbdislikes = getFacebook(df_f, row['date'], row['company'])
        fblikes, fbdislikes = getFacebook(df_f, index)
        twittelikes = getTwitter(df_t, index)
        
        if (fblikes > 0 or fbdislikes > 0 or twittelikes>0):
            print ('index=%s, fblikes=%i, fbdislikes=%i, twittelikes=%i' \
               %(index, fblikes, fbdislikes, twittelikes))
            df_p.at[index, 'fblikes'] = fblikes
            df_p.at[index, 'fbdislikes'] = fbdislikes
            df_p.at[index, 'twittelikes'] = twittelikes
    

    df_p.to_csv('./new_file.csv', sep=',', encoding='utf-8')        
    
    end_time = datetime.now()
    print('Task end at:' + datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S') )
