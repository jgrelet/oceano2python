FROM alpine:3.6
LABEL maintainer="Jacques.Grelet_at_ird.fr"

ENV PACKAGES="\
    dumb-init \
    musl \
    libc6-compat \
    linux-headers \
    build-base \
    bash \
    make \
    git \
    cmake \
    libxml2 \
    libxml2-dev \
#    hdf5 \
#    hdf5-dev \
    netcdf-bin \
    libnetcdf-dev \ 
    ca-certificates \
    libgcc \
    libstdc++ \
    tcl \
    tk \
    libssl1.0 \
    net-tools \
    iputils-ping \
    "

ENV PYTHON_PACKAGES="\
    numpy \
    matplotlib \
    scipy \
    https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz \
    toml \ 
    pynmea2 \
    pySerial \ 
    netCDF4 \    
    seawater \
    PyInstaller \ 
    PySimpleGUI \
    PySimpleGUIQt \
    ConfigParser \
    PySide2 \
    PyAstronomy \
    "
 
RUN apk add --no-cache --virtual build-dependencies python3 \
    && apk add --virtual build-runtime \
    build-base python3-dev freetype-dev pkgconfig \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip \
    && rm -r /root/.cache \
    && apk --no-cache add \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
        hdf5 \
    && apk --no-cache add --virtual .builddeps.edge \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
    hdf5-dev \
    && pip install --no-cache-dir $PYTHON_PACKAGES \
    && apk del build-runtime \
    && apk add --no-cache --virtual build-dependencies $PACKAGES \
    && rm -rf /var/cache/apk/* 

VOLUME /data
RUN groupadd -r scientifiques && useradd -r -g scientifiques -p antea science 
USER science
WORKDIR /home/science
#COPY .bashrc /root
COPY .bashrc /home/science
