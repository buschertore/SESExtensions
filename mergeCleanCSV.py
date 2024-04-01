import logging
import os
import sys
import time
from typing import List

from utils import extensionCSVRow


#

def readAllUniqueCSVs() -> []:
    # Read all extension Csvs
    """    csvList = ["extensionList.csv",
               # "data/make_chrome_yoursaccessibilitySuggestedLinks.csv",
               # "data/make_chrome_yoursfunctionalitySuggestedLinks.csv",
               # "data/make_chrome_yoursprivacySuggestedLinks.csv",
               "data/productivitycommunicationSuggestedLinks.csv",
               "data/productivitydeveloperSuggestedLinks.csv",
               "data/productivityeducationSuggestedLinks.csv",
               "data/productivitytoolsSuggestedLinks.csv",
               # "data/productivityworkflowSuggestedLinks.csv"
               ]"""

    allRows = []
    allChromeLinks = []

    for csvFile in os.listdir("data/CSVs"):
        logging.info(f"file = {csvFile}")
        with open(f"data/CSVs/{csvFile}", "r") as inFile:
            for row in inFile.readlines():
                try:
                    chromeLink = row.split(",")[1]
                    if chromeLink not in allChromeLinks:
                        allRows.append(extensionCSVRow(name=row.split(",")[1].split("/")[-2], chromeLink=chromeLink,
                                                       gitHubLink=row.split(",")[3]))
                        allChromeLinks.append(chromeLink)
                except Exception as e:
                    logging.warning(f"")

    return allRows


def filterRows(rows: List[extensionCSVRow]) -> List[extensionCSVRow]:
    newRows = []
    for row in rows:
        row.gitHubLink = row.gitHubLink.removeprefix("https://").strip()
        # skip unclean rows
        if row.chromeLink.strip() in [
            "https://chromewebstore.google.com/detail/github-sidebar/lblnbldblpeiikndppnekobccdocccho",
        ] \
                or row.gitHubLink.strip() in ["github.com/ericuldall", "github.com/users"]:
            continue

        # Cleanup appendices
        newGitHubLink = row.gitHubLink.strip()
        possibleEndings = ["/issues", "/", ".", "blob/master/README.md", "/releases", ").",
                           "/tree/main/packages/extension#getting-started", "/wiki/Features",
                           "/blob/master/README.md#content", ")", "/blob/master/privacy-policy.md",
                           "/tree/main/code-review-emoji-guide.", "/blob/9e1f59/mux.go", "#how-to-contribute",
                           "/issues/17256;", "/issues/new/choose", "/issues/8", "/wiki", "#readme",
                           "/blob/master/LICENSE.md", "/blob/master/CHANGELOG.md", "/blob/master/LICENSE.md",
                           "/tree/main/code-review-emoji-guide",
                           "/issues/new?assignees=da-stoi&labels=URL+Add+Request&projects=&template=url-add-request.md&title=URL+Add+Request",
                           "/blob/main/CHANGELOG.md", ]

        if row.gitHubLink.strip() == "github.com/tulios":
            newGitHubLink = "github.com/tulios/json-viewer"
        if row.gitHubLink.strip() == "github.com/FlowCrypt":
            newGitHubLink = "github.com/FlowCrypt/flowcrypt-browser"
        if row.gitHubLink.strip() == "github.com/4thtech/static-assets/raw/main/pdf/licence.pdf":
            newGitHubLink = "github.com/4thtech/encryptor-extension"
        if row.gitHubLink.strip() == "github.com/abbeycampbell":
            newGitHubLink = "github.com/KabaLabs/Cypress-Recorder"

        for ending in possibleEndings:
            newGitHubLink = newGitHubLink.strip().removesuffix(ending)
        logging.info(f"Appending {newGitHubLink} from {row.gitHubLink}")

        try:
            firstSlashIndex = newGitHubLink.index("/")
            secondSlashIndex = newGitHubLink[firstSlashIndex + 1:].index("/") + firstSlashIndex + 1
            thirdSlashIndex = newGitHubLink[secondSlashIndex + 1:].index("/") + secondSlashIndex + 1
            newGitHubLink = newGitHubLink[:thirdSlashIndex]
            logging.info(f"Cut {newGitHubLink}, was {row.gitHubLink}")
        except ValueError:
            logging.debug(f"No third slash found in {newGitHubLink}")

        if newGitHubLink.count("/") != 2:
            logging.warning(f"Bad Link_: {newGitHubLink} was omitted")
            continue

        newRows.append(extensionCSVRow(name=row.name, chromeLink=row.chromeLink, gitHubLink=newGitHubLink))

    return newRows


def main(args):
    logging.basicConfig(level=logging.INFO)
    logging.warning(f"Started running at: {time.ctime()}")

    allRawRows = readAllUniqueCSVs()
    allRows = filterRows(allRawRows)
    logging.info(f"Found {len(allRawRows)} extensions, {len(allRows)} remain")

    with open("data/mergedCSV.csv", "w") as out:
        for row in allRows:
            out.write(f"{row.name},{row.chromeLink},,{row.gitHubLink}\n")

    logging.warning(f"Ended at {time.ctime()}")


if __name__ == "__main__":
    main(sys.argv[1:])
