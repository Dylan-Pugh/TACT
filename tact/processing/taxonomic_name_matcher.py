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
        "matchType",
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

        try:
            resp = pyworms.aphiaRecordsByMatchNames(row["scientificName"])[0][0]
        except Exception as e:
            current_name = row["scientificName"]
            print(f"Lookup failed for: {current_name}. Error: {e}")
            continue
        
        worms_lut.loc[index, "matchType"] = resp["match_type"]
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
        new = worms_lut.loc[worms_lut["scientificName"] == name]
   
        new_dict = {
            "matchType": new["matchType"].values[0],
            "acceptedname": new["acceptedname"].values[0],
            "acceptedID": new["acceptedID"].values[0],
            "scientificNameID": new["scientificNameID"].values[0],
            "kingdom": new["kingdom"].values[0],
            "phylum": new["phylum"].values[0],
            "class": new["class"].values[0],
            "order": new["order"].values[0],
            "family": new["family"].values[0],
            "genus": new["genus"].values[0],
            "scientificNameAuthorship": new["scientificNameAuthorship"].values[0],
            "taxonRank": new["taxonRank"].values[0],
        }

        preview[name] = {"before": name, "after": new_dict}

    return preview
