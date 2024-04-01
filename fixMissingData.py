import logging
import os
import shutil
import sys
from multiprocessing import Pool

import ChromeReviews
import controller


def getCSVDict() -> {}:
    with open("data/doneExtensions.csv") as doneFile:
        rows = doneFile.readlines()
    dict = {}
    for row in rows:
        dict[row.split(",")[0]] = row

    return dict


def writeChromeMetrics(filePathAndLink):
    logging.info(f"Found {filePathAndLink}")
    path, link = filePathAndLink

    rating = str(ChromeReviews.fetchStarRating(chromeLink=link))

    with open(path, "w") as metricsFile:
        metricsFile.write(rating)


def main(argv):
    logging.basicConfig(level=logging.INFO)


    subfolders = [f.path for f in os.scandir("data/extensions") if f.is_dir()]
    #allExtensionScores = []
    allLines = []
    rmList = []
    fixArgList = []
    nameToRow = getCSVDict()
    allChromePathsAndLinks = []
    for subfolder in subfolders:
        logging.info(f"Checking subfolder {subfolder}")
        name = subfolder.split("/")[-1]
        logging.info(f"Exctracted {name}")
        chromeLink = nameToRow[name].split(",")[1]
        logging.info(f"Exctracted {chromeLink}")

        allChromePathsAndLinks.append((f"{subfolder}/chromeMetrics.txt", chromeLink))



        """        missingOwasp = False
        missingJson = False
        logging.info(f"Checking subfolder {subfolder}")
        try:
            with open(f"{subfolder}/dependency-check-report.html") as owaspDC:
                lines = owaspDC.readlines()
        except FileNotFoundError as e:
            logging.error(f"Missing owasp for {subfolder}")
            missingOwasp = True
        try:
            with open(f"{subfolder}/manifest.json") as manifest:
                lines = manifest.readlines()
        except FileNotFoundError as e:
            logging.error(f"Missing manifest for {subfolder}")
            missingJson = True

        nameToRow = getCSVDict()

        if missingOwasp or missingJson:
            rmList.append(subfolder)
            logging.warning(f"appending: {(nameToRow[subfolder.split('/')[-1]], 0)} to fixArgList")
            fixArgList.append((nameToRow[subfolder.split("/")[-1]], 0))

    logging.warning(f"Found {len(rmList)} rows with missing files")

    for rmFolder in rmList:
        shutil.rmtree(f"{rmFolder}")

    with Pool(processes=48) as pool:
        pool.map(controller.callProcessRow, fixArgList)"""

    with Pool(processes=24) as pool:
        pool.map(writeChromeMetrics, allChromePathsAndLinks)


if __name__ == "__main__":
    main(sys.argv)