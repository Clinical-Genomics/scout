# Scout
Analyze VCFs quicker and easier.

--------------

## Overview
Scout is a **visualizer for VCF files** intended for a clinical audience. As such it will enable advanced features like variant filters in an intutative web interface. Scout enables team collaboration by URL sharing and user comments tied to families and variants.

--------------

**N.B. Portable version of Scout.**
A more easily installable version of Scout is under early development and we will make further announcements when it's ready for testing.

--------------

## Motivation
DNA sequencing is quickly entering clinical settings. As such doctors and genetcists need tools that cater to non-bioinformatians. Scout is an attempt to provide a simple interface for bioinformaticians and clinicians alike to collaborate on the interpretation of variant calling results.

--------------

## Installation
For now, install as:

```bash
$ pip install git+https://github.com/Clinical-Genomics/scout.git
```

Extended installation instructions, including how to setup MongoDB, will be added in the future. We also plan to define a Vagrantfile to setting up a demo/development environment for testing.

--------------

### Roadmap
We are trying to build Scout piece-by-piece. This is the prioritized order we are planning on implementing those pieces.

1. Release a MVP of the working interface (core functionality)
2. Take in a first round of feedback from close collaborators
3. Make sure that the package is installable with pip and/or Vagrant

	- Include logging and error reports
	- Setup testing suite

--------------

## Contributing
See [Development](development).
