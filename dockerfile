
FROM jupyter/scipy-notebook:latest

RUN pip install --no-cache-dir vdom==0.5
