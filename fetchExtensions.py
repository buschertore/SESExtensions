import sys
from multiprocessing import Pool
import re
import utils
from utils import Review
import selenium.common.exceptions
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import logging


# Make Chrome Yours
categoryListCustom = [
    "https://chromewebstore.google.com/category/extensions/make_chrome_yours/accessibility",
    "https://chromewebstore.google.com/category/extensions/make_chrome_yours/privacy",
    "https://chromewebstore.google.com/category/extensions/make_chrome_yours/functionality"
]

# Lifestyle
categoryListLifestyle = [
    "https://chromewebstore.google.com/category/extensions/lifestyle/household",
    "https://chromewebstore.google.com/category/extensions/lifestyle/art",
    "https://chromewebstore.google.com/category/extensions/lifestyle/news",
    "https://chromewebstore.google.com/category/extensions/lifestyle/travel",
    "https://chromewebstore.google.com/category/extensions/lifestyle/shopping",
    "https://chromewebstore.google.com/category/extensions/lifestyle/social",
    "https://chromewebstore.google.com/category/extensions/lifestyle/fun",
    "https://chromewebstore.google.com/category/extensions/lifestyle/games",
    "https://chromewebstore.google.com/category/extensions/lifestyle/entertainment",
    "https://chromewebstore.google.com/category/extensions/lifestyle/well_being"
]

# Productivity
categoryListProductivity = [
    "https://chromewebstore.google.com/category/extensions/productivity/developer",
    "https://chromewebstore.google.com/category/extensions/productivity/communication",
    "https://chromewebstore.google.com/category/extensions/productivity/education",
    "https://chromewebstore.google.com/category/extensions/productivity/tools",
    "https://chromewebstore.google.com/category/extensions/productivity/workflow"
]

categoryLists = [categoryListProductivity, categoryListLifestyle, categoryListCustom]


def testExtensionForGitHub(linkToChromeStore):
    # will return a str with length > 0 if test is positive, an empty string if test is negative
    driver = utils.setUpWebdriver()
    logging.debug(f"loading page for {linkToChromeStore}")
    driver.get(linkToChromeStore)
    time.sleep(0.5)
    #text = driver.find_element(By.XPATH, '//span[@jsname="bN97Pc"]').text
    text = driver.find_element(By.CLASS_NAME, "uORbKe").text
    logging.debug(f"Found description: {text}")
    try:
        match = re.search("github\.com\/[\S]+", text)
        gitHubLink = match.group()
    except AttributeError as e:
        gitHubLink = ""
    logging.info(f"Found link: {gitHubLink}")

    driver.close()
    if gitHubLink:
        return [linkToChromeStore, gitHubLink]
    else:
        return ""

def filterExtensionListForGitHub(extensionLinkList):
    logging.warning(f"Call to filter for github with a list len of: {len(extensionLinkList)}")

    with Pool(processes=6) as pool:
        allReturns = pool.map(testExtensionForGitHub, extensionLinkList)

    logging.info(allReturns)

    #Filtering empty returns:
    actualReturns = [linkTuple for linkTuple in allReturns if linkTuple]
    logging.info(f"Actual returns were: {actualReturns}")
    logging.warning(f"Found {len(actualReturns)} OSS extensions from {len(extensionLinkList)} tested extensions")

    return actualReturns

def analyzeCategory(link):
    driver = utils.setUpWebdriver()
    driver.get(link)
    time.sleep(5)
    logging.info(f"Loaded page for {link}")
    loadMoreCount = 0
    while loadMoreCount < 10:
        try:
            driver.find_element(By.CLASS_NAME, "mUIrbf-LgbsSe-OWXEXe-dgl2Hf").click()
            time.sleep(1)
            loadMoreCount += 1
        except selenium.common.NoSuchElementException as e:
            logging.debug(e)
    time.sleep(1)
    logging.info("Finished loading more extensions in category")
    allExtensionElementWrappers = driver.find_elements(By.CLASS_NAME, "cD9yc")
    logging.info(allExtensionElementWrappers)
    allExtensionLinks = []
    for element in allExtensionElementWrappers:
        extensionLinkElement = element.find_element(By.XPATH, "./child::*")

        logging.debug(f"Found extension link {extensionLinkElement}")
        extensionLink = extensionLinkElement.get_attribute("href")
        logging.debug(f"Found extension link {extensionLink}")
        allExtensionLinks.append(extensionLink)

    driver.close()
    linkTuples = filterExtensionListForGitHub(allExtensionLinks)

    #Store found extensions
    with open(f"data/{link[55:]}SuggestedLinks".replace("/", "")) as outFile:
        for linkTuple in linkTuples:
            outFile.write(f"{linkTuple[0].split('/')[-1]}, {linkTuple[0]},,{linkTuple[0]}")



def main(args):


    logging.basicConfig(level=logging.INFO)
    logging.warning(f"Started running at: {time.ctime()}")
    #Get activityPage
    for categoryList in categoryLists:
        for categoryLink in categoryList:
            analyzeCategory(categoryLink)

    #githubTuple = testExtensionForGitHub("https://chromewebstore.google.com/detail/rogold-level-up-roblox/mafcicncghogpdpaieifglifaagndbni")
    #logging.info(f'Result is = {githubTuple}')
    #logging.info(f'Result is = {testExtensionForGitHub("https://chromewebstore.google.com/detail/requestly-intercept-modif/mdnleldcmiljblolnjhpnblkcekpdkpa")}')


    logging.warning(f"Ended at {time.ctime()}")

if __name__ == "__main__":
    main(sys.argv[1:])