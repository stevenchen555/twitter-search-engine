from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from time import sleep
import json
import datetime
import multiprocessing
import pandas as pd

NUMBER_OF_WORKERS = 5

CEO_df = pd.read_csv(r"C:\Users\User\PycharmProjects\Twitter_Search\Twitter_Top_50.csv")
users = CEO_df['CEO_ID']

#start = datetime.datetime(2017, 1, 1)  # year, month, day
#end = datetime.datetime(2018, 1, 1)  # year, month, day

start = '2015-01-01'
end = '2017-01-01'

def format_day(date):
    day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day)
    month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month)
    year = str(date.year)
    return '-'.join([year, month, day])

def form_url(user ,since, until):
    p1 = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A'
    p2 =  user + '%20since%3A' + since + '%20until%3A' + until + 'include%3Aretweets&src=typd'
    return p1 + p2

def increment_day(date, i):
    return date + datetime.timedelta(days=i)

def run(queue,ts1,ts2):
    while True:
        user = queue.get()
        if(user is None):
            queue.task_done()
            return
        start = datetime.datetime.strptime(ts1, '%Y-%m-%d')
        end = datetime.datetime.strptime(ts2, '%Y-%m-%d')
        #start = datetime.datetime(2015, 1, 1)  # year, month, day
        #end = datetime.datetime(2017, 1, 1)  # year, month, day
        days = (end - start).days + 1
        id_selector = '.time a.tweet-timestamp'
        tweet_selector = 'li.js-stream-item'
        delay = 1  # time to wait on each page load before reading the page
        driver = webdriver.Chrome()  # options are Chrome() Firefox() Safari()
        # don't mess with this stuff
        user = user.lower()
        twitter_ids_filename = 'ids/' + user + '_all_ids.json'
        ids = []
        for day in range(days):
            d1 = format_day(increment_day(start, 0))
            d2 = format_day(increment_day(start, 1))
            url = form_url(user,d1, d2)
            print(url)
            print(d1)
            driver.get(url)
            sleep(delay)

            try:
                found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                increment = 10

                while len(found_tweets) >= increment:
                    print('scrolling down to load more tweets for ' + user)
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(delay)
                    found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                    increment += 10

                print('{} tweets found, {} total'.format(len(found_tweets), len(ids)))

                for tweet in found_tweets:
                    try:
                        id = tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                        ids.append(id)
                    except StaleElementReferenceException as e:
                        print('lost element reference', tweet)

            except NoSuchElementException:
                print('no tweets on this day')

            start = increment_day(start, 1)

        try:
            with open(twitter_ids_filename) as f:
                all_ids = ids + json.load(f)
                data_to_write = list(set(all_ids))
                print(user + ' tweets found on this scrape: ', len(ids))
                print(user + ' total tweet count: ', len(data_to_write))
        except FileNotFoundError:
            with open(twitter_ids_filename, 'w') as f:
                all_ids = ids
                data_to_write = list(set(all_ids))
                print(user + ' tweets found on this scrape: ', len(ids))
                print(user + ' total tweet count: ', len(data_to_write))

        with open(twitter_ids_filename, 'w') as outfile:
            json.dump(data_to_write, outfile)

        print(user + ' all done here')
        driver.close()  # edit these three variables
        queue.task_done()

if __name__ == '__main__':
    jobs = multiprocessing.JoinableQueue()
    if len(users)  < NUMBER_OF_WORKERS:
        NUMBER_OF_WORKERS = len(users)
    for w in range(NUMBER_OF_WORKERS):
        p = multiprocessing.Process(target=run, args=(jobs,start,end))
        p.daemon = True
        p.start()
    for user in users:
        jobs.put(user)
    jobs.join()
    print('all jobs done here')

    # Let the worker die
    for w in range(NUMBER_OF_WORKERS):
        jobs.put(None)
