#The program also has the following dependencies:
#!pip install BeautifulSoup
#!pip install html
#
#You must run these commands before executing the program, asssuming
#the other imports are already available on your python environment
#
#This program will go through 9 pages on yelp and scrape emails, but it will 
#take a while because of spaced dealys. These delays are in place because yelp
#will temporarily block web addresses that make too many queries in a given time frame.

from lxml import html  
from exceptions import ValueError
from time import sleep
from bs4 import BeautifulSoup

import json
import requests
import re,urllib
import argparse
import time
import random

import urllib3
urllib3.disable_warnings()

def parse(url):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	response = requests.get(url, headers=headers, verify=False).text
	parser = html.fromstring(response)
	print ("Parsing the page...")
    
  #use html class from python to pull specific information
	raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")	
	raw_claimed = parser.xpath("//span[contains(@class,'claim-status_icon--claimed')]/parent::div/text()")	
	raw_reviews = parser.xpath("//div[contains(@class,'biz-main-info')]//span[contains(@class,'review-count rating-qualifier')]//text()")	
	raw_category  = parser.xpath('//div[contains(@class,"biz-page-header")]//span[@class="category-str-list"]//a/text()')
	hours_table = parser.xpath("//table[contains(@class,'hours-table')]//tr")
	details_table = parser.xpath("//div[@class='short-def-list']//dl")
	raw_map_link = parser.xpath("//a[@class='biz-map-directions']/img/@src")
	raw_phone = parser.xpath(".//span[@class='biz-phone']//text()")
	raw_address = parser.xpath('//div[@class="mapbox-text"]//div[contains(@class,"map-box-address")]//text()')
	raw_wbsite_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
	raw_price_range = parser.xpath("//dd[contains(@class,'price-description')]//text()")
	raw_health_rating = parser.xpath("//dd[contains(@class,'health-score-description')]//text()")
	rating_histogram = parser.xpath("//table[contains(@class,'histogram')]//tr[contains(@class,'histogram_row')]")
	raw_ratings = parser.xpath("//div[contains(@class,'biz-page-header')]//div[contains(@class,'rating')]/@title")
  
	time.sleep(random.randint(0, 1) * .531467298)

  #find array of working hours
	working_hours = []
	for hours in hours_table:
		raw_day = hours.xpath(".//th//text()")
		raw_timing = hours.xpath("./td//text()")
		day = ''.join(raw_day).strip()
		timing = ''.join(raw_timing).strip()
		working_hours.append({day:timing})
    
  #any yelp-related information on website
	info = []
	for details in details_table:
		raw_description_key = details.xpath('.//dt//text()')
		raw_description_value = details.xpath('.//dd//text()')
		description_key = ''.join(raw_description_key).strip()
		description_value = ''.join(raw_description_value).strip()
		info.append({description_key:description_value})

  #How many 5 star, 4 star, 3 star, 2 star, and 1 star ratings there are
	ratings_histogram = [] 
	for ratings in rating_histogram:
		raw_rating_key = ratings.xpath(".//th//text()")
		raw_rating_value = ratings.xpath(".//td[@class='histogram_count']//text()")
		rating_key = ''.join(raw_rating_key).strip()
		rating_value = ''.join(raw_rating_value).strip()
		ratings_histogram.append({rating_key:rating_value})
	
  #Strip all of the strings to make processing simpler
	name = ''.join(raw_name).strip()
	phone = ''.join(raw_phone).strip()
	address = ' '.join(' '.join(raw_address).split())
	health_rating = ''.join(raw_health_rating).strip()
	price_range = ''.join(raw_price_range).strip()
	claimed_status = ''.join(raw_claimed).strip()
	reviews = ''.join(raw_reviews).strip()
	category = ','.join(raw_category)
	cleaned_ratings = ''.join(raw_ratings).strip()

  #Check that the business has a private website
	if raw_wbsite_link:
		decoded_raw_website_link = urllib.unquote(raw_wbsite_link[0])
		website = re.findall("biz_redir\?url=(.*)&website_link",decoded_raw_website_link)[0]
	else:
		website = ''
    
  #Check if the ratings 
	if raw_ratings:
		ratings = re.findall("\d+[.,]?\d+",cleaned_ratings)[0]
	else:
		ratings = 0
	
  #how data is currently organized
	data={
    'working_hours':working_hours,
		'info':info,
		'ratings_histogram':ratings_histogram,
		'name':name,
		'phone':phone,
		'ratings':ratings,
		'address':address,
		'health_rating':health_rating,
		'price_range':price_range,
		'claimed_status':claimed_status,
		'reviews':reviews,
		'category':category,
		'website':website,
		'url':url
	}
  
	return data

#request zipcode here
numPages = 9

print ("What zipcode would you like to read from on yelp?")
zipcode = raw_input()
business_type = "https://www.yelp.com/search?find_desc=&find_loc="

#Home Repair: "https://www.yelp.com/search?cflt=homeservices&find_loc="
#Restaurants: "https://www.yelp.com/search?find_desc=&find_loc="
#Auto: "https://www.yelp.com/search?cflt=auto&find_loc="
#Hair: "https://www.yelp.com/search?cflt=hair&find_loc="

link_general = business_type + zipcode + "&ns=1"
yelp_links = []

#start crawling from yelp based on zipcode
for i in range(0, numPages + 1):
  #generate the next yelp-page
  link_cur = link_general + "&start=" + str(i * 10)
  html2 = requests.get(link_cur).text
  
  #Using BeautifulSoup to scrap href links
  bs = BeautifulSoup(html2)
  possible_links = bs.find_all('a')
      
  #find all the business-related links on the page
  for link in possible_links:
    if link.has_attr('href'):
      x = link.attrs['href']
      
      if ("/biz/" in x):
        link_sub = "https://www.yelp.com" + x
        yelp_links.append(link_sub)

#remove duplicates
yelp_links.sort()
residual = []

for i in range(0, len(yelp_links)):
  if (i % 3 == 0):
    residual.append(yelp_links[i])

#begin parsing the links on the general yelp page
for l in residual:
  parsed_data = parse(l)
  print(parsed_data)
