import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4
import pandas as pd

def get_date(x):
    return pd.to_datetime(x)

def get_tweets(city, state, since, until, radius=30, scrolls=50):
    browser = webdriver.Chrome(executable_path='./chromedriver')
    stem = "http://twitter.com/search?l=&q="
    url = '{}near:%22{}%2C%20{}%22%20within:{}mi%20since:{}%20until:{}&src=typd'.format(stem, city, state, radius, since, until)
    print(url)
    browser.get(url)
    body = browser.find_element_by_tag_name('body')
    mylist = []
    for i in range(scrolls):
        body.send_keys(Keys.PAGE_DOWN)
        try:
            time.sleep(.1)
        except:
            pass
        
        page_source = browser.page_source
        soup = bs4.BeautifulSoup(page_source, 'lxml')

        for row in soup.find_all('li', {'data-item-type' : 'tweet'}):
            tweet = {}
            try:
                tweet['time'] = row.find('a', {'class' : 'tweet-timestamp js-permalink js-nav js-tooltip'}).attrs['title']
            except:
                pass
            tweet['text'] = row.find('p').text
            tweet['ID'] = row.attrs['id'].strip('stream-item-tweet-')
            mylist.append(tweet)

        mydf = pd.DataFrame(mylist)

        browser.close()

        return mydf

# print(get_tweets('sydney', 'new south wales', '2019-06-01', '2020-01-16'))

def iterate_disasters(df):
    all_dfs = []
    for row in df.index:
        city = df.loc[row, 'declaredCountyArea']
        state = df.loc[row, 'state']
        disaster_begin = df.loc[row, 'incidentBeginDate']
        before_disaster = (pd.to_datetime(disaster_begin) - pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        before_disaster_end = (pd.to_datetime(disaster_begin) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        after_disaster = (pd.to_datetime(disaster_begin) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        
        # running 'get tweets' function for before disaster
        tweets_disaster_before = get_tweets(city, state, before_disaster, before_disaster_end)
        
        # setting additional vars for each row
        tweets_disaster_before['disaster_num'] = df.loc[row, 'disasterNumber'] 
        tweets_disaster_before['disaster_type'] = df.loc[row, 'title']
        tweets_disaster_before['disaster_declared'] = df.loc[row, 'declarationDate']
        tweets_disaster_before['disaster_started'] = df.loc[row, 'incidentBeginDate']
        tweets_disaster_before['location'] = df.loc[row, 'declaredCountyArea']
        tweets_disaster_before['disaster_happened'] = '0'
        
        all_dfs.append(tweets_disaster_before) # adding to list
        
        # running get tweets function for after disaster
        tweets_disaster_after = get_tweets(city, state, disaster_begin, after_disaster)
   
        # setting additional vars for each row
        tweets_disaster_after['disaster_num'] = df.loc[row, 'disasterNumber'] 
        tweets_disaster_after['disaster_type'] = df.loc[row, 'title']
        tweets_disaster_after['disaster_declared'] = df.loc[row, 'declarationDate']
        tweets_disaster_after['disaster_started'] = df.loc[row, 'incidentBeginDate']
        tweets_disaster_after['location'] = df.loc[row, 'declaredCountyArea']
        tweets_disaster_after['disaster_happened'] = '1'

        # adding each df to a csv
        all_dfs.append(tweets_disaster_after) # instantiating empty list
    
    return all_dfs

# Wrap function - this is the one to call 
def tweets_to_csv(df, csv_name):
    X = iterate_disasters(df)
    full = pd.concat(X, sort=False)
    # changing time to timeseries
    full['time'] = full['time'].str.replace(r'[-]', '').apply(get_date)
    full.drop_duplicates(subset = ['ID', 'text'], inplace = True)
    # saving to csv
    full.to_csv(csv_name) # RENAME THIS before pushing it to github to avoid confusion

### read in your csv
to_scrape = pd.read_csv('./disasters')
## what we used to filter by disaster type - OPTIONAL
to_scrape_filtered = disasters[disasters['disasterType'] == 'DR'] # DR = major disaster

# breaking up the csv to scrape into parts (recommended)
part = [[10, 110], [110, 210], [210, 310], [310, 410], [410, 510], [510, 547]]

for i in part:
    suffix = str(i[0]) + '_' + str(i[1])
    csv_name = './disasters' + suffix + '.csv'
    tweets_to_csv(to_scrape_filtered[i[0]:i[1]], csv_name)

tweets_to_csv(to_scrape_filtered)