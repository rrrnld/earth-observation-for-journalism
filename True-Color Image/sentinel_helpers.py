import zipfile
import glob
from Pathlib import Path

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
        rasters = glob.glob(Path(p) / '**/*.jp2'
        
    rasters = [r for r in rasters for b in bands if b in r]
    if resolution:
        rasters = [r for r in rasters if resolution in r]

    rasters = ['zip+file://' + p + '!/' + r for r in rasters]
    return rasters

 
def rgb_paths(zip_file, resolution='10m'):
    return band_paths(zip_file, ['B02', 'B03', 'B04'], resolution)