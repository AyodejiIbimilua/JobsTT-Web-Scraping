#import libraries
import time
import re
import math
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

def get_soup(url):
    """
    parses pages and returns soup
    """
    r = requests.get(url,
                     headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
    soup = BeautifulSoup(r.text, 'html.parser')
    
    return soup

#loads page
soup = get_soup("https://jobstt.com/search-results-jobs/?searchId=1659019988.2823&action=search&page=1&listings_per_page=100&view=list")

#get the number of search results
nub_pages = soup.select("div.topjobs h3")[0].text.split(": ")[1].strip()
nub_pages = int(nub_pages)

#calculates the number of pages
if 100 > nub_pages:
    pg_range = [1]
else:
    pg_range = math.ceil(nub_pages / 100)
    pg_range = np.arange(1, pg_range + 1)

#gets individual job links

job_urls = []
for pg in pg_range:
    
    url = "https://jobstt.com/search-results-jobs/?searchId=1659019988.2823&action=search&page=" + str(pg) + "&listings_per_page=100&view=list"
    soup = get_soup(url)
    
    menu = soup.select("section#home > div.listone")
    urls = [mn.select("h1 > a")[0]["href"] for mn in menu]    
    for i in urls:
        job_urls.append(i)

data_list = []

#extracts data for each job
for job_url in job_urls:
    soup = get_soup(job_url)
    
    try:
        job_title = soup.select("div#listingsResults > h1")[0].text.strip()
    except:
        job_title = ""
    try:
        city = soup.select("div#listingsResults > div.citycost > span.city")[0].text.strip()
    except:
        city = ""

    try:
        isfulltime = soup.select("div#listingsResults > div.citycost > span.fulltimejob")[0].text.strip()
    except:
        isfulltime = ""

    posted_on = ""
    expired_on = ""

    dates = soup.select("div#listingsResults > div.citycost > span.date")

    for dt in dates:
        if "Posted On " in dt.text:
            po = dt.text.split("Posted On ")[1]
            posted_on += po
        elif "Expire On " in dt.text:
            eo = dt.text.split("Expire On ")[1]
            expired_on += eo
    try:        
        employer = soup.select("div#listingsResults > div.citycost > span.hr")[0].text    
    except:
        employer = ""

    try:
        description = soup.select("div#listingsResults div.cvtips.job_description")[0].text.replace("\n", "").replace("\xa0", "")
        description = description.split("Description", 1)[1].strip()
    except:
        description = ""

    try:    
        company_name = soup.select("div.codetails > h1")[0].text.strip()
    except:
        company_name = ""

    try:
        company_profile = soup.select("div.codetails > a")[1]["href"]
    except:
        company_profile = ""    
        
    dt = {
        "Job Title": job_title,
        "Job Url": job_url,
        "City": city,
        "Job Type": isfulltime,
        "Posted On": posted_on,
        "Expired On": expired_on,
        "Employer": employer,
        "Description": description,
        "Company Name": company_name,
        "Company Profile Link": company_profile
    }
    
    data_list.append(dt)

#converts extracted data to dataframe
df = pd.DataFrame(data_list)

df.to_excel("jobstt.xlsx", index=False)

