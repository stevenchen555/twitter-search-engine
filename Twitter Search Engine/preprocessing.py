import pandas as pd
import re
from nltk.corpus import stopwords
from textblob import Word

tweets_df = pd.read_csv(r"C:\Users\User\PycharmProjects\Twitter_Search\all_tweets.csv")

patterns = '(?<![\w\d])\$SPX(?![\w\d])' \
           '|(?<![\w\d])\#SPX(?![\w\d])' \
           '|(?<![\w\d])S&P 500(?![\w\d])' \
           '|(?<![\w\d])SP500(?![\w\d])' \
           '|(?<![\w\d])SANDP 500(?![\w\d])' \
           '|(?<![\w\d])S&amp;P 500(?![\w\d])' \
           '|(?<![\w\d])Company(?![\w\d])'  \
           '|(?<![\w\d])company(?![\w\d])' \
           '|(?<![\w\d])stock(?![\w\d])' \
           '|(?<![\w\d])stocks(?![\w\d])' \
           '|(?<![\w\d])Stock(?![\w\d])' \
           '|(?<![\w\d])Economic(?![\w\d])' \
           '|(?<![\w\d])economic(?![\w\d])' \
           '|(?<![\w\d])companies(?![\w\d])' \
           '|(?<![\w\d])Companies(?![\w\d])' \
           '|(?<![\w\d])market(?![\w\d])' \
           '|(?<![\w\d])markets(?![\w\d])'

filter = tweets_df['text'].str.contains(patterns,regex = True)
tweets_df = tweets_df[filter]

tweets_df['cleaned_text'] = tweets_df['text'].apply(lambda x: " ".join(x.lower() for x in x.split()))
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('@\S+', '*ACCOUNT*')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('(\*ACCOUNT\*(\s)*)+', '*ACCOUNT* ')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('\*ACCOUNT\*', '')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('https\S+', '*LINK*')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('(\*LINK\*(\s)*)+', '*LINK* ')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('\*LINK\*', '')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('(http\S+)', '')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', '')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('[\W]', ' ')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('(\@.*?(?=\s))', ' ')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('([\s]{2,})', ' ')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('[^\w\s]','')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('\d+', '')

stop = stopwords.words('english')
tweets_df['cleaned_text'] = tweets_df['cleaned_text'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))

tweets_df['cleaned_text'] = tweets_df['cleaned_text'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
#print(tweets_df.sample(5))
#print(tweets_df['text'].sample(20))

tweets_df.to_csv(r"C:\Users\User\PycharmProjects\Twitter_Search\all_tweets_related.csv")