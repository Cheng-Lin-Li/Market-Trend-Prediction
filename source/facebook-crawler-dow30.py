#!/usr/bin/env python
# encoding: utf-8
'''
facebook content crawler: By facebook graph API.

This is a content crawler for facebook via facebook graph API.

@author: Cheng-Lin Li a.k.a. Clark

@copyright:  2017 Cheng-Lin Li@University of Southern California. All rights reserved.

@license:    Licensed under the GNU v3.0. https://www.gnu.org/licenses/gpl

@contact:    clark.cl.li@gmail.com
@version:    1.1

@create:    October 22, 2017
@updated:   November 28, 2017

Reference:
    https://github.com/chenjr0719/Facebook-Page-Crawler/edit/master/Facebook_Page_Crawler.py

Enhance:
  1. Support Facebook Graph API 2.11
  2. Additional parameters for better control.
  3. add delay time for every request of post.
  4. encode with utf-8
  5. Add html mode for better JSON Lines CDR creation.
  6. Add reactions summary by single query to improve performance in html mode rather than counting each reaction in json mode.
  7. Add 'total' to summary the total counts of reactions of each post.
  8. Bug fix.

## Get summary reactions in one single query.
?fields=reactions.type(LIKE).limit(0).summary(1).as(like),
        reactions.type(WOW).limit(0).summary(1).as(wow),
        reactions.type(SAD).limit(0).summary(1).as(sad)
            
Facebook Graph API limitation:
    api call level restriction: 200 call per hour per user. (18 seconds a call in average.)
    page level: 4800 call per page per user per 24 hours

Graph API error code:
| Throttling Type             | At least                  | Error Code | 
|-----------------------------|---------------------------|------------|
|Application-level throttling | 200 calls/person/hour     |4           |
|Account-level throttling     | Not applicable            |17          |
|Page-level throttling        |4800 calls/person/24-hours |32          |
|Custom-level throttling      |Not applicable             |613         |
    
Getting the Access Token:
https://medium.com/towards-data-science/how-to-use-facebook-graph-api-and-extract-data-using-python-1839e19d6999
    To be able to extract data from Facebook using a python code you need to register as a developer on Facebook and then have an access token. 
    Here are the steps for it.
  1. Go to link developers.facebook.com, create an account there.
  2. Go to link developers.facebook.com/tools/explorer.
  3. Go to “My apps” drop down in the top right corner and select “add a new app”. 
      Choose a display name and a category and then “Create App ID”.
  4. Again get back to the same link developers.facebook.com/tools/explorer. 
      You will see “Graph API Explorer” below “My Apps” in the top right corner. From “Graph API Explorer” drop down, select your app.
  5. Then, select “Get Token”. From this drop down, select “Get User Access Token”. 
      Select permissions from the menu that appears and then select “Get Access Token.”
  6. Go to link developers.facebook.com/tools/accesstoken. Select “Debug” corresponding to “User Token”. 
      Go to “Extend Token Access”. This will ensure that your token does not expire every two hours.    
    
'''

import requests, os, time, json
import argparse, sys 
from functools import partial
from datetime import datetime
import urllib.parse

from multiprocessing import Pool

URL_HEADER = 'https://graph.facebook.com/v2.11/'
iMaxStackSize = 5000 #Change max recursion depth from default around 1000 to 5000

sys.setrecursionlimit(iMaxStackSize)

def getRequests(url, delay):

    requests_result = requests.get(url, headers={'Connection':'close'}).json()
    time.sleep(delay)

    return requests_result

def getFeedIds(feeds, feed_list, delay):

    feeds = feeds['feed'] if 'feed' in feeds else feeds

    for feed in feeds['data']:
        feed_list.append(feed['id'])
        if not stream:
            print('Feed found: ' + feed['id'] + '\n')
            #log.write('Feed found: ' + feed['id'] + '\n')
    
    if 'paging' in feeds and 'next' in feeds['paging']:
        feeds_url = feeds['paging']['next']
        feed_list = getFeedIds(getRequests(feeds_url, delay), feed_list, delay)

    return feed_list

