import contextlib
import os
import sys
from multiprocessing import Pool

import ChromeReviews
import githubMetricGetter


def relaunchGitHubMetrics(args):
    extensionName, link = args
    try:
        with open(f"data/extensions/{extensionName}/gitHubMetrics.txt") as inFile:
            commitTimeString = inFile.readline().split(":")[-1]
            #commitTime = float(commitTimeString)
            majorContributorsString = inFile.readline().split(":")[-1]
            majorContributors = int(majorContributorsString)
    except FileNotFoundError:
        majorContributors = 0
    if(majorContributors == 0):
        print(f"Regathering github for {extensionName}")
        os.popen(f"rm data/extensions/{extensionName}/gitHubMetrics.txt")
        try:
            githubMetricGetter.main([link, f"data/extensions/{extensionName}/gitHubMetrics.txt"])
        except Exception as e:
            print(f"No file for {extensionName}: {e}")


def relaunchChromeStoreRatings(listOfDirAndLink) -> None:
    extensionName, chromeLink = listOfDirAndLink
    try:
        with open(f"data/extensions/{extensionName}/chromeMetrics.txt") as inFile:
            oldUserNumber = inFile.readline().split(":")[-1]
            recommended = inFile.readline().split(":")[-1]
    except FileNotFoundError:
        oldUserNumber = 0
    # TODO remove again
    #oldUserNumber = 0
    if oldUserNumber == 0:
        print(f"Regetting chrome metrics for {extensionName}: {chromeLink}")
        numberOfUsers, recommended = ChromeReviews.fetchChromeRatings(chromeLink)
        print(f"Number of users: {numberOfUsers}, recommended: {recommended}")
        if os.path.exists(f"data/extensions/{extensionName}/chromeMetrics.txt"):
            os.remove(f"data/extensions/{extensionName}/chromeMetrics.txt")
        with open(f"data/extensions/{extensionName}/chromeMetrics.txt", "w") as outFile:
            outFile.write(f"NumberOfUsers: {numberOfUsers}\n")
            outFile.write(f"isRecommended: {recommended}\n")
    else:
        print(f"Skipping chrome store for {extensionName}")
        #pass





def main(argv):

    subfolders = [f.name for f in os.scandir("data/extensions") if f.is_dir()]

    with open("data/doneExtensions.csv") as list:
        rows = list.readlines()
        rows = rows[1:]
    gitHubLinkDict = {}
    chromeLinkDict = {}
    for row in rows:
        dataDirName, chromeLink, firefoxLink, githubLink = row.split(",")
        gitHubLinkDict[dataDirName] = githubLink
        chromeLinkDict[dataDirName] = chromeLink

    """    args_list = [(subfolder, gitHubLinkDict[subfolder]) for subfolder in subfolders]
    with Pool(processes=36) as pool:
        pool.map(relaunchGitHubMetrics, args_list)"""


    chromeMetricArgs = [(subfolder, chromeLinkDict[subfolder]) for subfolder in subfolders]
    with Pool(processes=100) as pool:
        pool.map(relaunchChromeStoreRatings,chromeMetricArgs)


if __name__ == "__main__":
    main(sys.argv[1:])

