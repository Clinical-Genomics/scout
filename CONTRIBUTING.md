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
    the code
1. If the pull request adds functionality the docs should be updated
1. Don't forget to update the CHANGELOG.md document
1. The PR is automatically built and tested on [Travis-CI][travis-ci]. Please know that we appreciate your work even if Travis suggests changes
    1. _PEP8 Compliance_: [Black][black] is a tool to make code [PEP8][pep8] compliant. Black is run on the code and reports if it would make changes to the code to make it compliant with its formatting rules. To get automatic formatting of your code with Black to PEP8 you can install [pre-commit][pre-commit] with `pre-commit install`
    1. _Pylint Rating_: Pylint is a tool that can suggest changes that would improve maintainability and readability. This tool checks if the new code is at least as well structured as the previous version and suggests improvements otherwise. This check will turn green when the code is at least as well structured as the previous version
    1. _Lint Free_: Checks line lengths and suggest other code cleanliness improvements

### Coding standards

- We try to follow [PEP8][pep8] with an line length of 100
- Always include docstrings to explain functions/classes
- All code has to work for python 3.6+

[release_flow]: https://www.nebbiatech.com/2019/03/15/git-branching-strategies-which-one-should-i-pick/
[pep8]: https://www.python.org/dev/peps/pep-0008/
[black]: https://github.com/psf/black
[pre-commit]: https://pre-commit.com/
[travis-ci]: https://travis-ci.org/
