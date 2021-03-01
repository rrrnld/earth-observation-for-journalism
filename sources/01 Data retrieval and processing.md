# Data Retrieval and Processing

The first chapter contains notebooks that document the data retrieval process from the Copernicus Open Access Hub.

It explains how to use [`sentinelsat`](https://github.com/sentinelsat/sentinelsat) library to interact with the API: How to specify what kind of data we are interested in with the aide of open map data from [OpenStreetMap](https://www.openstreetmap.org/) and [`geopandas`](https://geopandas.org/) and how to download it. It then goes on to show how to use [`rasterio`](https://rasterio.readthedocs.io/) and [`matplotlib`](https://matplotlib.org/stable/index.html) to work with the data.

The Sentinel-2 satellite captures light in visible and invisible parts of the spectrum. This can be used to derive different kinds of useful information about ground-level phenomena. This chapter will detail how to use it to create true-color images for different moments in time.
