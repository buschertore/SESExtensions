from datetime import datetime
import sys

from utils import Review
import selenium.common.exceptions
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import logging


def checkLink(link: str) -> str:
    if not link.startswith('https://github.com'):
        raise TypeError('Not a github link')
    if not link.endswith('/'):
        link += '/'

    return link.strip()

def extractDateFromCommit(commitSpan) -> datetime:
    stringDate = commitSpan.get_attribute("title")
    logging.debug(f"Commit date: {stringDate}")
    logging.debug(f"text: {commitSpan.text}")
    # Example date from GitHub:     Mar 6, 2024, 3:54 PM GMT+1
    #Trim timezone
    stringDate = stringDate[:-6]
    date = datetime.strptime(stringDate, "%b %d, %Y, %I:%M %p")
    logging.debug(f"Found date to be: {date.isoformat()}")
    return date

def calculateAverageTimeDifference(allDates) -> str | float | int:
    if len(allDates) == 0:
        logging.warning("Commit time check failed. No commits in /activity -> max penalty")
        return 999
    # Calculate the time difference between the first datetime and now
    firstDate = allDates[0]
    now = datetime.now()
    timeDifferenceFirst = (now - firstDate).days

    # Calculate the time difference between consecutive datetime elements
    totalDays = 0
    for i in range(len(allDates) - 1):
        timeDiff = (allDates[i] - allDates[i + 1]).days
        totalDays += timeDiff

    # Calculate the average time difference
    totalElements = len(allDates)
    if totalElements > 1:
        averageDays = (totalDays + timeDifferenceFirst) / totalElements
    else:
        averageDays = timeDifferenceFirst  # Only one datetime, return the difference

    return averageDays

def findMajorContributors(allCommitCounts):
    numberOfContributors = len(allCommitCounts)
    if numberOfContributors >= 100:
        return sum(1 for num in allCommitCounts if num > 10)
    elif numberOfContributors >= 50:
        return sum(1 for num in allCommitCounts if num > 5)
    elif numberOfContributors >= 10:
        return sum(1 for num in allCommitCounts if num > 1)
    else:
        return len(allCommitCounts)


def getContributors(driver, link):
    contributorLinks = getContribLinkandWait(driver, link, 4)
    if len(contributorLinks) != 0:
        logging.info(f"Found {len(contributorLinks)} after 7.5")
        return contributorLinks
    contributorLinks = getContribLinkandWait(driver, link, 11)
    if len(contributorLinks) != 0:
        logging.info(f"Found {len(contributorLinks)} after 15")
        return contributorLinks
    contributorLinks = getContribLinkandWait(driver, link, 30)
    if len(contributorLinks) == 0:
        return ""
    logging.info(f"Found {len(contributorLinks)} after 30")
    return contributorLinks

def getContribLinkandWait(driver, link, arg2):
    driver.get(link)
    time.sleep(arg2)
    return driver.find_elements(By.PARTIAL_LINK_TEXT, "commit")



def main(argv):
    # sourcery skip: extract-duplicate-method, inline-immediately-returned-variable
    if not argv:
        argv = ["https://github.com/greatsuspender/thegreatsuspender", "githubMetricsTheGreatSuspender.txt"]

    link = argv[0]
    gitHubMetricFileName = argv[1]

    #ensure correctness of link
    link = checkLink(link)

    activityLink = f"{link}activity"

    #Setup webdriver
    logging.basicConfig(level=logging.INFO)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    #Get activityPage
    driver.get(activityLink)
    time.sleep(3)
    logging.info("Started window")

    #extract elements
    allCommits = driver.find_elements(By.CSS_SELECTOR, ".Text-sc-17v1xeu-0.gPDEWA")
    # filter out button that is not a date
    for commit in allCommits:
        if commit.text.strip() == "All users":
            allCommits.remove(commit)
    logging.info(f"Found {len(allCommits)} commits")


    allDates = []
    for commit in allCommits:
        try:
            allDates.append(extractDateFromCommit(commit))
        except ValueError as e:
            logging.info(f"Not a commit: datestring was: {commit.text}")
    allDates = allDates[:10]
    averageDays = calculateAverageTimeDifference(allDates)
    logging.info(f"average days: {averageDays}")


    #get contributors
    contribLink = f"{link}graphs/contributors".replace("\n", "").replace(" ", "")
    logging.info(f"contribLink: {contribLink}")

    contributorLinks = getContributors(driver=driver, link=contribLink)

    logging.info(f"Found {len(contributorLinks)} contribs")
    commitNumbers = [int(link.text.split("commit")[0].strip().replace(",", "")) for link in contributorLinks]
    majorContributors = findMajorContributors(commitNumbers)
    logging.info(f"found {majorContributors} major contributors")

    driver.close()
    # write results
    with open(gitHubMetricFileName, "w") as out:
        out.write(
            f"Average time between commits:{str(averageDays)}\n# of major contributors:{str(majorContributors)}\n# of non-major contributors:{len(commitNumbers)}"
        )




if __name__ == "__main__":
    main(sys.argv[1:])