def getComments(comments, comments_count, stream, delay):

    # If comments exist.
    comments = comments['comments'] if 'comments' in comments else comments
    if 'data' in comments:

        if not stream:
            comments_dir = 'comments/'
            if not os.path.exists(comments_dir):
                os.makedirs(comments_dir)

        for comment in comments['data']:

            comment_content = {
                'id': comment['id'],
                'user_id': comment['from']['id'],
                'user_name': comment['from']['name'] if 'name' in comment['from'] else None,
                'message': comment['message'],
                'like_count': comment['like_count'] if 'like_count' in comment else None,
                'created_time': comment['created_time']
            }

            comments_count+= 1

            if stream:
                print(comment_content)
            else:
                print('Processing comment: ' + comment['id'] + '\n')
                comment_file = open(comments_dir + comment['id'] + '.json', 'w')
                comment_file.write(json.dumps(comment_content, indent = 4))
                comment_file.close()
                #log.write('Processing comment: ' + feed_id + '/' + comment['id'] + '\n')

        # Check comments has next or not.
        if 'paging' in comments and 'next' in comments['paging']:
            comments_url = comments['paging']['next']
            comments_count = getComments(getRequests(comments_url, delay), comments_count, stream, delay)

    return comments_count

def getReactions(reactions, reactions_count_dict, stream, delay):

    # If reactions exist.
    reactions = reactions['reactions'] if 'reactions' in reactions else reactions
    if 'data' in reactions:

        if not stream:
            reactions_dir = 'reactions/'
            if not os.path.exists(reactions_dir):
                os.makedirs(reactions_dir)

        for reaction in reactions['data']:

            if reaction['type'] == 'LIKE':
                reactions_count_dict['like']+= 1
                reactions_count_dict['total']+= 1
            elif reaction['type'] == 'LOVE':
                reactions_count_dict['love']+= 1
                reactions_count_dict['total']+= 1
            elif reaction['type'] == 'HAHA':
                reactions_count_dict['haha']+= 1
                reactions_count_dict['total']+= 1
            elif reaction['type'] == 'WOW':
                reactions_count_dict['wow']+= 1
                reactions_count_dict['total']+= 1
            elif reaction['type'] == 'SAD':
                reactions_count_dict['sad']+= 1
                reactions_count_dict['total']+= 1
            elif reaction['type'] == 'ANGRY':
                reactions_count_dict['angry']+= 1
                reactions_count_dict['total']+= 1

            if stream:
                print(reaction)
            else:
                print('Processing reaction: ' + reaction['id'] + '\n')
                reaction_file = open(reactions_dir + reaction['id'] + '.json', 'w')
                reaction_file.write(json.dumps(reaction, indent = 4))
                reaction_file.close()
                #log.write('Processing reaction: ' + feed_id + '/' + reaction['id'] + '\n')

        # Check reactions has next or not.
        if 'paging' in reactions and 'next' in reactions['paging']:
            reactions_url = reactions['paging']['next']
            try:
                reactions_count_dict, reactions_content = getReactions(getRequests(reactions_url, delay), reactions_count_dict, stream, delay)
            except RuntimeError as re:
                if re.args[0] != 'maximum recursion depth exceeded':
                    # different type of runtime error
                    print('Oopsie: {}'.format(re.args[0]))
                    raise
                print('Sorry but this getReactions was not able to finish '
                      'analyzing the getReactions: {}'.format(re.args[0]))
                return reactions_count_dict, reaction          
                
            if 'data' in reactions_content:
                reaction['data'].append(reactions_content['data'])
                
    return reactions_count_dict, reaction

def getReactionSummary(reactions, reactions_count_dict, stream, delay):
    # If reactions exist.
    '''
    {
      "LIKE": {
        "data": [
        ],
        "summary": {
          "total_count": 2006,
          "viewer_reaction": "NONE"
        }
      },
      "LOVE": {
        "data": [
        ],
        "summary": {
          "total_count": 158,
          "viewer_reaction": "NONE"
        }
      },
      "id": "168597536563870_1495301963893414"
    }
        
    '''
    _like_ct = reactions['LIKE']['summary']['total_count']
    _love_ct = reactions['LOVE']['summary']['total_count']
    _haha_ct = reactions['HAHA']['summary']['total_count']
    _wow_ct = reactions['WOW']['summary']['total_count']
    _sad_ct = reactions['SAD']['summary']['total_count']
    _angry_ct = reactions['ANGRY']['summary']['total_count']    
    
    _total_ct = _like_ct + _love_ct + _haha_ct + _wow_ct + _sad_ct + _angry_ct 
               
    reactions_count_dict['like'] = _like_ct
    reactions_count_dict['love'] = _love_ct
    reactions_count_dict['haha'] = _haha_ct
    reactions_count_dict['wow'] = _wow_ct
    reactions_count_dict['sad'] = _sad_ct
    reactions_count_dict['angry'] = _angry_ct
    reactions_count_dict['total'] = _total_ct
        
    if stream:
        print(reactions)
    else:
        pass
                
    return reactions_count_dict, reactions

