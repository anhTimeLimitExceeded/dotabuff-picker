from calendar import c
import string
from tokenize import String
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json 
import pandas

HEROES_URL = "https://www.dotabuff.com/heroes"
HEROES_COUNTERS_URL = "https://www.dotabuff.com/heroes/{id}/counters"
def crawl_heroes():
  driver = webdriver.Firefox(executable_path='../selenium-drivers/geckodriver-0-31-0.exe')
  wait = WebDriverWait(driver, 100)
  heroes_json = {}
  HERO_GRID = "/html/body/div[2]/div[2]/div[3]/div[4]/section[2]/footer/div"
  driver.get(HEROES_URL)
  wait.until(EC.presence_of_element_located((By.XPATH, HERO_GRID)))
  soup = BeautifulSoup(driver.page_source, 'html.parser')
  driver.close()
  heroes = soup.find("div", {"class": "hero-grid"}).findChildren("a" , recursive=False)
  for hero in heroes:
    hero_json = {}
    hero_id = str(hero['href']).replace("/heroes/", "")
    hero_name = hero.find("div", {"class": "name"}).text
    hero_json["id"] = hero_id
    hero_json["name"] = str(hero_name)
    heroes_json[hero_id] = hero_json
  
  # Serializing json
  json_object = json.dumps(heroes_json, indent=2)
  with open("heroes.json", "w") as outfile:
    outfile.write(json_object)

def crawl_stats():
  driver = webdriver.Firefox(executable_path='../selenium-drivers/geckodriver-0-31-0.exe')
  wait = WebDriverWait(driver, 100)
  COUNTERS_TABLE_XPATH = "/html/body/div[2]/div[2]/div[3]/div[4]/section[3]/article/table"

  f = open("heroes.json", "r")
  heroes_json = json.load(f)
  count = 0
  for hero_json in heroes_json.values():    
    url = str.format(HEROES_COUNTERS_URL, id=hero_json['id'])
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.XPATH, COUNTERS_TABLE_XPATH)))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    counters = soup.find("table", {"class": "sortable"}).find("tbody" , recursive=False).findChildren("tr" , recursive=False)
    heroes_counters_json = {}
    for counter in counters:
      hero_id = counter.find("a", {"class": "link-type-hero"})['href'].replace("/heroes/", "")
      hero_percentage = counter.find("td", {"class": "sorted"}).text
      heroes_counters_json[hero_id] = hero_percentage
    hero_json['counters'] = heroes_counters_json
    count += 1
    if count == 10:
      # Serializing json
      json_object = json.dumps(heroes_json, indent=2)
      with open("heroes.json", "w") as outfile:
        outfile.write(json_object)
  # Serializing json
  json_object = json.dumps(heroes_json, indent=2)
  with open("heroes.json", "w") as outfile:
    outfile.write(json_object)
  driver.close()

def pick():
  enemies = ["zeus", "lion"]
  columns = []
  columns.extend(enemies)
  columns.append("total")
  result = pandas.DataFrame(columns=columns)
  f = open("heroes.json", "r")
  heroes_json = json.load(f)
  for hero in heroes_json: 
    if hero in enemies: 
      continue
    total_score = 0
    row = []
    for enemy in enemies:
      score = float(heroes_json[enemy]['counters'][hero])
      row.append(score)
      total_score += score
    row.append(total_score)
    result.loc[hero] = row
  
  result.sort_values('total', ascending=False, inplace=True)
  print(result.to_string())

# crawl_heroes()
crawl_stats()
# pick()