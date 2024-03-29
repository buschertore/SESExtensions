import contextlib
import os
import sys
from multiprocessing import Pool

import ChromeReviews
import githubMetricGetter


def relaunchGitHubMetrics(args):
    extensionName, link = args
    try:
        with open(f"data/{extensionName}/gitHubMetrics.txt") as inFile:
            commitTimeString = inFile.readline().split(":")[-1]
            #commitTime = float(commitTimeString)
            majorContributorsString = inFile.readline().split(":")[-1]
            majorContributors = int(majorContributorsString)
    except FileNotFoundError:
        majorContributors = 0
    if(majorContributors == 0):
        print(f"Regathering github for {extensionName}")
        os.popen(f"rm data/{extensionName}/gitHubMetrics.txt")
        try:
            githubMetricGetter.main([link, f"data/{extensionName}/gitHubMetrics.txt"])
        except Exception:
            print(f"No file for {extensionName}")


def relaunchChromeStoreRatings(listOfDirAndLink) -> None:
    extensionName, chromeLink = listOfDirAndLink
    try:
        with open(f"data/{extensionName}/chromeMetrics.txt") as inFile:
            oldUserNumber = inFile.readline().split(":")[-1]
            recommended = inFile.readline().split(":")[-1]
    except FileNotFoundError:
        oldUserNumber = 0


    if oldUserNumber == 0:
        print(f"Regetting chrome metrics for {extensionName}: {chromeLink}")
        numberOfUsers, recommended = ChromeReviews.fetchChromeRatings(chromeLink)
        print(f"Number of users: {numberOfUsers}, recommended: {recommended}")
        if os.path.exists(f"data/{extensionName}/chromeMetrics.txt"):
            os.remove(f"data/{extensionName}/chromeMetrics.txt")
        with open(f"data/{extensionName}/chromeMetrics.txt", "w") as outFile:
            outFile.write(f"NumberOfUsers: {numberOfUsers}\n")
            outFile.write(f"isRecommended: {recommended}\n")





def main(argv):

    subfolders = [f.name for f in os.scandir("data/") if f.is_dir()]

    with open("extensionList.csv") as list:
        rows = list.readlines()
        rows = rows[1:]
    gitHubLinkDict = {}
    chromeLinkDict = {}
    for row in rows:
        dataDirName, chromeLink, firefoxLink, githubLink = row.split(",")
        gitHubLinkDict[dataDirName] = githubLink
        chromeLinkDict[dataDirName] = chromeLink

    args_list = [(subfolder, gitHubLinkDict[subfolder]) for subfolder in subfolders]
    with Pool(processes=100) as pool:
        pool.map(relaunchGitHubMetrics, args_list)


    chromeMetricArgs = [(subfolder, chromeLinkDict[subfolder]) for subfolder in subfolders]
    with Pool(processes=100) as pool:
        pool.map(relaunchChromeStoreRatings,chromeMetricArgs)


if __name__ == "__main__":
    main(sys.argv[1:])

