from splinter import Browser
from bs4 import BeautifulSoup 
from splinter.exceptions import ElementDoesNotExist
import pandas as pd
import requests
import time
import pymongo

def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)


client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 




def scrape_info():
    collection.drop()
    browser = init_browser()

    # NASA Mars News
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    articles = soup.find('li', class_='slide')
    titles = soup.find('div', class_="content_title").find('a')
    paragraphs = articles.find('div', class_ = "article_teaser_body")
    news_title = titles.text.strip()
    news_p = paragraphs.text.strip()

    time.sleep(1)

    # JPL Mars images- Featured Image
    JPL_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(JPL_url)
    JPL_html = browser.html
    JPL_soup = BeautifulSoup(JPL_html, 'html.parser')
    JPL_image_url = JPL_soup.find('div', class_="carousel_container").article.footer.a['data-fancybox-href']
    full_image_url = 'https://www.jpl.nasa.gov'+ JPL_image_url

    #Mars Weather
    mars_weather_URL = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(mars_weather_URL)
    weather_html = browser.html
    weather_soup = BeautifulSoup(weather_html, 'html.parser')
    mars_weather_tweet = weather_soup.find('p', class_= "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
    mars_weather = mars_weather_tweet.text.strip()

    #Mars Facts
    mars_facts_URL = 'https://space-facts.com/mars/'
    tables = pd.read_html(mars_facts_URL)
    mars_facts = tables[0]
    mars_facts.columns = ['Metric', 'Fact.']
    mars_facts.set_index('Metric', inplace=True)
    mars_html_table = mars_facts.to_html()
    mars_html_table.replace('\n', '')

    #Mars Hemispheres
    hemispheres_URL = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_URL)
    hemispheres_html = browser.html
    hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')

    mars_hemispheres = []

    for i in range (4):
        images = browser.find_by_tag('h3')
        images[i].click()
        hemispheres_html = browser.html
        hemispheres_soup = hemispheres_soup(hemispheres_html, 'html.parser')
        partial_url = hemispheres_soup.find("img", class_="wide-image")["src"]
        img_title = hemispheres_soup.find("h2",class_="title").text
        img_url = 'https://astrogeology.usgs.gov'+ partial_url
        dictionary={"title":img_title,"img_url":img_url}
        mars_hemispheres.append(dictionary)
        
   
    # Close the browser after scraping
    browser.quit()

    mars_data ={
        'news_title' : news_title,
        'news_paragraph': news_p,
        'full_image_url': full_image_url,
        'mars_weather': mars_weather,
        'mars_html_table': mars_html_table,
        'mars_hemispheres': mars_hemispheres
    }
    collection.insert(mars_data)
