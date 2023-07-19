import pandas as pd
import pyworms
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def gen_worms_lookup(occurrence: pd.DataFrame, target_column: str):
    # Create empty dataframe with unique scientific names
    worms_lut = pd.DataFrame(
        columns=["scientificName"], data=occurrence[target_column].unique()
    )

    # Add empty columns for each header
    headers = [
        "acceptedname",
        "acceptedID",
        "scientificNameID",
        "kingdom",
        "phylum",
        "class",
        "order",
        "family",
        "genus",
        "scientificNameAuthorship",
        "taxonRank",
    ]
    for head in headers:
        worms_lut[head] = ""

    # Query pyworms for each scientific name and add results to lut_worms
    for index, row in worms_lut.iterrows():
        logger.debug("Searching for scientific name = %s" % row["scientificName"])
        resp = pyworms.aphiaRecordsByMatchNames(row["scientificName"])[0][0]
        worms_lut.loc[index, "acceptedname"] = resp["valid_name"]
        worms_lut.loc[index, "acceptedID"] = resp["valid_AphiaID"]
        worms_lut.loc[index, "scientificNameID"] = resp["lsid"]
        worms_lut.loc[index, "kingdom"] = resp["kingdom"]
        worms_lut.loc[index, "phylum"] = resp["phylum"]
        worms_lut.loc[index, "class"] = resp["class"]
        worms_lut.loc[index, "order"] = resp["order"]
        worms_lut.loc[index, "family"] = resp["family"]
        worms_lut.loc[index, "genus"] = resp["genus"]
        worms_lut.loc[index, "scientificNameAuthorship"] = resp["authority"]
        worms_lut.loc[index, "taxonRank"] = resp["rank"]

    return worms_lut


def preview_changes(df, target_column: str):
    worms_lut = gen_worms_lookup(df, target_column)

    # create a dictionary to store before/after values
    preview = {}

    for name in df[target_column].unique():
        original = df.loc[df[target_column] == name, "acceptedname"].values[0]
        new = worms_lut.loc[worms_lut["scientificName"] == name, "acceptedname"].values[
            0
        ]

        if original != new:
            preview[name] = {"before": original, "after": new}

    return preview
