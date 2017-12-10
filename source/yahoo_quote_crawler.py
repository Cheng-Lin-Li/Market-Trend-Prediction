# -*- coding: utf-8 -*-

"""

Created on Thu Nov 30 2017
@author: Cheng-Lin Li

Reference:
github: https://github.com/c0redumb/yahoo_quote_download
Created on Thu May 18 22:58:12 2017
@author: c0redumb

"""
# To make print working for Python2/3
from __future__ import print_function
# Use six to import urllib so it is working for Python2/3
#from six.moves import urllib

# If you don't want to use six, please comment out the line above
# and use the line below instead (for Python3 only).
import urllib.request, urllib.parse
import os, time
import argparse

from datetime import datetime


'''
Starting on May 2017, Yahoo financial has terminated its service on
the well used EOD data download without warning. This is confirmed
by Yahoo employee in forum posts.

Yahoo financial EOD data, however, still works on Yahoo financial pages.
These download links uses a "crumb" for authentication with a cookie "B".
This code is provided to obtain such matching cookie and crumb.
'''

URL_HEADER = 'https://finance.yahoo.com/quote/'
URL_API = 'https://query1.finance.yahoo.com/v7/finance/download/'

# Build the cookie handler
cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)



# Cookie and corresponding crumb
_cookie = None
_crumb = None



# Headers to fake a user agent
_headers={
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}


def _get_cookie_crumb():

    '''
    This function perform a query and extract the matching cookie and crumb.
    '''

    # Perform a Yahoo financial lookup on SP500
    req = urllib.request.Request('https://finance.yahoo.com/quote/^GSPC', headers=_headers)
    f = urllib.request.urlopen(req)
    alines = f.read().decode('utf-8')


    # Extract the crumb from the response
    global _crumb
    cs = alines.find('CrumbStore')
    cr = alines.find('crumb', cs + 10)
    cl = alines.find(':', cr + 5)
    q1 = alines.find('"', cl + 1)
    q2 = alines.find('"', q1 + 1)
    crumb = alines[q1 + 1:q2]
    _crumb = crumb



    # Extract the cookie from cookiejar
    global cookier, _cookie
    for c in cookier.cookiejar:
        if c.domain != '.yahoo.com':
            continue
        
        if c.name != 'B':
            continue
        _cookie = c.value

    # Print the cookie and crumb
    #print('Cookie:', _cookie)
    #print('Crumb:', _crumb)



def load_yahoo_quote(ticker, begindate, enddate, info = 'quote'):
    '''
    This function load the corresponding history/divident/split from Yahoo.
    '''

    # Check to make sure that the cookie and crumb has been loaded
    global _cookie, _crumb
    
    if _cookie == None or _crumb == None:
        _get_cookie_crumb()

    # Prepare the parameters and the URL
    tb = time.mktime((int(begindate[0:4]), int(begindate[4:6]), int(begindate[6:8]), 4, 0, 0, 0, 0, 0))
    te = time.mktime((int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), 18, 0, 0, 0, 0, 0))


    param = dict()
    param['period1'] = int(tb)
    param['period2'] = int(te)
    param['interval'] = '1d'

    if info == 'quote':
        param['events'] = 'history'
    elif info == 'dividend':
        param['events'] = 'div'
    elif info == 'split':
        param['events'] = 'split'

    param['crumb'] = _crumb
    params = urllib.parse.urlencode(param)

    url = URL_API+'{}?{}'.format(ticker, params)

    print(url)

    req = urllib.request.Request(url, headers=_headers)


    # Perform the query
    # There is no need to enter the cookie here, as it is automatically handled by opener

    f = urllib.request.urlopen(req)
    alines = f.read().decode('utf-8')

    print(alines)

    return alines.split('\n')

def convertToDow(target):
    
    companydict = { '^DJI': 'DJIA',
                    'MMM':'3M', 
                    'AXP':'American Express',
                    'AAPL': 'Apple',
                    'BA':'Boeing', 
                    'CAT':'Caterpillar', 
                    'CVX':'Chevron',
                    'CSCO':'Cisco Systems',
                    'KO':'Coca-Cola', 
                    'DWDP':'DowDuPont', 
                    'XOM':'ExxonMobil', 
                    'GE':'General Electric', 
                    'GS':'Goldman Sachs', 
                    'IBM':'IBM', 
                    'INTC':'Intel', 
                    'JNJ':'Johnson & Johnson', 
                    'JPM':'JPMorgan Chase',
                    'MCD':"McDonald's", 
                    'MRK':'Merck', 
                    'MSFT':'Microsoft',
                    'NKE':'Nike', 
                    'PFE':'Nike',
                    'PG':'Pfizer', 
                    'proctergamble':'Procter & Gamble', 
                    'HD':'The Home Depot', 
                    'TRV':'Travelers', 
                    'UTX':'United Technologies',
                    'UNH':'UnitedHealth Group', 
                    'VZ':'Verizon', 
                    'V':'Visa', 
                    'WMT':'Walmart', 
                    'DIS':'Walt Disney'}
    _target = target.strip()
    companyname = companydict.get(_target)
