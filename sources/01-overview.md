# Overview

The first chapter contains notebooks that document the data retrieval process from the Copernicus Open Access Hub.

It explains how to use the [`sentinelsat`](https://github.com/sentinelsat/sentinelsat) library to interact with the HTTP API: How to specify what kind of data we are interested in with the aide of open map data from [OpenStreetMap](https://www.openstreetmap.org/) and [`geopandas`](https://geopandas.org/) and how to download it. It then goes on to show how to use [`rasterio`](https://rasterio.readthedocs.io/) and [`numpy`](https://numpy.org/) to read and process the downloaded data and [`matplotlib`](https://matplotlib.org/stable/index.html) to visualize it.

The Sentinel-2 mission is a part of the [Copernicus earth observation missions of the ESA](http://www.esa.int/Applications/Observing_the_Earth/Copernicus), which provide open satellite data to anyone. Sentinel-2 is a group of satellites that capture electromagnetic radiation. A part of this is visible light, so it can be used to create detailed satellite maps, but a large part of this is invisible. It can be used to infer information on all kinds of ground-level phenomena where other data sources are scarce

This chapter will detail how to retrieve, interpret and manipulate this data, and ends with a notebook that can create a true color image using recent satellite data for any area.
