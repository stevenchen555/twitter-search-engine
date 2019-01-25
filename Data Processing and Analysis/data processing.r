
all_tweets_related<- read.csv(file.choose(),header = T)
str(all_tweets_related)

# build corpus
library(tm)
#
corpus<-iconv(all_tweets_related$text, to = 'UTF-8',sub="byte")
#
corpus<- Corpus(VectorSource(corpus))

#text cleaning
corpus<- tm_map(corpus,tolower)  # converting the texts into lower case if any
inspect(corpus[1:5])

corpus<- tm_map(corpus, removePunctuation) #removing punctuation marks if any
inspect(corpus[1:5])

corpus<- tm_map(corpus, removeNumbers) #removing any numerical values from the tweets
inspect (corpus[1:5])

cleandata<-tm_map(corpus,removeWords,stopwords('english')) #removing the stop words
inspect(cleandata[1:5])

removeURL <- function(x) gsub('http[[:alnum:]]*','',x)
cleandata<- tm_map(cleandata, content_transformer(removeURL)) #removing the unwanted Url
inspect(cleandata[1:5])

cleandata<-tm_map(cleandata,gsub,pattern = 'companies',replacement = 'company')
cleandata<-tm_map(cleandata,stripWhitespace) #removing the unwanted whitespace
inspect(cleandata[1:5])


#term document matrix
tdm<- TermDocumentMatrix(cleandata)

tdm <- as.matrix((tdm))
tdm[1:15,1:15]



#bar plot
w<-rowSums(tdm)
w<-subset(w,w>=75)
barplot(w,
        las = 2,
        col = rainbow(45))

#wordcloud
library(wordcloud)
w<- sort(rowSums(tdm),decreasing = TRUE)
set.seed(222)
wordcloud(words = names(w),
          freq = w,
          max.words = 100,
          random.order = F,
          min.freq = 3,
          colors = brewer.pal(7,'Dark2'),
          scale = c(7,0.3))



#sentiment analysis
library(syuzhet)
library(lubridate)
library(ggplot2)
library(scales)
library(reshape2)
library(dplyr)
library(stringr)
#read file

all_tweets_related<- read.csv(file.choose(),header = T)

#all_tweets_related$created_at<-as.POSIXct(all_tweets_related$created_at,format="%Y-%m-%dT%H:%M",tz = "America/New_York")

#timestamp <- as.POSIXct(sapply(some_tweets, function(x)x$getCreated()), origin="1970-01-01", tz="GMT")
#tweets<- iconv(musk$text, to = 'UTF-8',sub = "byte")
all_tweets_related$created_at <- mdy_hm(all_tweets_related$created_at)
all_tweets_related$created_at <- with_tz(all_tweets_related$created_at, "America/New_York")
all_tweets_related$clean_text <- str_replace_all(all_tweets_related$text, "@\\w+", "")#improve
Sentiment <- get_nrc_sentiment(all_tweets_related$clean_text)
alltweets_senti <- cbind(all_tweets_related, Sentiment)
sentimentTotals <- data.frame(colSums(alltweets_senti[,c(7:16)]))

names(sentimentTotals) <- "count"
sentimentTotals <- cbind("sentiment" = rownames(sentimentTotals), sentimentTotals)
rownames(sentimentTotals) <- NULL
#Twitter volume in each sentiment category
ggplot(data = sentimentTotals, aes(x = sentiment, y = count)) +
  geom_bar(aes(fill = sentiment), stat = "identity") +
  theme(legend.position = "none") +
  xlab("Sentiment") + ylab("Total Count") + ggtitle("Total Sentiment Score for All Tweets")
#Positive and negative sentiment over time
#alltweets_senti$created_at<-as.POSIXct(alltweets_senti$created_at,format="%Y-%m-%dT%H:%M",tz = "America/New_York")

#alltweets_senti$created_at <- with_tz(ymd_hms(alltweets_senti$created_at), "America/New_York")
posnegtime <- alltweets_senti %>% 
  group_by(created_at = cut(created_at, breaks="2 days")) %>%
  summarise(negative = mean(negative),
            positive = mean(positive)) %>% melt



# Using created as id variables
names(posnegtime) <- c("created_at", "sentiment", "meanvalue")
posnegtime$sentiment = factor(posnegtime$sentiment,levels(posnegtime$sentiment)[c(2,1)])

ggplot(data = posnegtime, aes(x = as.Date(created_at), y = meanvalue, group = sentiment)) +
  geom_line(size = 1.5, alpha = 0.7, aes(color = sentiment)) +
  geom_point(size = 0.3) +
  ylim(0, NA) + 
  scale_colour_manual(values = c("springgreen4", "firebrick3")) +
  theme(legend.title=element_blank(), axis.title.x = element_blank()) +
  scale_x_date(breaks = date_breaks("3 months"), 
               labels = date_format("%Y-%b")) +
  ylab("Average sentiment score") + 
  ggtitle("Sentiment Over Time")


#sentiment over months

alltweets_senti$month <- month(alltweets_senti$created_at, label = TRUE)
monthlysentiment <- alltweets_senti %>% group_by(month) %>% 
  summarise(anger = mean(anger), 
            anticipation = mean(anticipation), 
            disgust = mean(disgust), 
            fear = mean(fear), 
            joy = mean(joy), 
            sadness = mean(sadness), 
            surprise = mean(surprise), 
            trust = mean(trust)) %>% melt



names(monthlysentiment) <- c("month", "sentiment", "meanvalue")

ggplot(data = monthlysentiment, aes(x = month, y = meanvalue, group = sentiment)) +
  geom_line(size = 2.5, alpha = 0.7, aes(color = sentiment)) +
  geom_point(size = 0.5) +
  ylim(0, NA) +
  theme(legend.title=element_blank(), axis.title.x = element_blank()) +
  ylab("Average sentiment score") + 
  ggtitle("Sentiment During the Year")



#sentiment scores
s<- get_nrc_sentiment(tweets)
head(s)
#get_nrc_sentiment('ugly')

#bar plot for sentiment analysis
barplot(colSums(s),
        las = 2,
        col = rainbow(10),
        ylab = 'count',
        main = 'sentiment score for elon musk')

