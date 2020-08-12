# See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html#using-pip-install-or-conda-install-in-a-child-docker-image for more info

FROM jupyter/scipy-notebook
ENV JUPYTER_LAB_ENABLE=1

# RUN pip install geopandas sentinelsat==0.14 descartes && \
# 	fix-permissions $CONDA_DIR && \
# 	fix-permissions /home/$NB_USER
