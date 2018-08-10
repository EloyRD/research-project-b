
FROM jupyter/scipy-notebook:latest177037d09156
RUN pip install --no-cache-dir notebook==5.*
RUN pip install --no-cache-dir vdom==0.5
