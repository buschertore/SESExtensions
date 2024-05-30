import json
import logging
import os
import sys
from utils import ExtensionScore

from bs4 import BeautifulSoup


def scoreSemgrep(file_path: str) -> int:
    # Initialize score
    total_score = 0

    try:
        # Open the file and read lines
        with open(file_path, 'r') as file:
            for line in file:
                # Check if the line starts with '/home/'
                if line.startswith('data/'):
                    # Check for the presence of 'error' and 'warning' in the line
                    if ':error' in line:
                        total_score += 2
                    elif ':warning' in line:
                        total_score += 0.5

    except FileNotFoundError:
        logging.error(f"No semgrepFile for {file_path}")
        raise ValueError(f"File not found: {file_path}")

    # Return the total score
    return int(total_score)


def scorePermissions(file_path: str) -> int:
    # Initialize scores for each word
    word_scores = {"storage": 4, "contextMenus": 2, "certificateProvider": 10, "identity": 10, "platformKeys": 10,
                   "vpnProvider": 10, "u2fDevices": 2, "audioCapture": 4, "desktopCapture": 4,
                   "app.window.fullscreen": 2,
                   "hid": 2, "printerProvider": 4, "serial": 4, "usb": 4, "videoCaptuer": 4, "clipboardRead": 2,
                   "fileSystem": 10, "fileSystemProvider": 10, "mediaGalleries": 4, "syncFileSytem": 4,
                   "unlimitedStorage": 4,
                   "webRequestBlocking": 3, "networking.config": 3, "experimental": 3, "gcm": 3, "proxy": 3,
                   "webRequest": 4,
                   "system.cpu": 5, "system.display": 5, "enterprise_deviceAttributes": 10, "system.memory": 5,
                   "nativeMessaging": 10, "system.network": 5, "power": 10, "system.storage": 5, "alarms": 2,
                   "notifications": 2, "app.window.fullscreen.overrideEsc": 2, "tts": 2}

    # Initialize total score
    total_score = 0

    try:
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Check if the 'permissions' key exists in the JSON data
        if 'permissions' in data:
            # Check for each word and increment the total score
            for word, score in word_scores.items():
                if word in data['permissions']:
                    total_score += score

        return int(total_score)

    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON in file: {file_path}")


def scoreOwaspDC(owaspHTMLFile: str) -> int:
    # Moderate is not an actual CVE category. It is assigned 0 points
    categoryWeights = {"CRITICAL": 15, "HIGH": 7.5, "MEDIUM": 4, "LOW": 2, "MODERATE": 0}

    with open(owaspHTMLFile) as inFile:
        soup = BeautifulSoup(inFile, 'html.parser')

    penalty = 0
    allVulnerabilities = soup.find_all("tr", class_="vulnerable")
    logging.debug(f"found {len(allVulnerabilities)} vulns")
    for vulnerability in allVulnerabilities:
        categoryTd = vulnerability.findChildren(recursive=False)[3]
        category = categoryTd.text
        logging.debug(f"category: {category}")
        penalty += categoryWeights[category]

    logging.info(f"penalty: {round(penalty)}")
    return round(penalty)


"""calculates scores for activity and contributors: [activityScore, contributorScore]"""


def scoreGithubMetrics(githubHTMLFile: str) -> []:
    with open(githubHTMLFile) as inFile:
        commitTimeString = inFile.readline().split(":")[-1]
        commitTime = float(commitTimeString)
        commitPenalty = max(commitTime - 0.5, 0) * 0.05
        commitPenalty = min(round(commitPenalty), 10)

        majorContributorsString = inFile.readline().split(":")[-1]
        majorContributors = int(majorContributorsString)
        # TODO validate formula
        contribPenalty = max(majorContributors - 8, 0)
        contribPenalty = min(contribPenalty, 10)
        if majorContributors == 0:
            raise ValueError("No major contributors")


    return [commitPenalty, contribPenalty]


def readStarRatingFile(starRatingFile) -> float:
    with open(starRatingFile) as inFile:
        try:
            return float(inFile.readline())
        except Exception as e:
            return float(-1)


"""Returns the chrome metrics: [users, recommended]"""
def readChromeMetrics(chromeMetricFile: str) -> []:
    with open(chromeMetricFile) as inFile:
        try:
            numberOfUsers = int(inFile.readline().split(":")[-1])
            recommended = inFile.readline().split(":")[-1].strip()
        except Exception as e:
            numberOfUsers = 0
            recommended = -1

    return [numberOfUsers, recommended]