def getAttachments(attachments, attachments_content):

    # If attachments exist.
    attachments = attachments['attachments'] if 'attachments' in attachments else attachments
    if 'data' in attachments:
        attachments_content['title'] = attachments['data'][0]['title'] if 'title' in attachments['data'][0] else ''
        attachments_content['description'] = attachments['data'][0]['description'] if 'description' in attachments['data'][0] else ''
        attachments_content['target'] = attachments['data'][0]['target']['url'] if 'target' in attachments['data'][0] and 'url' in attachments['data'][0]['target'] else ''

    return attachments_content

def getFeed(target, get_reactions, stream, token, limit, delay, output, feed_id):

    feed_url = URL_HEADER + feed_id
    comments_count = 0
    attachments_content = {
        'title': '',
        'description': '',
        'target': ''
    }
    reactions_count_dict = {
        'like': 0,
        'love': 0,
        'haha': 0,
        'wow': 0,
        'sad': 0,
        'angry': 0,
        'total': 0
    }
    if not stream:
        feed_dir = feed_id + '/'
        if not os.path.exists(feed_dir):
            os.makedirs(feed_dir)

        os.chdir(feed_dir)

        print('\nProcessing feed: ' + feed_id + '\nAt: ' + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + '\n')
        log = open('../log', 'a')
        log.write('\nProcessing feed: ' + feed_id + '\nAt: ' + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + '\n')
        log.close()

    # For reactions.
    if get_reactions:


        if output == 'html':
            reactions_summary_url = feed_url + ('?fields=reactions.type(LIKE).limit(0).summary(1).as(LIKE),'
                                'reactions.type(LOVE).limit(0).summary(1).as(LOVE),'
                                'reactions.type(HAHA).limit(0).summary(1).as(HAHA),'
                                'reactions.type(WOW).limit(0).summary(1).as(WOW),'
                                'reactions.type(SAD).limit(0).summary(1).as(SAD),'
                                'reactions.type(ANGRY).limit(0).summary(1).as(ANGRY)') + '&'+ token            
            reactions_count_dict, reactions_content = getReactionSummary(getRequests(reactions_summary_url, delay), reactions_count_dict, stream, delay)
        else: #json format.
            # For comments.###########
            comments_url = feed_url + '?fields=comments.limit(' + str(limit) + ')&' + token
            comments_count = getComments(getRequests(comments_url, delay), 0, stream, delay)
            ##########################
            # For reactions.###########
            reactions_url = feed_url + '?fields=reactions.limit(' + str(limit) + ')&' + token            
            reactions_count_dict, reactions_content = getReactions(getRequests(reactions_url, delay), reactions_count_dict, stream, delay)
            #########################
            # For attachments. ######
            attachments_url = feed_url + '?fields=attachments&' + token
            attachments_content = getAttachments(getRequests(attachments_url, delay), attachments_content)
            #########################
            
    # For feed content.
    feed = getRequests(feed_url + '?' + token, delay)

    if 'message' in feed:
        feed_content = {
            'id': feed['id'],
            'message': feed['message'],
            'link': feed['link'] if 'link' in feed else None,
            'created_time': convertDatetime(feed['created_time']),
            'comments_count': comments_count
        }

        feed_content.update(attachments_content)

        if get_reactions:
            feed_content.update(reactions_count_dict)
            #Todo: Include all reactions into single file. So far only include first reaction, need to be enhanced.