#     print ('target ="%s", companyname="%s"'%(_target, str(companyname)))
    if companyname == None:
        companyname = _target
    else:
        pass
    
    return companyname

def getHTML(target, dictObj):
        
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
    output += getHTMLItems(dictObj)
    output += ('</body>'
      '</html>'
      )     
    return output

def getHTMLItems(dictObj):
    output = ''
    output += '  <ul>\n'
    for k,v in dictObj.items():
        output += '    <li class="' + k + '"> ' + k + ': ' + ('0' if v is None else str(v)) + '</li>'
    output += '  ' + '</ul>\n'
    
    return output

def getCSV(target, dictObj, sequence, num):
    # target = company ticker
    # sequence = sequence of query
    # num = the number of row.
    header = ''
    output = ''
    _target = convertToDow(target)
    
    for k, v in dictObj.items():
         # first ticker's first row print header
        if sequence == 0 and num ==1:
            header += k+','
        else:
            pass
        output += v+','
     # first ticker's first row print header
    if sequence == 0 and num == 1:
        header += _target+'\n'
    output = header + output + _target+'\n'

    return output


def printQuote(target, quote, sequence):
    URL_HEADER = 'https://finance.yahoo.com/quote/'
    'IBM/history?period1=1480492800&period2=1480492800&interval=1d&filter=history&frequency=1d'
    feed_id = URL_HEADER + target + '/history?period1='
    url = ''
    header = []
    dictObj = {}
    
    for i, row in enumerate(quote):
        words = row.split(',')
        if i == 0:
            header = words
        else:
            if len(words) > 1:
                url = feed_id
                for j , data in enumerate(words):
                    dictObj[header[j]] = data
    
                begindate = dictObj['Date']
                tb = str(int(time.mktime((int(begindate[0:4]), int(begindate[5:7]), int(begindate[8:10]), 4, 0, 0, 0, 0, 0))))
                                 
                url += tb+'&period2='+tb+'&interval=1d&filter=history&frequency=1d'
#                 print ('url=%s'%(url))                
                feed_file = open('./'+urllib.parse.quote_plus(url), 'w', encoding='utf8')
                feed_file.write(getHTML(target, dictObj))
                feed_file.close()
                csv_file = open('./DJIA.csv', 'a', encoding='utf8')
                csv_file.write(getCSV(target, dictObj, sequence, i))
                csv_file.close()
            else:
                pass

    
def getTarget(target, since, until, limit, stream, delay, sequence):

#     if not stream:
#         target_dir = target + '/'
#         if not os.path.exists(target_dir):
#             os.makedirs(target_dir)
#         os.chdir(target_dir)

    log = open('log', 'w')
    start_time = datetime.now()
    print('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + target + '\nSince: ' + since + '\nUntil: ' + until + '\n')
    log.write('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + target + '\nSince: ' + since + '\nUntil: ' + until + '\n')
    log.close()

    #Get list of feed id from target.

    quote = load_yahoo_quote(target, since, until, 'quote')
    print('quote = %s'%(quote))
    printQuote(target, quote, sequence)
 

if __name__ == '__main__':
    # Set crawler target and parameters.
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target', help='Set ticker you want to get. Ex: \'^DJI\' or \'^DJI, AXP\'')
    parser.add_argument('-s', '--since', help='Set the start date you want to crawling. Format: \'yyyymmdd\'')
    parser.add_argument('-u', '--until', help='Set the end date you want to crawling. Format: \'yyyymmdd\'')
    parser.add_argument('-l', '--limit', help='This is the maximum number of objects that may be returned')

    parser.add_argument('-d', '--delay', help='delay seconds between each http request call, default = 1 second')
        
    parser.add_argument('-m', '--stream', help='If yes, this crawler will turn to streaming mode.')    

         
    # ^DJI, MMM, AXP, AAPL, BA, CAT, CVX, CSCO, KO, DWDP, XOM, GE, GS, HD, IBM, INTC, JNJ, JPM, MCD, MRK, MSFT, NKE, PFE, PG, TRV, UNH, UTX, VZ, V, WMT, DIS
    parser.print_help()

    args = parser.parse_args()

    target = str(args.target)
    since = str(args.since)
    until = str(args.until)
    
    if args.limit is not None:
        limit = int(args.limit)
    else:
        limit = 100

    if args.stream == 'yes':
        stream = True
    else:
        stream = False
        
    if args.delay is not None:
        delay = int(args.delay)
    else:
        delay = 1

    #Create a directory to restore the result if not in stream mode.
    if not stream:
        result_dir = 'Result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        os.chdir(result_dir)

    if target.find(',') == -1:
        getTarget(target, since, until, limit, stream, delay, 0)
        
    else:

        target = target.split(',')
        for i, t in enumerate(target) :
            getTarget(t.strip(), since, until, limit, stream, delay, i)

    end_time = datetime.now()
    print('Task end at:' + datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + str(target) + '\nSince: ' + since + '\nUntil: ' + until + '\n')

