import logging
import sys
import time
from typing import List

from utils import extensionCSVRow

#

def readAllCSVs() -> []:
    # Read all extension Csvs
    csvList = ["data/make_chrome_yoursaccessibilitySuggestedLinks.csv",
               "data/make_chrome_yoursfunctionalitySuggestedLinks.csv",
               "data/make_chrome_yoursprivacySuggestedLinks.csv",
               "data/productivitycommunicationSuggestedLinks.csv",
               "data/productivitydeveloperSuggestedLinks.csv",
               "data/productivityeducationSuggestedLinks.csv",
               "data/productivitytoolsSuggestedLinks.csv",
               "data/productivityworkflowSuggestedLinks.csv"
               ]

    allRows = []

    for csvFile in csvList:
        with open(csvFile, "r") as inFile:
            for row in inFile.readlines():
                try:
                    allRows.append(extensionCSVRow(name=row.split(",")[1].split("/")[-2], chromeLink=row.split(",")[1], gitHubLink=row.split(",")[3]))
                except Exception as e:
                    logging.warning(f"")

    return allRows


def filterRows(rows: List[extensionCSVRow]) -> List[extensionCSVRow]:
    newRows = []
    for row in rows:
        #logging.info(row.gitHubLink)
        #gitHubLinkParts = row.chromeLink.split("/")
        #gitHubLink = "".join(gitHubLinkParts[:2])
        newRows.append(extensionCSVRow(name=row.name, chromeLink=row.chromeLink, gitHubLink=row.gitHubLink))
        #logging.info(gitHubLink)

    return newRows

def main(args):


    logging.basicConfig(level=logging.INFO)
    logging.warning(f"Started running at: {time.ctime()}")

    allRawRows = readAllCSVs()
    allRows = filterRows(allRawRows)
    logging.info(f"Found {len(allRawRows)} extensions")

    with open("data/mergedCSV.csv", "w") as out:
        for row in allRows:
            out.write(f"{row.name},{row.chromeLink},,{row.gitHubLink}")

    logging.warning(f"Ended at {time.ctime()}")

if __name__ == "__main__":
    main(sys.argv[1:])