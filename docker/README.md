# Docker image for Python oceanographic containers

## build image from Docker file

''''
docker build -t jgrelet/oceano2python:3.6 -f Dockerfile .
''''

## pull pull the existing images from Docker hub

''''
docker pull jgrelet/oceano2python:3.6
''''

## run the container

''''
docker run -it --rm -v /D_DRIVE:/data -e CRUISE="$CRUISE" -e DRIVE=/data python jgrelet/oceano2python:3.6 /bin/bash
''''
