import tweepy
import json
import math
import glob
import csv
import zipfile
import time
import zlib
from tweepy import TweepError
from time import sleep
from six import u as unicode
import pandas as pd

CEO_df = pd.read_csv(r"C:\Users\User\PycharmProjects\Twitter_Search\Twitter_Top_50.csv")
# CHANGE THIS TO THE USER YOU WANT
users = CEO_df['CEO_ID']
ids = []

with open('api_keys.json') as f:
    keys = json.load(f)

auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)
user = 'all_tweets'
user = user.lower()
output_file = '{}.json'.format(user)
output_file_short = '{}_short.json'.format(user)
compression = zipfile.ZIP_DEFLATED

for user_name in users:
    temp_file_name = 'ids/' + user_name + '_all_ids.json'
    with open(temp_file_name) as f:
        ids =  ids + json.load(f)

#with open('all_ids.json') as f:
#   ids = json.load(f)

print('total ids: {}'.format(len(ids)))

all_data = []
results = []
start = 0
end = 100
limit = len(ids)
i = math.ceil(limit / 100)

for go in range(i):
    print('currently getting {} - {}'.format(start, end))
    sleep(1)  # needed to prevent hitting API rate limit
    id_batch = ids[start:end]
    start += 100
    end += 100
    tweets = api.statuses_lookup(id_batch)
    for tweet in tweets:
        entry = tweet._json
        t = {
            "user": entry["user"]["screen_name"],
            "created_at": entry["created_at"],
            "text": entry["text"],
        }
        results.append(t)

print('creating minimized json master file')
with open(output_file_short, 'w') as outfile:
    json.dump(results, outfile)

with open(output_file_short) as master_file:
    data = json.load(master_file)
    fields = ["user","created_at", "text"]
    print('creating CSV version of minimized json master file')
    f = csv.writer(open('{}.csv'.format(user), 'w',encoding='utf-8',newline=''))
    f.writerow(fields)
    for x in data:
        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(x["created_at"], '%a %b %d %H:%M:%S +0000 %Y'))
        f.writerow( [x["user"],created_at,x["text"]])