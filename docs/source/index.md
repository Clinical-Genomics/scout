# Scout
Analyze VCFs quicker and easier.

## Motivation
DNA sequencing is quickly entering the clinical setting. As such we need tools that cater to non-bioinformatics people. Scout is an attempt to provide an interface for bioinformaticians and clinicians alike to collaborate on the interpretation of variant calling results.


## Installation
Scout is not currently on *pip* but we intend on registering it once we work out more specifically the scope of the package.

For now, install as:

```bash
$ pip install https://github.com/Clinical-Genomics/scout/zipball/master
```

### Core dependencies

- MongoDB
- Python
- Probably some C-compiler(s)

**Recommended dependencies**

- Docker


## Goals
There are 3 main goals stated for the project.

  1. Visualize (annotated) VCFs
  2. Following (coding) best practices
  3. Be designed as a natural point of entry for customer

For each of these topics there are a number of more concrete objectives ranked as primary, secondary (if possibles), or tertiary (if we have time).

### 1. Visualize (annotated) VCFs
We don't need to be GEMINI, focus more on visual part, marking, commenting etc.


## Roadmap
We are trying to build Scout piece by piece. This is the prioritized order we are planning on implementing those pieces.

- [ ] Prepare real world representation of demo data + import CLI
- [ ] Release a first draft of the working interface (core functionality)
- [ ] Make sure that the package is installable with pip and/or Docker
	- Include logging and error reports
	- Setup testing suite
- [ ] Take in a first round of feedback from close collaborators
- [ ] Add functionality for user management and comments
	- Profile, settings, feedback functionality
	- Feeds and actitivy indicator in case list
- [ ] Implement more of less MIP/Clinical Genomics specific functionality
  - Access rights connected with cases/families. "Admin" users should be able to view any case.
  - IGV
  - Sanger email order (+ image from IGV?)
  - Show gene list and ethical approval in case list


## Contributing
Further details to come at a later stage.
