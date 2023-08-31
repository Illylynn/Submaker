from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait

import re
import time

def generate_affs(topic):
    search = "Generate subliminal affirmations for %s" % topic

    url = "https://www.perplexity.ai/search?q=%s&copilot=false" % search

    WINDOW_SIZE = "1920,1080"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    chrome_options.add_argument("window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.current_url != url)

    time.sleep(10)

    driver.get(driver.current_url)

    print(driver.current_url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    results = soup.select(".break-words.min-w-0>div>.prose.inline.leading-normal.break-words.min-w-0 > *")

    # Remove sure message
    results = results[1:-1]

    affs = []

    for result in results:
        
        text = re.sub("[1-9]\.", ".", result.text)
        text = re.sub("\n", "", text)
        text = re.sub("\.", ".|", text)
        
        affs.append(text)

    driver.quit()
    
    return affs
    
