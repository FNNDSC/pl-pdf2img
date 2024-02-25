# PDF to Image

[![Version](https://img.shields.io/docker/v/fnndsc/pl-pdf2img?sort=semver)](https://hub.docker.com/r/fnndsc/pl-pdf2img)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-pdf2img)](https://github.com/FNNDSC/pl-pdf2img/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-pdf2img/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-pdf2img/actions/workflows/ci.yml)

`pl-pdf2img` is a [_ChRIS_](https://chrisproject.org/) _ds_ plugin which takes in pdfs as input files and creates jpgs or pngs as output files.

## Abstract

Radiological databases, or PACS (Picture Archive and Communication Systems), can typically only store image files in DICOM format. Occasionally text data, often in the form of a report, needs to be added to a Study/Series in a PACS. The canonical way to effect this, is to create a PDF version of the report, convert that to an image, DICOMize this image, and push to a PACS. This ChRIS DS plugin can be used for part of that workflow.

## Installation

`pl-pdf2img` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can run from either within _ChRIS_ or the command-line.

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/) (a.k.a. Singularity) to run `pl-pdf2img` as a container:

```shell
apptainer exec docker://fnndsc/pl-pdf2img pdf2img [--args values...] input/ output/
```

To print its available options, run:

```shell
apptainer exec docker://fnndsc/pl-pdf2img pdf2img --help
```

## Examples

`pdf2img` requires two positional arguments: a directory containing input data, and a directory where to create output data. First, create the input directory and move input data into it.

```shell
mkdir incoming/ outgoing/
mv some.dat other.dat incoming/
apptainer exec docker://fnndsc/pl-pdf2img:latest pdf2img [--args] incoming/ outgoing/
```

## Development

Instructions for developers.

### Building

Build a local container image:

```shell
docker build -t localhost/fnndsc/pl-pdf2img .
```

### Running

Mount the source code `pdf2img.py` into a container to try out changes without rebuild.

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/pdf2img.py:/usr/local/lib/python3.11/site-packages/pdf2img.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-pdf2img pdf2img /incoming /outgoing
```

### Testing

Run unit tests using `pytest`.
It's recommended to rebuild the image to ensure that sources are up-to-date.
Use the option `--build-arg extras_require=dev` to install extra dependencies for testing.

```shell
docker build -t localhost/fnndsc/pl-pdf2img:dev --build-arg extras_require=dev .
docker run --rm -it localhost/fnndsc/pl-pdf2img:dev pytest
```

## Release

Steps for release can be automated by [Github Actions](.github/workflows/ci.yml).
This section is about how to do those steps manually.

### Increase Version Number

Increase the version number in `setup.py` and commit this file.

### Push Container Image

Build and push an image tagged by the version. For example, for version `1.2.3`:

```
docker build -t docker.io/fnndsc/pl-pdf2img:1.2.3 .
docker push docker.io/fnndsc/pl-pdf2img:1.2.3
```

### Get JSON Representation

Run [`chris_plugin_info`](https://github.com/FNNDSC/chris_plugin#usage)
to produce a JSON description of this plugin, which can be uploaded to _ChRIS_.

```shell
docker run --rm docker.io/fnndsc/pl-pdf2img:1.2.3 chris_plugin_info -d docker.io/fnndsc/pl-pdf2img:1.2.3 > chris_plugin_info.json
```

Intructions on how to upload the plugin to _ChRIS_ can be found here: https://chrisproject.org/docs/tutorials/upload_plugin

