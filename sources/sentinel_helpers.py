from dateutil.parser import parse as parse_datetime
import urllib.parse
from pathlib import Path

import fiona
import folium
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np
import rasterio as r
from rasterio.features import geometry_mask
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


def scihub_cloud_mask(product_path, **kwargs):
    '''
    Given a `product_path` pointing to a product downlaoded from the Copernicus
    Open Access Hub, returns a shapely geometry representing the included cloud
    mask.
    
    If an additional parameter, `rasterize=True` is given, the returned cloud
    mask will be a rasterized numpy ndarray instead of a vector geometry. Two
    additional parameters, `target_path` and `target_transform` are needed to
    determine the size of this array. In this array, pixels with clouds are
    `False` and pixels without clouds are `True`.
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
                    mask = unary_union([shape(f['geometry']) for f in features])
        except ValueError:
            # empty cloud mask
            mask = Polygon([])

    if kwargs.get('rasterize'):
        # return raster version of the vector geometry we found above
        target_shape = kwargs.get('target_shape')
        target_transform = kwargs.get('target_transform')
        if not target_transform or not target_shape:
            error_msg = 'target_transform and target_shape need to be set ' + \
                'to construct a rasterized cloud mask.'
            raise ValueError(error_msg)
        
        # completely empty cloud masks have to be handled separately
        if mask.is_empty:
            return np.full(target_shape, True)
        
        return geometry_mask(mask,
                             out_shape=target_shape,
                             transform=target_transform)
    else:
        return mask
    

def scihub_normalize_range(v):
    '''
    Raster files downloaded from the Copernicus Open Access Hub can contain
    pixels with reflectance values outside of the allowed range. This function
    discards those values and normalizes the range of the returned raster file
    to be [0...1].
    '''
    return np.clip(v, 0, 2000) / 2000


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

