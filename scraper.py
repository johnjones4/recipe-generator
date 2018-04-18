import microdata
import urllib2
from BeautifulSoup import BeautifulSoup
import re
from urlparse import urlparse
import psycopg2
import sys
import json
import os

def scrape(url):
  parsed_uri = urlparse(url)
  response = urllib2.urlopen(url)
  html = response.read()
  items = microdata.get_items(html)
  recipe = None
  if len(items) > 0:
    item = items[0]
    if hasattr(item, "ingredients") and item.ingredients != None and hasattr(item, "recipeInstructions") and item.recipeInstructions != None:
      recipe = {
        "ingredients": item.get_all("ingredients"),
        "instructions": [],
      }
      for instruction in item.recipeInstructions.split("\n"):
        clean = instruction.strip()
        if clean != "":
          recipe["instructions"].append(clean)
  soup = BeautifulSoup(html)
  hrefs = []
  for link in soup.findAll('a', attrs={'href': re.compile("//%s/" % parsed_uri.netloc)}):
    hrefs.append(link.get('href'))
  return hrefs, recipe

def get_next_url():
  cur = conn.cursor()
  cur.execute("SELECT url FROM page WHERE crawled=FALSE LIMIT 1")
  rows = cur.fetchall()
  if len(rows) > 0:
    return rows[0][0]
  else:
    return None

def setup_db():
  conn = psycopg2.connect(os.environ.get('DB_CONNECTION_STRING'))
  cur = conn.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS public.page(id serial NOT NULL, url varchar(256) NOT NULL, crawled bool NOT NULL DEFAULT FALSE, recipe text, CONSTRAINT page_pk PRIMARY KEY (id,url), CONSTRAINT url UNIQUE (url));")
  conn.commit()
  return conn

def mark_url_crawled(url, recipe):
  recipeJson = None
  if recipe != None:
    recipeJson = json.dumps(recipe)
  cur = conn.cursor()
  cur.execute("UPDATE page SET crawled=TRUE, recipe=%s WHERE url=%s", (recipeJson, url,))
  conn.commit()

def commit_new_hrefs(hrefs):
  if len(hrefs) > 0:
    for url in hrefs:
      cur = conn.cursor()
      cur.execute("SELECT id FROM page where url = %s", (url,))
      rows = cur.fetchall()
      if len(rows) == 0:
        print("adding %s" % url)
        cur.execute("INSERT INTO page (url) values (%s)", (url,))
        conn.commit()

def start():
  while True:
    url = get_next_url()
    print("Crawling %s" % url)
    hrefs, recipe = scrape(url)
    mark_url_crawled(url, recipe)
    commit_new_hrefs(hrefs)
    
conn = setup_db()
start()
