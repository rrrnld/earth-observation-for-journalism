import urllib.parse
from pathlib import Path

import fiona
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np
import rasterio as r
from rasterio.warp import calculate_default_transform, reproject, Resampling

from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union

from tempfile import TemporaryDirectory
from zipfile import ZipFile

import warnings

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
        with ZipFile(p) as f:
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


def scihub_bgr_paths(product_path, resolution=None):
    '''
    A convenence function to return the paths to the blue, green and red bands
    in the downloaded product at `product_path`.
    '''
    return scihub_band_paths(product_path, ['B02', 'B03', 'B04'], resolution)


def scihub_cloud_mask(product_path):
    '''
    Given a `product_path` pointing to a product downlaoded from the Copernicus
    Open Access Hub, returns a shapely geometry representing the included cloud
    mask.
    '''
    with TemporaryDirectory() as tmp_dir:
        # we need the temporary directory to work around a problem with reading
        # vector files from zip archives
        
        p = Path(product_path)
        if p.suffix == '.zip':
            # when dealing with zip files we have to read the filenames from the
            # archive first
            with ZipFile(p) as f:
                files = f.namelist()
                file = [f for f in files if f.endswith('MSK_CLOUDS_B00.gml')][0]
                f.extract(file, tmp_dir)
                file = Path(tmp_dir) / file
        else:
            file = list(p.glob('**/MSK_CLOUDS_B00.gml'))[0]

        try:
            with fiona.open(file) as features:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # this returns a warning because the iterator has to be
                    # rewound; while this is a performance issue, we can ignore it
                    return unary_union([shape(f['geometry']) for f in features])
        except ValueError:
            # empty cloud mask
            return Polygon([])
    

def scihub_normalize_range(v):
    '''
    Raster files downloaded from the Copernicus Open Access Hub can contain
    pixels with reflectance values outside of the allowed range. This function
    discards those values and normalizes the range of the returned raster file
    to be [0...1].
    '''
    return np.clip(v, 0, 2000) / 2000


def reproject_raster_image(src, dst, target_crs):
    '''
    FIXME: UNUSED!?
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

        
        
# TODO: This is documented somewhere in the python docs, we should link to it here

class RasterReaderList():
    '''
    This class allows opening a list of file paths in a `with` block using
    rasterio.open. They get automatically closed when the context created by
    the `with` block is left.
    '''
    
    def __init__(self, paths):
        self.open_files = []
        self.paths = paths
    
    def __enter__(self):
        for f in self.paths:
            self.open_files.append(r.open(f))
        
        return self.open_files
    
    def __exit__(self, _type, _value, _traceback):
        for f in self.open_files:
            f.close()