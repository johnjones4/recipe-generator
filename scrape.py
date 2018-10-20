from dotenv import load_dotenv
load_dotenv()
from lib import db
from lib.db import Page, Recipe
from lib.scrape_utils import scrape
import datetime

db.init_db()

# hrefs, recipe = scrape("https://www.epicurious.com/occasion/valentines-day")
# print(hrefs)

while True:
  page = db.session.query(Page).filter(Page.date_scraped==None).limit(1).one_or_none()
  if page is not None:
    print("Crawling %s" % page.url)
    hrefs, recipe = scrape(page.url)
    page.date_scraped = datetime.datetime.now()
    pages = []
    for href in hrefs:
      if db.session.query(Page).filter(Page.url==href).one_or_none() is None:
        pages.append(Page(
          url=href
        ))
    print("Found %d new URLs on the page" % len(pages))
    db.session.add_all(pages)
    if recipe is not None:
      print("Page contained a recipe")
      db.session.add(Recipe(
        page_id=page.id,
        recipe_info=recipe
      ))
  else:
    print("Seeding recipe URLs")
    db.session.add_all([
      Page(url="https://www.epicurious.com/"),
      Page(url="https://www.skinnytaste.com/"),
      Page(url="https://www.allrecipes.com/")
    ])
  db.session.commit()