# Contributing to Scout

Hi, nice to hear that you wan't to contribute to Scout! Please have a quick read through this text first. Contributing could be anything from questions and bug reports (issues), updating the documentation to fixing features.

## Questions and Bugs

First try to search the issues with some keywords to check if it has been touched before or if there is an ongoing discussion.

If you have found a new topic open a issue and describe as detailed as possible your question.
For bug reports try to include error messages if there are any.

## Contributor Guidelines

### Scout Git branching strategy

Scout development is organized on a flexible Git ["Release Flow" branching system](https://www.nebbiatech.com/2019/03/15/git-branching-strategies-which-one-should-i-pick/). Our Release Flow workflow is similar to the [GitHub Flow system](https://guides.github.com/introduction/flow/), but it differs from it for the fact we don't deploy master to production immediately after a pull request is merged. Instead we plan each new release of the software together with production team at our Facility. Before releasing a new Scout version we create a release branch and a [GitHub Release with a tag](https://github.blog/2013-07-02-release-your-software/) pointing to the head branch of the repository.

The easiest way to create a pull request to Scout would be to clone the repository and create your own feature branch based on an updated master branch. 

### Pull requests

1. We have included an automatic pull request template to help you defining the proposed changes/fixes and how to test the code.
1. If the pull request add functionality the docs should be updated
1. Don't forget to update the CHANGELOG.md document!

### Coding standards

Have a look at previous code and try to follow.
Always include docstrings to explain functions/classes.
All code has to work for python versions > 3.6.
