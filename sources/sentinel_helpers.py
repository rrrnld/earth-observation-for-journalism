from dateutil.parser import parse as parse_datetime
import urllib.parse
from pathlib import Path

import fiona
import folium
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np
import rasterio as r
from rasterio.features import geometry_mask, geometry_window
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import Window

from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union

from tempfile import TemporaryDirectory
from zipfile import ZipFile

import warnings

def search_osm(place):
    '''
    Returns a GeoDataFrame with results from OpenStreetMap Nominatim for the given search string.
    '''
    urlescaped_place = urllib.parse.quote(place)
    search_url = ('https://nominatim.openstreetmap.org/search/?q={}' +
                  '&format=geojson&polygon_geojson=1').format(urlescaped_place)
    return gpd.read_file(search_url)

            
def plot_downloaded_products(products, area_of_interest, **kwargs):
    ax = kwargs.get('ax')
    alpha = kwargs.pop('alpha', 0.1)
    if not ax:
        fig, ax = plt.subplots(**kwargs)
        
    grey = '#777777'
    purple = '#988ED5'
    
    # allow plotting raw shapely geometries
    if 'plot' not in dir(products):
        products = gpd.GeoSeries(products)
    if 'plot' not in dir(area_of_interest):
        area_of_interest = gpd.GeoSeries(area_of_interest)
    
    # area of interest in background
    a = area_of_interest.plot(ax=ax, facecolor=grey)
    # product fill layer
    b = products.plot(ax=ax, facecolor=purple, alpha=alpha)
    # product stroke layer
    products.plot(ax=ax, facecolor='none', edgecolor=purple, alpha=0.4)
    
    if not kwargs.get('ax'):
        ax.set(title='Area of Interest and Available Products')
    
    return ax

def scihub_band_paths(p, bands, resolution=None):
    '''
    Given a zip file or folder at `p`, returns the paths inside p to the raster files containing
    information for the given bands. Because some bands are available in more than one
    resolution, this can be filtered by prodiding a third parameter (e.g. resolution='10m').
    
    - `p` can be a string or a pathlib.Path.
    - `bands` can be a list of bands or a single band.
   
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
            rasters = [Path(f'zip+file://{p.absolute()}!/{f}') for f in files if f.endswith('.jp2')]
    else:
        rasters = p.glob('**/*.jp2')
    
    # take only the paths that contain one of the given bands
    rasters = [raster for band in bands for raster in rasters if band in raster.name]
    
    # if a resolution is given, further discard the bands we don't need
    if resolution:
        rasters = [raster for raster in rasters if resolution in raster.name]
    
    return rasters


def scihub_bgr_paths(product_path, resolution=None):
    '''
    A convenence function to return the paths to the blue, green and red bands
    in the downloaded product at `product_path`.
    '''
    return scihub_band_paths(product_path, ['B02', 'B03', 'B04'], resolution)


def scihub_cloud_mask(product_path, area=None, cloud_probability=0.75, resolution='10m'):
    '''
    Returns a numpy array with boolean values representing a product's cloud
    mask. Cloudy pixels are True, non-cloudy pixels are False.
    '''
    # TODO: Subset for area
    # there is no mask in 10m resolution an we need to manually upsample it;
    # upsampling code is taken from the rasterio documentation:
    # https://rasterio.readthedocs.io/en/latest/topics/resampling.html
    if resolution in ['20m', '60m']:
        mask_resolution = resolution
        upscale_factor = 1
    else:
        mask_resolution = '20m'
        upscale_factor = 2
    
    mask_path = scihub_band_paths(product_path, ['MSK_CLDPRB'], mask_resolution)[0]
    with r.open(mask_path) as mask:
        if isinstance(area, gpd.GeoDataFrame):
            window = geometry_window(mask, area.to_crs(mask.crs)['geometry'])
        else:
            window = Window(0, 0, mask.width, mask.height)
            
        mask_data = mask.read(
            out_shape=(
                mask.count,
                int(window.height * upscale_factor),
                int(window.width * upscale_factor)
            ),
            window=window,
            resampling=Resampling.bilinear
        )
        mask_transform = mask.transform * mask.transform.scale(
            (mask.width / mask_data.shape[-1]),
            (mask.height / mask_data.shape[-2])
        )
        
        # mask_data values range from 0 to 100, cloud_probability from 0 to 1
        return mask_data >= (cloud_probability * 100), mask_transform
    

def scihub_band_date(band):
    '''
    Given a string, `pathlib.Path` or `rasterio.DataSetReader`, returns the
    datetime encoded in the filename.
    '''
    if type(band) is r.DatasetReader:
        file_name = band.name
    else:
        file_name = Path(band).name
    return parse_datetime(file_name.split('_')[-3])

        
# See https://book.pythontips.com/en/latest/context_managers.html#implementing-a-context-manager-as-a-class

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
            # wrapped in a block so we still close other fails if one fails
            # to close
            try:
                f.close()
            except:
                pass


def geodataframe_on_map(geodataframe):
    '''
    Plot a GeoDataframe or GeoSeries on a Leaflet map; map automatically
    centers
    '''
    bbox = geodataframe.unary_union.bounds
    minx, miny, maxx, maxy = bbox
    m = folium.Map([0, 0], tiles='cartodbpositron', scroll_wheel_zoom=False)
    folium.GeoJson(geodataframe.to_json()).add_to(m)
    m.fit_bounds([[miny, minx], [maxy, maxx]])
    return m

