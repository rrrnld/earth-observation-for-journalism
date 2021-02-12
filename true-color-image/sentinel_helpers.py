import urllib.parse
from pathlib import Path
import zipfile

import fiona
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np
import rasterio as r
from rasterio.warp import calculate_default_transform, reproject, Resampling

def search_osm(place):
    '''
    Returns a GeoDataFrame with results from OpenStreetMap Nominatim for the given search string.
    This allows us to fetch detailed geometries for virtually any place on earth.
    '''
    urlescaped_place = urllib.parse.quote(place)
    search_url = ('https://nominatim.openstreetmap.org/search/?q={}' +
                  '&format=geojson&polygon_geojson=1').format(urlescaped_place)
    return gpd.read_file(search_url)


def nth(xs, n, default=None):
    '''
    Wraps list access to return `default` instead of returning an `ItemError`
    when accessing out-of-bounds elements. `default` is `None` when not
    explicitly given.
    '''
    try:
        return xs[n]
    except IndexError:
        return default

    
def plot_all(items, extra_kwargs=[]):
    '''
    Returns a plot containing all of the geometries in `items`.
    If an `item` does not contain a `plot` method, a GeoSeries will be
    constructed from it.
    
    The parameter `extra_kwargs` can contain extra keyword arguments that are
    passed to matplotlib for the given item.
    '''
    ax = None
    for idx, item in enumerate(items):
        if 'plot' not in dir(item):
            item = gpd.GeoSeries(item)
        
        kwargs = nth(extra_kwargs, idx, {})
        if not ax:
            ax = item.plot(**kwargs)
        else:
            item.plot(ax=ax, **kwargs)
    
    
def scihub_product_ids(geodataframe):
    '''
    Returns the product ids of items in a GeoDataFrame returned by
    `sentinelsat.to_geodataframe` as expected by `sentinelsat.download` and
    `sentinelsat.download_all`.
    '''
    return [link.split('Products(\'')[-1].split('\')/$value')[0] for link in geodataframe['link'].values]


def scihub_band_paths(p, bands, resolution=None):
    '''
    Given a zip file or folder at `p`, returns the paths inside p to the raster files containing
    information for the given bands. Because some bands are available in more than one
    resolution, this can be filtered by prodiding a third parameter (e.g. resolution='10m').
    
    `p` can be a string or a pathlib.Path.
    `bands` can be a list of bands or a single band.
   
    The returned paths are formatted in the zip scheme as per Apache Commons VFS if necessary
    and can be directly opened by rasterio.
    '''
    if type(bands) != list:
        # allow passing in a single band more easily
        bands = [bands]
    
    p = Path(p) # make sure we're dealing with a pathlib.Path
    if p.suffix == '.zip':
        # when dealing with zip files we have to read the filenames from the
        # archive first
        with zipfile.ZipFile(p) as f:
            files = f.namelist()
            rasters = [f for f in files if f.endswith('.jp2')]
    else:
        rasters = p.glob('**/*.jp2')
    
    # take only the paths that contain one of the given bands
    rasters = [raster for band in bands for raster in rasters if band in raster]
    
    # if a resolution is given, further discard the bands we don't need
    if resolution:
        rasters = [raster for raster in rasters if resolution in raster]

    if p.suffix == '.zip':
        # we have to reformat the paths to 
        rasters = [f'zip+file://{p}!/{r}' for r in rasters]
    
    return rasters


def scihub_bgr_paths(raster_path, resolution=None):
    '''
    A convenence function to return the paths to the blue, green and red bands
    in the downloaded product at `raster_path`.
    '''
    return scihub_band_paths(raster_path, ['B02', 'B03', 'B04'], resolution)


def scihub_normalize_range(v):
    return np.clip(v, 0, 2000) / 2000

 

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