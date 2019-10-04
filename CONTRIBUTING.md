# Contributing to Scout

Hi, nice to hear that you want to contribute to Scout! Please have a quick read through this text 
first. Contributing could be anything from questions and bug reports (issues), updating the 
documentation to fixing features.

## Questions and Bugs

Before submitting a new bug or question try to look into the existing issues (open or closed). 
Your problem could already be solved or the object of an ongoing discussion.

If you have found a new topic open a issue and describe as detailed as possible your question.
For bug reports include error messages if there are any.

## Contributor Guidelines

### Scout Git branching strategy

Scout development is organised on a flexible Git ["Release Flow"][release_flow] branching system.
This more or less means that we make releases in release branches which corresponds to stable 
versions of Scout. 
In order to add a new feature, create a branch from current master and follow the instructions 
below:

### Pull requests

The easiest way to create a pull request to Scout would be to clone the repository and create your 
own feature branch, based on an updated master branch.

1. Please try to name your PR with dashes as separator like `adds-supertrack-to-igv`
1. We have a pull request template to help you defining the proposed changes/fixes and how to test 
    the code.
1. If the pull request adds functionality the docs should be updated.
1. Don't forget to update the CHANGELOG.md document

### Coding standards

- We try to follow [PEP8][pep8] with an line length of 100
- Always include docstrings to explain functions/classes. 
- All code has to work for python versions > 3.6.

[release_flow]: https://www.nebbiatech.com/2019/03/15/git-branching-strategies-which-one-should-i-pick/
[pep8]: https://www.python.org/dev/peps/pep-0008/
