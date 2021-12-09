import pandas as pd
import pyworms  # pip install git+git://github.com/iobis/pyworms.git
import numpy as np
import uuid
import csv


# read in raw data file

file = 'data/MadeUpDataForBiologicalDataTraining.csv'
df = pd.read_csv(file, header=[0])


# create the eventID and occurrenceID in the original file so that
# information can be reused for all necessary files down the line

df['eventID'] = df[['region', 'station', 'transect']].apply(
    lambda x: '_'.join(x.astype(str)), axis=1)
df['occurrenceID'] = uuid.uuid4()


# We will need to create three separate files to comply with the sampling
# event format. We'll start with the event file but we only need to
# include the columns that are relevant to the event file.

# EVENT FILE

def create_darwin_event_file(df):

    event = df[['date', 'lat', 'lon', 'region', 'station',
                'transect', 'depth', 'bottom type', 'eventID']].copy()

    # rename any columns of data that match directly to Darwin Core. We know
    # this based on our crosswalk spreadsheet CrosswalkToDarwinCore.csv

    event['decimalLatitude'] = event['lat']
    event['decimalLongitude'] = event['lon']
    event['minimumDepthInMeters'] = event['depth']
    event['maximumDepthInMeters'] = event['depth']
    event['habitat'] = event['bottom type']
    event['island'] = event['region']

    # convert date to ISO format

    event['eventDate'] = pd.to_datetime(
        event['date'],
        format='%m/%d/%Y',
        utc=True)

    # add any missing required fields

    event['basisOfRecord'] = 'HumanObservation'
    event['geodeticDatum'] = 'EPSG:4326 WGS84'

    # remove any columns that we no longer need

    event.drop_duplicates(
        subset='eventID',
        inplace=True)

# write out the event file


event.to_csv(
    'MadeUpData_event_frompy.csv',
    header=True,
    index=False,
    date_format='%Y-%m-%d')


# Occurrence File

def create_darwin_occurrence_file(df):

    # create dataframe
    occurrence = df[['scientific name', 'eventID',
                     'occurrenceID', 'percent cover']].copy()

    # rename the columns that align directly with Darwin Core
    occurrence['scientificName'] = occurrence['scientific name']

    # add required information that's missing
    occurrence['occurrenceStatus'] = np.where(
        occurrence['percent cover'] == 0, 'absent', 'present')

    # create a lookup table of unique scientific names
    lut_worms = pd.DataFrame(
        columns=['scientificName'],
        data=occurrence['scientificName'].unique())

    # Add the columns that we can grab information from WoRMS including the
    # required scientificNameID
    headers = [
        'acceptedname',
        'acceptedID',
        'scientificNameID',
        'kingdom',
        'phylum',
        'class',
        'order',
        'family',
        'genus',
        'scientificNameAuthorship',
        'taxonRank']

    for head in headers:
        lut_worms[head] = ''