#             feed_content.update({'reactions_content':reactions_content})

        if stream:
            print(feed_content)
        elif output == 'html':
            feed_file = open('../'+urllib.parse.quote_plus('http://www.facebook.com/')+feed_id, 'w', encoding='utf8')
            feed_file.write(getHTML(target, feed_content, indent = 0))
            feed_file.close()
            csv_file = open('../'+target+'-reaction_counts.csv', 'a', encoding='utf8')
            csv_file.write(getCSV(target, feed_content))
            csv_file.close()
            
        else: # output as json
            feed_file = open('../'+urllib.parse.quote_plus('http://www.facebook.com/')+feed_id + '.json', 'w', encoding='utf8')
            feed_file.write(json.dumps(feed_content, indent = 4))
            feed_file.close()

    if not stream:
        os.chdir('../')

def convertDatetime(dt):
    # convert date time format from '%Y-%m-%dT%H:%M:%S+0000' to '%Y-%m-%d %H:%M:%S'
    _dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S+0000')
    strDate = datetime.strftime(_dt, '%Y-%m-%d %H:%M:%S')
    return strDate

def convertDate(dt):
    # convert date time format from '%Y-%m-%d %H:%M:%S' to '%Y-%m-%d'
    _dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    strDate = datetime.strftime(_dt, '%Y-%m-%d')
    return strDate

def getCSV(target, dictObj):

    strDate = convertDate(dictObj['created_time'])
    likes = dictObj['haha']+dictObj['like']+dictObj['love']+dictObj['wow'];
    bads = dictObj['sad']+dictObj['angry'];
    output = strDate+','+convertToDow(target)+','+ str(likes)+','+ str(bads)+'\n'
    print( 'Facebook====>%s'%(output))

    return output

def getHTML(target, dictObj, indent):
    output = ('<!DOCTYPE html>'
      '<html>'
      '<head>'
      '<meta charset="UTF-8">'
      '<title> ' + convertToDow(target) + '</title>'
      '</head>'
      '<body>'
      '<ul>'
      '    <li class="company">company: ' + convertToDow(target) + '</li>'
      '</ul>'
      )    
    output += getHTMLItems(dictObj, indent)
    output += ('</body>'
      '</html>'
      )     
    return output

def getHTMLItems(dictObj, indent):
    output = ''
    output += '  '*indent + '<ul>\n'
    for k,v in dictObj.items():
        if isinstance(v, dict):
            output += '  '*indent + '<li class="' + k + '"> ' + k + ': ' + '</li>'
            output += getHTMLItems(v, indent+1)
        else:
            output += ' '*indent + '<li class="' + k + '"> ' + k + ': ' + ('None' if v is None else str(v)) + '</li>'
    output += '  '*indent + '</ul>\n'
    
    return output

def convertToDow(target):
    
    companydict = {'3m':'3M', 
                   'AmericanExpressUS':'American Express',
                    'AppleInc.HD': 'Apple',
                    'Boeing':'Boeing', 
                    'caterpillar':'Caterpillar', 
                    'Chevron':'Chevron',
                    'Cisco':'Cisco Systems',
                    'CocaColaUnitedStates':'Coca-Cola', 
                    'dupontco':'DowDuPont', 
                    'ExxonMobil':'ExxonMobil', 
                    'GE':'General Electric', 
                    'goldmansachs':'Goldman Sachs', 
                    'ibm':'IBM', 
                    'Intel':'Intel', 
                    'jnj':'Johnson & Johnson', 
                    'jpmorganchase':'JPMorgan Chase',
                    'McDonaldsUS':"McDonald's", 
                    'MerckInvents':'Merck', 
                    'Microsoft':'Microsoft',
                    'Nike':'Nike', 
                    'nikesportswear':'Nike',
                    'Pfizer':'Pfizer', 
                    'proctergamble':'Procter & Gamble', 
                    'homedepot':'The Home Depot', 
                    'travelers':'Travelers', 
                    'unitedtechnologiescorp':'United Technologies',
                    'unitedhealthgroup':'UnitedHealth Group', 
                    'Verizon':'Verizon', 
                    'VisaUnitedStates':'Visa', 
                    'Walmart':'Walmart', 
                    'Disney':'Walt Disney'}
    _target = target.strip()
    companyname = companydict.get(_target)
