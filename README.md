# Earth Observation Data in a Journalistic Context

This repository contains a series of notebooks describing interaction with the Copernicus Open Acces Hub in order to obtain and manipulate earth observation data. A (free) Scihub account is needed in order to execute them, the registration form can be found at https://scihub.copernicus.eu/dhus/. 

The Docker image can be built using the following command:

``` bash
docker build . -t eratosthenes:latest
```

The resulting notebook is based on the [jupyter/scipy-notebook](https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook). Follow the link for more information on installed packages or other configuration details.

You need to define your Scihub user credentials as environment variables in order to be able to execute the notebooks:

``` bash
docker run -it -e SCIHUB_USERNAME='<username>' -e SCIHUB_PASSWORD='<password>' eratosthenes:latest
```
