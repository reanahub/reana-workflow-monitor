# This file is part of REANA.
# Copyright (C) 2017, 2018, 2020 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

FROM fedora:25
# hadolint ignore=DL3040, DL3041
RUN dnf -y update &&\
    dnf install -y gcc gcc-c++ graphviz-devel ImageMagick python-devel libffi-devel openssl openssl-devel unzip nano autoconf automake libtool python-pip &&\
    dnf install -y dnf redhat-rpm-config
COPY . /code
WORKDIR /code
# hadolint ignore=DL3013
RUN pip install --upgrade pip &&\
    pip install -e '.[all]'
