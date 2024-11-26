import pandas as pd
import pyworms
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)

def gen_worms_lookup(occurrence: pd.DataFrame, target_column: str):
    # Create empty dataframe with unique scientific names
    logger.info("Generating taxon lookup table.")

    worms_lut = pd.DataFrame(
        columns=["scientificName"], data=occurrence[target_column].unique()
    )

    # Add empty columns for each header
    # Columns correspond to values fetched from WoRMS
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
        logger.debug(f"Searching for scientific name: {row["scientificName"]}")

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

    logger.info("Lookup table generated.")


    return worms_lut


def preview_changes(input_df: pd.DataFrame, worms_lut: pd.DataFrame, target_column: str):
    # create a dictionary to store before/after values
    preview = {}

    for name in input_df[target_column].unique():
        logger.debug(f"Matching name: {name}")

        # Matches current name to scientific name in lookup table
        lookup_match = worms_lut.loc[worms_lut["scientificName"] == name]
   
        match_preview = {
            "matchType": lookup_match["matchType"].values[0],
            "acceptedname": lookup_match["acceptedname"].values[0],
            "acceptedID": lookup_match["acceptedID"].values[0],
            "scientificNameID": lookup_match["scientificNameID"].values[0],
            "kingdom": lookup_match["kingdom"].values[0],
            "phylum": lookup_match["phylum"].values[0],
            "class": lookup_match["class"].values[0],
            "order": lookup_match["order"].values[0],
            "family": lookup_match["family"].values[0],
            "genus": lookup_match["genus"].values[0],
            "scientificNameAuthorship": lookup_match["scientificNameAuthorship"].values[0],
            "taxonRank": lookup_match["taxonRank"].values[0],
        }

        logger.debug(f"Match for {name} found, adding to preview.")

        preview[name] = {"before": name, "after": match_preview}

    return preview


def merge_matched_taxa(input_df: pd.DataFrame, taxa_info: pd.DataFrame, target_values: list[str] = None, target_column: str = "scientificName"):
    
    # drop records from taxa table where target column value is not in target_values
    if target_values:
        logger.debug(f"Filtering taxa info, keeping values: {target_values}")
        taxa_info = taxa_info[taxa_info["scientificName"].isin(target_values)]

    try:
        logger.info("Merging taxa info into source data...")

        if target_column != "scientificName":
            logger.warning(f"Input columns do not match lookup table. Renaming {target_column} to scientificName in source data.")
            input_df = input_df.rename({target_column: "scientificName"}, axis="columns")

        merged_data = pd.merge(input_df, taxa_info, how='left', on="scientificName")
    except Exception as e:
        logger.error(
            "Merge FAILED. Something has gone horribly awry!"
            f" Check log for debug information. Error: {e.with_traceback}",
        )

    return merged_data