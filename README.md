# pydra-ants

[![PyPI - Version][pypi-version]][pypi-project]
[![PyPI - Python Version][pypi-pyversions]][pypi-project]
[![PyPI - Downloads][pypi-downloads]][pypi-project]
![][status-test]

-----

Pydra tasks for ANTs

[Pydra][pydra] is a dataflow engine which provides
a set of lightweight abstractions for DAG
construction, manipulation, and distributed execution.

[ANTs][ants] is a toolbox for multi-variate image registration,
segmentation and statistical analysis.

**Table of Contents**

- [Available Tasks](#available-tasks)
- [Installation](#installation)
- [Development](#development)
- [License](#license)

## Available Tasks

- ApplyTransforms
- N4BiasFieldCorrection
- RegistrationSyNQuick

## Installation

```console
pip install pydra-ants
```

A separate installation of ANTs is required to use this package.

An official conda package is available through conda-forge:

```console
conda install -c conda-forge ants
```

## Development

This project is managed with [Hatch][hatch]:

```console
pipx install hatch
```

To run the test suite:

```console
hatch run test
```

To fix linting issues:

```console
hatch run lint:fix
```

## License

This project is distributed under the terms of the [Apache License, Version 2.0][license].

[ants]: https://github.com/ANTsX/ANTs

[hatch]: https://hatch.pypa.io/

[license]: https://spdx.org/licenses/Apache-2.0.html

[pydra]: https://pydra.readthedocs.io/

[pypi-downloads]: https://static.pepy.tech/badge/pydra-ants

[pypi-project]: https://pypi.org/project/pydra-ants

[pypi-pyversions]: https://img.shields.io/pypi/pyversions/pydra-ants.svg

[pypi-version]: https://img.shields.io/pypi/v/pydra-ants.svg

[status-test]: https://github.com/aramis-lab/pydra-ants/actions/workflows/test.yaml/badge.svg
