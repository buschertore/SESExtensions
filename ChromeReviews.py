import string
import sys

from utils import Review
import selenium.common.exceptions
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import logging


def extractSectionDataFromHTML(seleniumSection) -> Review:
    star = int(seleniumSection.find_element(By.CLASS_NAME, "B1UG8d").get_attribute("title")[0])
    date = seleniumSection.find_element(By.CLASS_NAME, "ydlbEf").text
    review = seleniumSection.find_element(By.CLASS_NAME, "fzDEpf").text

    return Review(text=review, date=date, stars=star)

def main(argv):
    if not argv:
        argv = ["https://chromewebstore.google.com/detail/mdnleldcmiljblolnjhpnblkcekpdkpa", "data/RequestlyReviewsChrome.json"]
    link = argv[0]
    reviewFileName = argv[1]

    logging.basicConfig(level=logging.INFO)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    #webdriver_service = Service("./chromedriver/chrome") #Your chromedriver path
    #driver = webdriver.Chrome(service=webdriver_service,options=options)
    driver = webdriver.Chrome(options=options)

    data = []
    driver.get(link)
    driver.maximize_window()
    time.sleep(3)
    logging.info("Started window")


    clickCounter = 0

    while True:
        try:
            #driver.find_element(By.CLASS_NAME, "mUIrbf-LgbsSe mUIrbf-LgbsSe-OWXEXe-dgl2Hf").click()
            driver.find_element(By.XPATH, "//div[normalize-space()='Load more']").click()
            clickCounter += 1
            logging.info(f"Found & clicked 'load more' number: {clickCounter}")
            time.sleep(0.5)
        except selenium.common.exceptions.NoSuchElementException as e:
            logging.warning(e.msg)
            logging.warning(e.stacktrace)
            break

    allSections = driver.find_elements(By.CLASS_NAME, "T7rvce")
    sections = [extractSectionDataFromHTML(section) for section in allSections]
    #print(sections)
    driver.close()
    #jsonObject = json.dumps(sections, indent=4)

    jsonObject = Review.schema().dumps(sections, many=True)

    with open(reviewFileName, "w") as outfile:
        outfile.write(jsonObject)


def fetchStarRating(chromeLink: str) -> float:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(chromeLink)
    time.sleep(3)

    scoreElement = driver.find_element(By.CLASS_NAME, "Vq0ZA")
    score = scoreElement.text
    logging.info(f"Fetched star rating: {score}")
    driver.close()
    if score == "":
        score = -1
    return float(score)



"""Returns [numberOfUsers, recommended(0/1)]"""
def fetchChromeRatings(chromeLink: str) -> []:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(chromeLink)
    time.sleep(2)

    numberOfUsersElement = driver.find_element(By.CLASS_NAME, "F9iKBc")
    numberOfUsers = numberOfUsersElement.text
    logging.info(f"Fetched string: {numberOfUsers}")
    # Get last line, then first part of that line
    numberOfUsers = numberOfUsers.split("\n")[-1].split(" ")[0].replace(",", "").replace(".", "")
    logging.info(f"Fetched number: {numberOfUsers}")
    try:
        recommendedBadge = driver.find_element(By.CLASS_NAME, "OmOMFc")
        recommended = 1
    except selenium.common.NoSuchElementException:
        recommended = 0

    driver.close()
    return [numberOfUsers, recommended]

if __name__ == "__main__":
    main(sys.argv[1:])
