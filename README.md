# pydra-ants

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

[pydra]: https://pydra.readthedocs.io/

[ants]: https://github.com/ANTsX/ANTs

[hatch]: https://hatch.pypa.io/

[license]: https://spdx.org/licenses/Apache-2.0.html
