import dataclasses
import json
from dataclasses_json import dataclass_json
from selenium import webdriver


@dataclass_json
@dataclasses.dataclass
class Review:
    text: str
    date: str
    stars: int

@dataclass_json
@dataclasses.dataclass
class ExtensionScore:
    name: str
    semgrepPenalty: int
    owaspPenalty: int
    permissionPenalty: int
    activityPenalty: int
    contributorPenalty: int
    overallScore: int
    starRating: float
    manualWorkNeeded: str

def setUpWebdriver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)
