# Market-Trend-Prediction
This is a project of building knowledge graph course. The project leverages historical stock price, and integrates social media listening from customers to predict market Trend On Dow Jones Industrial Average (DJIA).

Data period: Aug 1, 2016 to Oct 31, 2017.
Data range for DJIA: Aug 1, 2016 to Nov 30, 2017.
Data Source: Business Insider (record no.: 2,017), Reddit finance(4,383), facebook (11,528), yahoo finance(10,478), Twitter(24,271)
Structure Data: Facebook, Twritter.

### Predict Results: 
1. Please refer [this link to the Jupyter code for prediction results with social media information as part of input features](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/Dow%20Jones%20Industrial%20Average%20Prediction%20with%20Media%20Channel%20Info-with%20Social%20Info.ipynb).

2. Please refer [this link to the Jupyter code for prediction results without social media information as input features](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/Dow%20Jones%20Industrial%20Average%20Prediction%20without%20Social%20media%20data.ipynb).

```text
T+1 Prediction
              precision    recall  f1-score   support

Decrease       0.00      0.00      0.00         7
Increase       0.70      1.00      0.82        16

avg / total    0.48      0.70      0.57        23

T+30 Prediction
              precision    recall  f1-score   support

Increase       1.00      1.00      1.00        23

avg / total    1.00      1.00      1.00        23 
```

### Program lists:
|Programs|Description|Link|
|------|------|--------|
|[JSONLines](https://github.com/Cheng-Lin-Li/KnowledgeGraph/tree/master/CDR_JSONLines)|Once your crawler download a lot of pages, how can you aggregate all of those files into single one? Json Lines is your answer. The program will package each of your file into single JSON object into the file which will contain multiple JSON objects.| [Source Code](https://github.com/Cheng-Lin-Li/KnowledgeGraph/blob/master/CDR_JSONLines/jsonlines.py)|
|[JSONLines content classifier program](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/classify.py)|The input is a json line document and a new json line file containing only the pages relevant to dow 30 companies based on glossary of Dow30 companies and their products. New tags containing company and product names will be added to html body to make it convenient for inferlink. NLTK tools was used for positive, negative message or post recognition. rltk tools was adopted to perform string similarity for web content and glossary of company names and productions.|[Source Code](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/classify.py)|
|[Data Integration program](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/dataintegration.py)| This program based on csv file of Dow30 companies and add with facebook, twitter social media likes, dislikes into csv for machine learning input. |[Source Code](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/dataintegration.py)|
|[Facebook Crawler for Dow30](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/facebook-crawler-dow30.py)| This is a crawler program to crawl facebook post via facebook graph api. A special facebook id and Dow 30 companies dictionary are integrated into this version. A CSV with like, dislike will provide by this program for machine learning. |[Source Code](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/facebook-crawler-dow30.py)|
|[Yahoo Crawler for Dow30](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/yahoo_quote_crawler.py)| This is a crawler program to crawl yahoo finance stock price via yahoo api. A special ticker id and Dow 30 companies dictionary are integrated into this version. A CSV with full company name will provide by this program for machine learning purpose. Input a list of stock ticker and time period for those price data. |[Source Code](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/yahoo_quote_crawler.py)|
|[Twitter Crawler for Dow30 Companies](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/tweetScraper.py)| This program scrapes the offcial Titter accounts of Dow components |[Source Code](https://github.com/Cheng-Lin-Li/Market-Trend-Prediction/blob/master/source/tweetScraper.py)|

### Team members: 
Cheng-Lin Li & YuCheng Guo 

### Date: Project kick off date
Oct., 2017@University of Southern California

## Disclaimer
Last updated: January 16, 2018

The information contained on https://github.com/Cheng-Lin-Li/ website (the "Service") is for general information purposes only.
Cheng-Lin-Li's github assumes no responsibility for errors or omissions in the contents on the Service.

In no event shall Cheng-Lin-Li's github be liable for any special, direct, indirect, consequential, or incidental damages or any damages whatsoever, whether in an action of contract, negligence or other tort, arising out of or in connection with the use of the Service or the contents of the Service. Cheng-Lin-Li's github reserves the right to make additions, deletions, or modification to the contents on the Service at any time without prior notice.

### External links disclaimer

https://github.com/Cheng-Lin-Li/ website may contain links to external websites that are not provided or maintained by or in any way affiliated with Cheng-Lin-Li's github.

Please note that the Cheng-Lin-Li's github does not guarantee the accuracy, relevance, timeliness, or completeness of any information on these external websites.

## Contact Information
Cheng-Lin Li@University of Southern California

chenglil@usc.edu or 

clark.cl.li@gmail.com


