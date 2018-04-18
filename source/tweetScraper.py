#!/usr/bin/env python
# encoding: utf-8

# scrape the offcial Titter accounts of Dow components
# Output: json, csv, json line
# Combine the total favorates and retweets per company per day
# Revised by: Cheng-Lin Li
# Modify date: April, 17, 2018
# To make print working for Python2/3
from __future__ import print_function

import tweepy  # https://github.com/tweepy/tweepy
import csv
import json
import sys, os
import argparse
from datetime import date, timedelta, datetime
import hashlib
from joblib.test.test_parallel import consumer

companies = "3M,American Express,Apple,Boeing,Caterpillar,Chevron,Cisco Systems," \
            "Coca-Cola,DowDuPont,ExxonMobil,General Electric,Goldman Sachs,IBM," \
            "Intel,Johnson & Johnson,JPMorgan Chase,McDonald's,Merck,Microsoft,Nike," \
            "Pfizer,Procter & Gamble,The Home Depot,Travelers,United Technologies," \
            "UnitedHealth Group,Verizon,Visa,Walmart,Walt Disney".split(",")

accounts = "3M,AmericanExpress,AppleSupport,Boeing,CaterpillarInc,Chevron,Cisco," \
           "CocaCola,DowDuPontCo,exxonmobil,generalelectric,GoldmanSachs,IBM,intel," \
           "JNJNews,jpmorgan,McDonalds,Merck,Microsoft,Nike,pfizer,ProcterGamble," \
           "HomeDepot,Travelers,UTC,UnitedHealthGrp,verizon,Visa,Walmart,DisneyStudios".split(",")

comDic = dict(zip(accounts, companies))


def get_all_tweets(screen_name, since, until, limit, consumer_key, consumer_secret, access_key, access_secret):
    # Twitter only allows access to a users most recent 3200 tweets with this method

    print("collecting tweets from: " + screen_name)
    # oldest = "925854293512589312"
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=limit)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        # all subsequent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=limit,
                                       max_id=oldest, exclude_replies=True)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print ("...%s tweets downloaded so far" % (len(alltweets)))

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[
        tweet.created_at,
        comDic[screen_name],
        "https://twitter.com/" + screen_name + "/status/" + tweet.id_str,
        tweet.text.encode("utf-8"),
        tweet.retweet_count,
        tweet.favorite_count,
        tweet.id_str]
        for tweet in alltweets]

    # write the csv
    print("writing the csv for: %s" % screen_name)
    result_dir = 'csv/'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)    
    with open('./%s%s.csv' % (result_dir, screen_name), 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["created_at", "company", "url", "text", "retweets", "likes", "id"])
        writer.writerows(outtweets)

    # compose dictionary for outputting json
    data = []
    for tweet in outtweets:
        row = {
            "created_at": str(tweet[0]),
            "company": str(tweet[1]),
            "url": str(tweet[2]),
            "text": str(tweet[3]),
            "re_tweets": str(tweet[4]),
            "likes": int(tweet[5]),
            "id": str(tweet[6])
        }
        data.append(row)

    # write the json
    result_dir = 'json/'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    with open('./%s%s.json' % (result_dir, screen_name), 'w', encoding='utf8') as outfile:
        json.dump(list(data), outfile)

    return outtweets


jlFile = open("twitter.jl", "w")

docID = 0  # auto increasing doc ID
rawContent = "<!DOCTYPEhtml><html><head><meta charset='UTF-8'>" \
             "<title>%s</title></head><body>" \
             "<ul><li class='company'>%s</li>" \
             "<li class='url'>%s</li>" \
             "<li class='text'>%s</li>" \
             "<li class='creat_time'>%s</li>" \
             "<li class='likes'>%s</li>" \
             "<li class='retweets'>%s</li>" \
             "</ul></body></html>"


def writeJL(line):
    global docID
    docID += 1
    row = {
        "doc_id": hashlib.sha256(str(line[2]).encode('utf-8')).hexdigest(),
        "timestamp_crawl": str(line[0]),
        "url": str(line[2]),
        "raw_content": rawContent % ("tweets of " + str(line[1]) + " on " + str(line[0]),
                                     str(line[1]), str(line[2]), str(line[3]), str(line[0]),
                                      str(line[5]), str(line[4]))
    }
    jlFile.write(json.dumps(row, separators=(',', ': ')) + "\n")



if __name__ == '__main__':
    # Set crawler target and parameters.
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--since', help='Set the start date you want to crawling. Format: \'yyyymmdd\'')
    parser.add_argument('-u', '--until', help='Set the end date you want to crawling. Format: \'yyyymmdd\'')
    parser.add_argument('-l', '--limit', help='This is the maximum number of messages, limitation is 200')

    parser.add_argument('-ck', '--c_key', help='consumer key')    
    parser.add_argument('-cs', '--c_secret', help='consumer secret')
    parser.add_argument('-ak', '--a_key', help='access key')    
    parser.add_argument('-as', '--a_secret', help='access secret')        

         
    parser.print_help()
    args = parser.parse_args()

    since = str(args.since)
    until = str(args.until)
    
    if args.limit is not None:
        limit = int(args.limit)
        if limit > 200: limit = 200
    else:
        limit = 200

    consumer_key = str(args.c_key)
    consumer_secret = str(args.c_secret)
    access_key = str(args.a_key)
    access_secret = str(args.a_secret)        
    print ('yyyy=%d, mm=%d, dd=%d'%(int(since[:4]), int(since[4:6]), int(since[6:8])))
    d1 = date(int(since[:4]), int(since[4:6]), int(since[6:8]))
    d2 = date(int(until[:4]), int(until[4:6]), int(until[6:8]))
    # generate a list containing all the dates in between d1 and d2
    dateRange = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]
    
    allData = {}
    for acc in accounts:
        allData[comDic[acc]] = get_all_tweets(acc, since, until, limit, consumer_key, consumer_secret, access_key, access_secret)
    
    csvLst = []
    for date in dateRange:
        for com in companies:
            retweets = 0
            likes = 0
            for tweet in allData[com]:
                if tweet[0].date() == date:
                    writeJL(tweet)  # write one json line
                    retweets += int(tweet[4])
                    likes += int(tweet[5])
            csvLst.append([date, com, retweets, likes])
    
    print("##### writing the .csv file in a time sequence #####")
    with open("twitter.csv", "w", encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(["date", "company", "re_tweets", "likes"])
        writer.writerows(csvLst)
    