#     print ('target ="%s", companyname="%s"'%(_target, str(companyname)))
    if companyname == None:
        companyname = _target
    else:
        pass
    
    return companyname.strip()


def getTarget(target, since, until, token, limit, get_reactions, stream, delay, output):

    if not stream:
        target_dir = target + '/'
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        os.chdir(target_dir)

        log = open('log', 'w')
        start_time = datetime.now()
        execution_start_time = time.time()
        print('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + target + '\nSince: ' + since + '\nUntil: ' + until + '\n')
        log.write('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + target + '\nSince: ' + since + '\nUntil: ' + until + '\n')
        log.close()

    #Get list of feed id from target.
    _since = str(datetime.strptime(since, '%Y-%m-%d %H:%M:%S').timestamp())
    _until = str(datetime.strptime(until, '%Y-%m-%d %H:%M:%S').timestamp())
    feeds_url = URL_HEADER + target + '/?fields=feed.limit(' + str(limit) + ').since(' + _since + ').until(' + _until + '){id}&' + token
    feed_list = getFeedIds(getRequests(feeds_url, delay), [], delay)

    if not stream:
        feed_list_file = open('feed_ids', 'w')
        for id in feed_list:
            feed_list_file.write(id + '\n')
        feed_list_file.close()

    #Get message, comments and reactions from feed.
    # getFeed is a function to be used in map
    func = partial(getFeed, target, get_reactions, stream, token, limit, delay, output) # multiple arguments to map function
    target_pool = Pool()
    target_pool.map(func, feed_list)
    target_pool.close()

    if not stream:
        end_time = datetime.now()
        cost_time = time.time() - execution_start_time
        print('\nTask end Time: ' + datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S') + '\nTime Cost: ' + str(cost_time))
        log = open('log', 'a')
        log.write('\nTask end Time: ' + datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S') + '\nTime Cost: ' + str(cost_time))
        log.close()
        os.chdir('../')


if __name__ == '__main__':
    # Set crawler target and parameters.
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target', help='Set the target fans page(at least one) you want to crawling. Ex: \'ibm\' or \'apple, ibm\'')
    parser.add_argument('-s', '--since', help='Set the start date you want to crawling. Format: \'yyyy-mm-dd HH:MM:SS\'')
    parser.add_argument('-u', '--until', help='Set the end date you want to crawling. Format: \'yyyy-mm-dd HH:MM:SS\'')
    parser.add_argument('-l', '--limit', help='This is the maximum number of objects that may be returned')

    parser.add_argument('-d', '--delay', help='delay seconds between each http request call, default = 1 second')
    parser.add_argument('-a', '--accesstoken', help='facebook access token. It will expire every two hours.')
    
    parser.add_argument('-r', '--reactions', help='Collect reactions or not. Default is no.')
    parser.add_argument('-m', '--stream', help='If yes, this crawler will turn to streaming mode.')    
    parser.add_argument('-o', '--output', help='Output format, json or html. Default is json for details comments and reactions.' 
        'html output is a summary version of the post without details for JSONLines program to package into CDR (Crawler Data Repository).'
        ' Please be aware of no file extension (.html) will be included in this option. File Name is the URL address of the post.')
         
    
    parser.print_help()

    args = parser.parse_args()

    target = str(args.target)
    since = str(args.since)
    until = str(args.until)
    access_token = str(args.accesstoken)
    
    if args.limit is not None:
        limit = int(args.limit)
    else:
        limit = 100
        
    if args.reactions == 'yes':
        get_reactions = True
    else:
        get_reactions = False

    if args.stream == 'yes':
        stream = True
    else:
        stream = False
        
    if args.delay is not None:
        delay = int(args.delay)
    else:
        delay = 1

    if args.output is not None:
        output = str(args.output)
    else:
        output = 'json'
        
    token = 'access_token=' +access_token

    #Create a directory to restore the result if not in stream mode.
    if not stream:
        result_dir = 'Result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        os.chdir(result_dir)

    if target.find(',') == -1:

        getTarget(target, since, until, token, limit, get_reactions, stream, delay, output)
        
    else:

        target = target.split(',')
        for t in target :
            getTarget(t, since, until, token, limit, get_reactions, stream, delay, output)
