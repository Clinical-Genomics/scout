# Scout
Analyze VCFs quicker and easier.

--------------

## Overview
Scout is a **visualizer for VCF files** intended for a clinical audience. As such it will presents advanced features like variant filters in an intutative web interface. Scout enables team collaboration by URL sharing and user comments tied to families and variants.

--------------

**Scout is currently in active development.**

Most of the features are already worked out but the code base will still change significantly before the eventual 1.0 release.

--------------

## Motivation
DNA sequencing is quickly entering clinical settings. As such doctors and genetcists need tools that cater to non-bioinformatians. Scout is an attempt to provide a simple interface for bioinformaticians and clinicians alike to collaborate on the interpretation of variant calling results.

--------------

## Installation
For now, install as:

```bash
$ pip install git+https://github.com/Clinical-Genomics/scout.git
```

Extended installation instructions, including how to setup MongoDB, will be added here in the future. We also plan to define a couple of Dockerfiles to simplify deployment to a single command and a single dependency (Docker).

--------------

## Goals
There are three main goals stated for the project.

  1. Visualize (annotated) VCFs
  2. Follow (coding) best practices
  3. Be reasonably easy to setup

### Roadmap
We are trying to build Scout piece-by-piece. This is the prioritized order we are planning on implementing those pieces.

1. Release a MVP of the working interface (core functionality)
2. Make sure that the package is installable with pip and/or Docker

	- Include logging and error reports
	- Setup testing suite

3. Take in a first round of feedback from close collaborators
4. Add functionality for user management and comments

	- Profile, settings, feedback functionality
	- Feeds and actitivy indicator in case list

5. Implement MIP/Clinical Genomics specific functionality

	- Access rights connected with cases/families. "Admin" users should be able to view any case.
	- IGV
	- Sanger email order (+ image from IGV?)
	- Show gene list and ethical approval in case list

--------------

## Contributing
See [Development](development).
