import glob
import urllib.parse
from pathlib import Path
import zipfile

import geopandas as gp
import rasterio as r

from rasterio.warp import calculate_default_transform, reproject, Resampling

def band_paths(p, bands, resolution=None):
    '''
    Given a zip file or folder at `p`, returns the paths inside p to the raster files containing
    information for the given bands. Because some bands are available in more than one
    resolution, this can be filtered by prodiding a third parameter (e.g. resolution='10m').
   
    The returned paths are formatted in the zip scheme as per Apache Commons VFS if necessary
    and can be directly opened by rasterio.
    '''
    if p.endswith('.zip'):
        with zipfile.ZipFile(p) as f:
            files = f.namelist()
            rasters = [f for f in files if f.endswith('.jp2')]
    else:
        rasters = glob.glob(Path(p) / '**/*.jp2')
    rasters = [r for r in rasters for b in bands if b in r]
    if resolution:
        rasters = [r for r in rasters if resolution in r]

    rasters = ['zip+file://' + p + '!/' + r for r in rasters]
    return rasters

 
def rgb_paths(zip_file, resolution='10m'):
    return band_paths(zip_file, ['B02', 'B03', 'B04'], resolution)


def search_osm(place):
    '''
    Returns a GeoDataFrame with results from OpenStreetMap Nominatim for the given search string.
    This allows us to fetch detailed geometries for virtually any place on earth.
    '''
    urlescaped_place = urllib.parse.quote(place)
    search_url = 'https://nominatim.openstreetmap.org/search/?q={}&format=geojson&polygon_geojson=1'.format(urlescaped_place)
    return gp.read_file(search_url)


def reproject_raster_image(src, dst, target_crs):
    '''
    Reprojects `src` into `dst`, given a coordinate reference system `target_crs`.
    '''
    transform, width, height = calculate_default_transform(
        src.crs, target_crs, src.width, src.height, *src.bounds)
        
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': target_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    for i in range(1, src.count + 1):
        reproject(
            source=r.band(src, i),
            destination=r.band(dst, i),
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=target_crs,
            resampling=Resampling.nearest)