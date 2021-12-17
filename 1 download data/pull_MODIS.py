import ee
import time
import sys
import numpy as np
import pandas as pd
import itertools
import os
import urllib

# ee.Authenticate()
ee.Initialize()


def export_oneimage(img, folder, name, region, scale, crs):
    print(f'Exporting to {folder}/{name}')
    task = ee.batch.Export.image(img, name, {
        'driveFolder': folder,
        'driveFileNamePrefix': name,
        'region': region,
        'scale': scale,
        'crs': crs
    })
    task.start()
    while task.status()['state'] == 'RUNNING':
        print('Running...')
        # Perhaps task.cancel() at some point.
        time.sleep(10)
    print('Done.', task.status())


locations = pd.read_csv('2 clean data/locations_final.csv', header=None)


# Transforms an Image Collection with 1 band per Image into a single Image with items as bands
# Author: Jamie Vleeshouwer

def appendBand(current, previous):
    # Rename the band
    previous = ee.Image(previous)
    current = current.select([0, 1, 2, 3, 4, 5, 6])
    # Append it to the result (Note: only return current item on first element/iteration)
    accum = ee.Algorithms.If(ee.Algorithms.IsEqual(previous, None), current, previous.addBands(ee.Image(current)))
    # Return the accumulation
    return accum


# Before 'MODIS/MOD09A1'
imgcoll = ee.ImageCollection('MODIS/006/MOD09A1') \
            .filter(ee.Filter.date('2020-08-01', '2020-09-01')) \
            .filterBounds(ee.Geometry.Rectangle(-106.5, 50, -64, 23))
            # .filter(ee.Filter.calendarRange(2020, 2020, 'year')) \
            # .filter(ee.Filter.calendarRange(8, 8, 'month')) \

img = imgcoll.iterate(appendBand)
img = ee.Image(img)

print(locations)

for loc1, loc2, lat, lon in locations.values:
    fname = '{}_{}'.format(int(loc1), int(loc2))

    offset = 0.11
    scale = 500
    crs = 'EPSG:4326'

    region = str([
        [lat - offset, lon + offset],
        [lat + offset, lon + offset],
        [lat + offset, lon - offset],
        [lat - offset, lon - offset]])

    # while True:
    #     try:
    #         export_oneimage(img, 'Data', fname, region, scale, crs)
    #     except:
    #         print('retry')
    #         time.sleep(10)
    #         continue
    #     break
