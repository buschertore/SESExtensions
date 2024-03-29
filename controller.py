import os
import subprocess
import logging
import time
import githubMetricGetter
import ChromeReviews
#import FastFireFoxReviews
import chromePermissions


def getReviews(chromeLink: str, firefoxLink: str, name: str) -> None:
    if firefoxLink != "":
        #FastFireFoxReviews.main([firefoxLink, f"data/{dirName}/firefoxReviews.json"])
        pass

    if chromeLink != "":
        ChromeReviews.main([f"{chromeLink}/reviews", f"data/{name}/chromeReviews.json"])

def getPermissions(chromeLink: str, firefoxLink: str, name: str) -> None:
    if chromeLink != "":
        chromePermissions.main([chromeLink, f"/home/codescan/data/{name}/manifest.json"])

def processRow(row):
    logging.debug(f"{row} splits into {row.split(',')}")
    dataDirName, chromeLink, firefoxLink, githubLink = row.split(",")

    #Setup data dir
    os.popen(f"mkdir data/{dataDirName}")

    logging.info("Running git clone...")
    #clone git for analysis
    process = subprocess.run(["git",  "clone", githubLink.strip()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Cloning into 'requestly'...
    output = process.stdout.decode() + process.stderr.decode()
    logging.debug(f"ouput is = {output}")
    codeDirName = output.split("'")[1]


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
    command = f"semgrep scan --emacs -j 4 --max-memory=6072 -q /home/codescan/{codeDirName}"
    semgrepProc = subprocess.run(command.split(" "), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    semgrepOutput = semgrepProc.stdout.decode() + semgrepProc.stderr.decode()
    logging.info(f"semgrep out length = {len(semgrepOutput)}")
    with open (f"data/{dataDirName}/semgrep.txt", "w") as out:
        out.write(semgrepOutput)
    logging.info("done with semgrep, running owasp dc...")


    #run owasp check & copy result file
    os.popen("cd /home/codescan/")
    os.popen(f"~/dependency-check/bin/dependency-check.sh -s ./{codeDirName}").read()
    os.popen(f"mv ./dependency-check-report.html data/{dataDirName}")
    logging.info("owasp dc done, cleaning up...")
    os.popen(f"rm -r {codeDirName}/")
    resetDir = os.popen("cd /home/codescan")
    logging.debug(resetDir.readlines())

    # Get necessary info about permissions
    getReviews(chromeLink=chromeLink, firefoxLink=firefoxLink, name=dataDirName)
    with open(f"data/{dataDirName}/starRating.txt", "w") as ratingFile:
        ratingFile.write(str(ChromeReviews.fetchStarRating(chromeLink=chromeLink)))
    getPermissions(chromeLink=chromeLink, firefoxLink=firefoxLink, name=dataDirName)

    # Get GitHub Metrics
    githubMetricGetter.main([githubLink, f"data/{dataDirName}/gitHubMetrics.txt"])






def main():

    logging.basicConfig(level=logging.INFO)

    with open("extensionList.csv") as list:
        rows = list.readlines()

    # drop header row
    rows = rows[1:]
    rows.reverse()

    logging.info(f"Found {len(rows)} rows")
    logging.debug(f"{rows[0].split(',')}")

    for num, row in enumerate(rows):
        processRow(row)
        logging.info(f"processed row {num}")


if __name__ == "__main__":
    main()