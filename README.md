# Remote Sensing for Journalism

This repository contains a series of notebooks describing interaction with the Copernicus Open Acces Hub in order to obtain and manipulate earth observation data.
The aim is to document common tasks that might make the data from the Copernicus Sentinel missions attractive for usage in data journalism reporting.

The publication and research uses [Jupyter notebooks](https://jupyter.org) and is published using [jupyter-books](https://jupyter-book.org), an open-source python project that allows generating HTML pages from a collection of Jupyter notebooks.

## Copernicus Open Access Hub

Copernicus Open Access Hub is the platform which is openly distributing the Terrabytes of Sentinel-2 data which these notebooks rely on.
A (free) Scihub account is needed in order to follow this documentation interactively.
The registration form can be found at https://scihub.copernicus.eu/dhus/. 

## Obtaining and Running the Code

The source code lives at https://github.com/heyarne/remote-sensing-for-journalism.

A `Dockerfile` is present at the root of the repository to help with reproducing the computing environment.
The image can be built by running the following command from the project root:

``` bash
docker build . -t eratosthenes:latest
```

When running the docker image you need to define your Scihub user credentials as environment variables:

``` bash
docker run -it \
  --name eratosthenes \
  --net host \
  --volume "$(pwd)":/home/jovyan \
  -e SCIHUB_USERNAME='<username>' \
  -e SCIHUB_PASSWORD='<password>' \
  eratosthenes:latest
```

This starts up a `JupyterLab` environment which allows you to interactively execute all notebooks and modify them to suit your needs.

The Docker image is based on the [jupyter/scipy-notebook](https://github.com/jupyter/docker-stacks/tree/master/scipy-notebook).
Follow the link for more information on installed packages or other configuration details.

## Hardware Requirements

Note that working with this kind of data is resource intensive.
These notebooks download or create roughly 50GB of data, most of which is occupied by compressed GeoTIFF files.
They have been executed and tested on a virtual server with 4 CPU cores at 2.6 GHz each and 32 GB of RAM.

## Building the Jupyter Book

The `jupyter-book` dependency is included in the `Dockerfile`.
You can build a book from a running container by executing the following command on the Docker host:

```
docker run -it eratosthenes jupyter-book build .
```

The resulting book can be found in the directory `_build/html/`.
