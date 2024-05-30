import numpy as np
import pandas
import logging
from scipy.stats import spearmanr

logging.basicConfig(level=logging.INFO)
df = pandas.read_csv("results.csv")
logging.info(f"Columns are: {df.columns}")
logging.info(f"Unfiltered head: \n {df.head()}")

filteredDf = df[df["manualWork"] != "yes"]
logging.info(f"filtered head: \n {filteredDf.head()}")








owaspSemgrepCorr = filteredDf["owasp"].corr(filteredDf["semgrep"], method="spearman")

logging.critical(f"Correlation owasp to semgrep {owaspSemgrepCorr}")

# drop row with only headings
#df = df.iloc[1: , :]

# remove the column manual work & name so that only numeric values are left

cutDf = filteredDf.filter(["owasp", "semgrep", "permission", "contributor", "activity", "manifestVersion"])

correlationMatrix = cutDf.corr(method="spearman")
pvalueMatrix = cutDf.corr(method=lambda x,y: spearmanr(x,y)[1])

logging.critical(f"Correlation matrix {correlationMatrix}")
logging.critical(f"P-value matrix {pvalueMatrix}")

correlationMatrix.to_csv("correlationMatrix.csv")
pvalueMatrix.to_csv("pvalueMatrix.csv")
