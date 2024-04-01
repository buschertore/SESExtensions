import os
import subprocess
import logging
import time
from multiprocessing import Pool

import githubMetricGetter
import ChromeReviews
#import FastFireFoxReviews
import chromePermissions


def getReviews(chromeLink: str, firefoxLink: str, name: str) -> None:
    if firefoxLink != "":
        #FastFireFoxReviews.main([firefoxLink, f"data/{dirName}/firefoxReviews.json"])
        pass

    if chromeLink != "":
        ChromeReviews.main([f"{chromeLink}/reviews", f"data/extensions/{name}/chromeReviews.json"])

def getPermissions(chromeLink: str, firefoxLink: str, name: str) -> None:
    if chromeLink != "":
        chromePermissions.main([chromeLink, f"data/extensions/{name}/manifest.json"])

def processRow(row):
    logging.debug(f"{row} splits into {row.split(',')}")
    dataDirName, chromeLink, firefoxLink, githubLink = row.split(",")

    #Setup data dir
    os.popen(f"mkdir data/extensions/{dataDirName}")
    if not githubLink.startswith("https://"):
        githubLink = f"https://{githubLink}"
    logging.info(f"Running git clone {githubLink}")
    #clone git for analysis
    process = subprocess.run(["git",  "clone", githubLink.strip(), f"data/tempCode/{dataDirName}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Cloning into 'requestly'...
    output = process.stdout.decode() + process.stderr.decode()
    logging.info(f"ouput is = {output}")
    codeDirName = f"data/tempCode/{dataDirName}"


    # setup & semgrep scan - write output to data dir
    """
    os.popen(f"cd {dirName} && python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install semgrep")
    command = "semgrep scan --emacs -j 4 --max-memory=6072 -q"
    semgrepProc = subprocess.run(command.split(" "), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    """
    #semgrep_command = "python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install semgrep && echo 'endOfPrep' && semgrep scan --emacs -j 4 --max-memory=6072 -q && deactivate"

    # Run semgrep command
    logging.info(f"switching to dir {codeDirName}/, running semgrep...")
    os.popen(f"cd {codeDirName}")
    # TODO eval if absolute path necessary
    command = f"semgrep scan --emacs -j 4 --max-memory=6072 -q {codeDirName}"
    semgrepProc = subprocess.run(command.split(" "), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    semgrepOutput = semgrepProc.stdout.decode() + semgrepProc.stderr.decode()
    logging.info(f"semgrep out length = {len(semgrepOutput)}")
    with open (f"data/extensions/{dataDirName}/semgrep.txt", "w") as out:
        out.write(semgrepOutput)
    logging.info("done with semgrep, running owasp dc...")


    #run owasp check & copy result file
    # TODO edit path the owasp DC
    os.popen(f"cd {codeDirName};/home/user/PycharmProjects/SESExtensions/owaspDC/dependency-check/bin/dependency-check.sh -s .").read()
    os.popen(f"mv {codeDirName}/dependency-check-report.html data/extensions/{dataDirName}").read()
    logging.info("owasp dc done, cleaning up...")

    # Get necessary info about permissions
    #getReviews(chromeLink=chromeLink, firefoxLink=firefoxLink, name=dataDirName)
    with open(f"data/extensions/{dataDirName}/starRating.txt", "w") as ratingFile:
        ratingFile.write(str(ChromeReviews.fetchStarRating(chromeLink=chromeLink)))
    getPermissions(chromeLink=chromeLink, firefoxLink=firefoxLink, name=dataDirName)

    os.popen(f"rm -r {codeDirName}/")


    # Get GitHub Metrics
    githubMetricGetter.main([githubLink, f"data/extensions/{dataDirName}/gitHubMetrics.txt"])


def callProcessRow(rowAndNum):
    try:
        row, num = rowAndNum
    except Exception as e:
        logging.error(f"Failed to UNPACK: {rowAndNum}")
        row = "Error"
        num = 0
    try:

        with open("data/doneExtensions.csv", "r") as done:
            if row not in done:
                processRow(row)
                with open("data/doneExtensions.csv", "a") as log:
                    log.write(row)
        logging.info(f"processed row {num}")
    except Exception as e:
        logging.error(f"Error with row: {row.strip()}: {e}")


def main():

    logging.basicConfig(level=logging.INFO)

    with open("data/mergedCSV.csv") as extensionList:
        rows = extensionList.readlines()

    # drop header row
    #rows = rows[1:]
    #rows.reverse()

    logging.info(f"Found {len(rows)} rows")
    logging.debug(f"{rows[0].split(',')}")


    allArgs = [(row, num) for num, row in enumerate(rows)]
    with Pool(processes=48) as pool:
        pool.map(callProcessRow, allArgs)

if __name__ == "__main__":
    main()