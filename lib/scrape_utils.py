from urllib.request import urlopen
from urllib.parse import urlparse
import microdata
from bs4 import BeautifulSoup
import re

def scrape(url):
  try:
    parsed_uri = urlparse(url)
    response = urlopen(url)
    html = response.read()
    items = microdata.get_items(html)
    recipe = None
    if len(items) > 0:
      for item in items:
        if str(item.itemtype[0]).endswith("/Recipe"):
          instructions = []
          ingredients = []
          if item.recipeInstructions is not None:
            for instruction in item.get_all("recipeInstructions"):
              splitted = instruction.split("\n")
              for line in splitted:
                clean = line.strip()
                if clean != "":
                  instructions.append(clean)
          if item.ingredients is not None:
            ingredients = item.get_all("ingredients")
          if item.recipeIngredient is not None:
            ingredients = item.get_all("recipeIngredient")
          if len(ingredients) > 0 and len(instructions) > 0:
            recipe = {
              "name": item.name,
              "ingredients": ingredients,
              "instructions": instructions
            }
    soup = BeautifulSoup(markup=html, features="html5lib")
    hrefs = []
    for link in soup.findAll('a'):
      href = link.get('href')
      parsed_sub_uri = urlparse(href)
      if parsed_sub_uri.netloc == "" or parsed_sub_uri.netloc == parsed_uri.netloc:
        new_url = parsed_uri.scheme + "://" + parsed_uri.netloc + parsed_sub_uri.path
        if new_url != url:
          hrefs.append(new_url)
    return set(hrefs), recipe
  except Exception as e:
    print(e)
    return set([]), None