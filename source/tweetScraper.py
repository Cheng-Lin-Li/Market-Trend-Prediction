#!/usr/bin/env python
# encoding: utf-8

# scrape the offcial Titter accounts of Dow components
# Output: json, csv, json line
# Combine the total favorates and retweets per company per day

import tweepy  # https://github.com/tweepy/tweepy
import csv
import json
import sys
from datetime import date, timedelta, datetime
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')

# Twitter API credentials
consumer_key = "WkmvAytt1DEWva2VukcqACVtK"
consumer_secret = "jy8D7yESo1KrUc0EgIXwVWw4IUHvSy2AgQzsMIXMUb6UtM0S9p"
access_key = "447676855-FbQsPAuLttxllF8TB4eK6CV8keYZk7BEW6UCQDuw"
access_secret = "NaFfyZMKHCP9zCpm88PcoGvOh7ZQNP3kUlPaxUjS44Vxz"

# consumer_key = "46E4JNzKWLXlzx9Nk2l2W1si8"
# consumer_secret = "PT7RO2gbxY82pQytAemwElSBNXafj4UAuIVGLTIBJBDUUNXKbg"
# access_key = "721719816801751040-Epz6Y0TbfyoM4l89D02mCgFoNz5sCia"
# access_secret = "ryxV6c3qFo4BWQa96hu3HhV1c8w4ZL9urc8EqvRQpXrbB"

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


def get_all_tweets(screen_name):
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
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        # all subsequent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200,
                                       max_id=oldest, exclude_replies=True)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print "...%s tweets downloaded so far" % (len(alltweets))

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
    with open('./csv/%s.csv' % screen_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["created_at", "company", "url", "text", "retweets", "likes", "id"])
        writer.writerows(outtweets)

    # compose dictionary for outputting json
    data = []
    for tweet in outtweets:
        row = {
            "created_at": str(tweet[0]),
            "company": tweet[1],
            "url": tweet[2],
            "text": tweet[3],
            "re_tweets": tweet[4],
            "likes": tweet[5],
            "id": tweet[6]
        }
        data.append(row)

    # write the json
    with open('./json/%s.json' % screen_name, 'wb') as outfile:
        json.dump(data, outfile)

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
        "doc_id": hashlib.sha256(line[2]).hexdigest(),
        "timestamp_crawl": str(line[0]),
        "url": line[2],
        "raw_content": rawContent % ("tweets of " + line[1] + " on " + str(line[0]),
                                     line[1], line[2], line[3], line[0], line[5], line[4])
    }
    jlFile.write(json.dumps(row, separators=(',', ': ')) + "\n")


d1 = date(2016, 8, 1)
d2 = date(2017, 10, 31)
# generate a list containing all the dates in between d1 and d2
dateRange = [d1 + timedelta(days=x) for x in range((d2 - d1).days + 1)]

allData = {}
for acc in accounts:
    allData[comDic[acc]] = get_all_tweets(acc)

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
with open("twitter.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "company", "re_tweets", "likes"])
    writer.writerows(csvLst)

# if __name__ == '__main__':
#     # pass in the username of the account you want to download
#     get_all_tweets(screen_name)
