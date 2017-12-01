# Resolve the the Dow 30 companies and their corresponding products
# Classify them into separate json line files

# input: a json line document
# output: a new json line file containing only the pages relevant to dow 30
#         new tags containing company and product names will be added to html
#         body to make it convenient for inferlink

import json
import os
import nltk
import rltk
import sys
from bs4 import BeautifulSoup
from nltk.classify import NaiveBayesClassifier

reload(sys)
sys.setdefaultencoding('utf-8')

fsm = rltk.init()  # fuzzy string match


# ######## Train sentiment analysis model #########
def format_sentence(sent):
    return {word: True for word in nltk.word_tokenize(sent)}


pos = []
with open("./pos_tweets.txt") as f:
    for i in f:
        pos.append([format_sentence(i), 'positive'])

neg = []
with open("./neg_tweets.txt") as f:
    for i in f:
        neg.append([format_sentence(i), 'negative'])

# next, split labeled data into the training and test data
training = pos[:int(.8 * len(pos))] + neg[:int(.8 * len(neg))]
test = pos[int(.8 * len(pos)):] + neg[int(.8 * len(neg)):]

detOpinion = NaiveBayesClassifier.train(training)

# ######## End of training sentiment analysis model #########


dow30 = []  # a list of the Dow components
# populate the Dow dictionary with companies and their products
dowDic = {}  # the Dow dictionary
with open("./product_brand_glossory.txt", "r") as productFile:
    for chunk in productFile.read().split("\n\n"):
        products = chunk.split("\n")
        company = products[0]
        dow30.append(company)
        dowDic[company] = products[1:]


# match the companies and products in the Dow dictionary
def match_company_and_product(text):
    result = {"company": [], "product": []}
    words = text.split()  # words tokenized by spaces
    for wi in range(len(words)):
        for com in dow30:
            # match company names
            if com in ["3M", "Apple", "Visa"] and com == words[wi]:
                result["company"].append(com)
            else:
                comName = com.split()
                if len(comName) + wi <= len(
                        words) and fsm.levenshtein_similarity(com, " ".join(
                        words[wi: len(comName) + wi])) > 0.8:
                    result["company"].append(com)

            # match product names
            for product in dowDic[com]:
                proName = product.split()
                if len(proName) + wi <= len(
                        words) and fsm.levenshtein_similarity(product, " ".join(
                        words[wi: len(proName) + wi])) > 0.8:
                    result["product"].append(product)
                    if com not in result["company"]:
                        result["company"].append(com)
    return result


def filter_and_classify(path):
    jlLst = []  # json line list
    with open(path, "r") as jl_file:
        for line in jl_file:
            jsonObj = json.loads(line.rstrip())
            soup = BeautifulSoup(jsonObj["raw_content"], 'html.parser')
            title = soup.title.text if soup.title else ""
            body = soup.body.text if soup.body else ""
            entity = match_company_and_product(title + " " + body)
            insertText = ""
            if entity["company"]:
                insertText += " <span id='company'>%s</span> " % ",".join(
                    entity["company"])
            if entity["product"]:
                insertText += " <span id='product'>%s</span> " % ",".join(
                    entity["product"])
            if insertText:
                opinion = detOpinion.classify(format_sentence(title + body))
                insertText += " <span id='opinion'>%s</span> " % opinion

                text = jsonObj["raw_content"]
                index = text.find("</body>")
                jsonObj["raw_content"] = text[:index] + insertText + text[
                                                                     index:]
                jlLst.append(json.dumps(jsonObj))
    return jlLst


# output a new file to current folder
for path in sys.argv[1:]:
    jlLst = filter_and_classify(path)
    if jlLst:
        with open("new_" + os.path.basename(path), "w") as outFile:
            for jl in jlLst:
                outFile.write(jl + "\n")
