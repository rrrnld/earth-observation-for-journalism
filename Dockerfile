# See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html#using-pip-install-or-conda-install-in-a-child-docker-image for more info

FROM jupyter/scipy-notebook
ENV JUPYTER_ENABLE_LAB=yes

RUN pip install geopandas==0.8.1 descartes==1.1.0 sentinelsat==0.14 rasterio==1.1.5 folium==0.11.0 && \
	fix-permissions $CONDA_DIR && \
	fix-permissions /home/$NB_USER