def readManifestVersion(manifestFilePath: str) -> str:
    rawText = open(manifestFilePath).read()
    manifestJson = json.loads(rawText)
    return manifestJson["manifest_version"]


def main(argv):
    logging.basicConfig(level=logging.INFO)

    # get list of all directories to scan
    # TODO change folder
    subfolders = [f.path for f in os.scandir("data/extensions") if f.is_dir()]
    #allExtensionScores = []
    allLines = []
    for subfolder in subfolders:
        manualWork = "no"
        name = subfolder.split("/")[-1]



        try:
            owaspRaw = scoreOwaspDC(f"{subfolder}/dependency-check-report.html")
            owaspPenalty = min(40, owaspRaw)
            semgrepRaw = scoreSemgrep(f"{subfolder}/semgrep.txt")
            semgrepPenalty = min(40, semgrepRaw)
            permissionRaw = scorePermissions(f"{subfolder}/manifest.json")
            permissionPenalty = min(20, permissionRaw)
            try:
                activityRaw, contribRaw = scoreGithubMetrics(f"{subfolder}/gitHubMetrics.txt")
                activityPenalty = min(activityRaw, 10)
                contribPenalty = min(contribRaw, 10)
            except ValueError as ve:
                activityRaw = -1
                contribRaw = -1
                activityPenalty = -1
                contribPenalty = -1
                manualWork = "yes"
            overallScore = max(0,
                               100 - owaspPenalty - semgrepPenalty - permissionPenalty - activityPenalty - contribPenalty)
            starRating = readStarRatingFile(f"{subfolder}/starRating.txt")
            if starRating == float(-1):
                manualWork = "yes"
            users, recommended = readChromeMetrics(f"{subfolder}/chromeMetrics.txt")
            manifestVersion = readManifestVersion(f"{subfolder}/manifest.json")
            logging.info(f"name: {name} score: {overallScore} of rating: {starRating} | manual work?: {manualWork}")
            """allExtensionScores.append(
                ExtensionScore(name=name, owaspPenalty=owaspPenalty, semgrepPenalty=semgrepPenalty,
                               permissionPenalty=permissionPenalty, contributorPenalty=contribPenalty,
                               activityPenalty=activityPenalty, overallScore=overallScore,
                               starRating=starRating, manualWorkNeeded=manualWork))"""
            #"name,overallScore,starRating,users,recommended,owasp,owaspRaw,semgrep,semgrepRaw,permission,permissionRaw,contributor,contributorRaw,activity,activityRaw,manualWork\n"
            allLines.append(
                ",".join(
                    [
                        str(name),
                        str(overallScore),
                        str(starRating),
                        str(users),
                        str(recommended),
                        str(owaspPenalty),
                        str(owaspRaw),
                        str(semgrepPenalty),
                        str(semgrepRaw),
                        str(permissionPenalty),
                        str(permissionRaw),
                        str(contribPenalty),
                        str(contribRaw),
                        str(activityPenalty),
                        str(activityRaw),
                        str(manualWork),
                        str(manifestVersion),
                    ]
                )
            )
        except Exception as e:
            logging.error(e)
            logging.error(f"Error occured while scoring {subfolder}: {e.args} | {type(e)}")
            """allExtensionScores.append(ExtensionScore(name=name, owaspPenalty=0, semgrepPenalty=0, permissionPenalty=0,
                                                     contributorPenalty=0, activityPenalty=0, overallScore=0,
                                                     starRating=0, manualWorkNeeded="yes"))"""

    with open("results.csv", "w") as csvfile:
        #csvfile.write("name,owasp,semgrep,permission,contributor,activity,overallScore,starRating,manualWorkNeeded\n")
        csvfile.write("name,overallScore,starRating,users,recommended,owasp,owaspRaw,semgrep,semgrepRaw,permission,permissionRaw,contributor,contributorRaw,activity,activityRaw,manualWork,manifestVersion\n")
        """for score in allExtensionScores:
            csvfile.write(
                f"{score.name},{score.owaspPenalty},{score.semgrepPenalty},{score.permissionPenalty},{score.contributorPenalty},{score.activityPenalty},{score.overallScore},{score.starRating},{score.manualWorkNeeded}\n")"""
        for line in allLines:
            csvfile.write(f"{line}\n")


if __name__ == "__main__":
    main(sys.argv)
