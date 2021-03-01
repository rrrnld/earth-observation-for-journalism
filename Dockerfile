# Please substitute the values below with your user credentials; the signup
# form can be found at https://scihub.copernicus.eu/dhus.
# Alternatively you can provide the values when running the docker container.
FROM jupyter/scipy-notebook:42f4c82a07ff

ENV SCIHUB_USERNAME=""
ENV SCIHUB_PASSWORD=""
ENV JUPYTER_ENABLE_LAB=yes

# See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html#using-pip-install-or-conda-install-in-a-child-docker-image for more info
RUN conda install -c conda-forge geopandas==0.8.1 && \
  pip install \
    descartes==1.1.0 sentinelsat==0.14 rasterio==1.2.0 folium==0.11.0 \
    jupyterlab-spellchecker \
    jupyter-book 0.10.0 && \ 	
  fix-permissions $CONDA_DIR && \
  fix-permissions /home/$NB_USER
