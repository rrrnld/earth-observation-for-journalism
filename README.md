# Using Earth Observation for Journalism

This repository contains a series of notebooks describing interaction with the Copernicus Open Access Hub in order to obtain, manipulate and analyze earth observation data.
The aim is to document common tasks that might make the data from the Copernicus Sentinel-2 mission attractive for usage in data journalism.

The publication and research uses [Jupyter notebooks](https://jupyter.org) and is published using [jupyter-books](https://jupyter-book.org), an open-source python project that allows generating HTML pages from a collection of Jupyter notebooks.

## Copernicus Open Access Hub

Copernicus Open Access Hub is the platform which is openly distributing the Terrabytes of Sentinel-2 data which these notebooks rely on.
A (free) Scihub account is needed in order to follow this documentation interactively.
The registration form can be found at https://scihub.copernicus.eu/dhus/. 

## Target Audience

These notebooks assume Python knowledge as well as familiarity with common Python data processing tools like the `pandas` library.
The topic is approached primarily from a computer science perspective, i.e. not an aeronautical, not a geophyisical, or any other one.
As a consequence the focus will be how different tasks can be implemented.
Many considerations behind a particular action or processing step can only be briefly touched.

## Obtaining and Running the Code

The notebooks are published for reading at https://arne.schlueter.is/working-on/remote-sensing-for-journalism.
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
They have been executed and tested on a virtual server with 4 CPU cores with a clock speed of 2.6 GHz each and 32 GB of RAM.

There are notebooks cells with `%%time` or `%%timeit` magic commands.
Their ouput contains information about the execution time on the system described above.

## Building the Jupyter Book

The `jupyter-book` dependency is included in the `Dockerfile`.
You can build a book from a running container by executing the following command when the container above is running:

```
docker exec eratosthenes jupyter-book build .
```

Alternatively you can start a container just to build the book

```
docker run -v "$(pwd)":/home/jovyan eratosthenes:latest jupyter-book build .
```

The resulting book can be found in the directory `_build/html/`.
