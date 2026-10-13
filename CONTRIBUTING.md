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
1. The PR is automatically built and tested with [GitHub Actions][github-actions]. Please know that we appreciate your work even if GitHub Actions suggests changes
    1. _PEP8 Compliance_: [Black][black] is a tool to make code [PEP8][pep8] compliant. Black is run on the code and reports if it would make changes to the code to make it compliant with its formatting rules. To get automatic formatting of your code with Black to PEP8 you can install [pre-commit][pre-commit] with `pre-commit install`. Or configure your IDE to run `black` on changes. In both cases, be active with updating to avoid conflicts with the automation.
    1. _CodeFactor_, _SonarCloud_: CodeFactor and SonarCloud are tools that can suggest changes that would improve security, maintainability and readability. These tools check if no issues were found with the new code and suggest improvements otherwise.
    1. _Flake8_: Checks line lengths and suggest other code cleanliness improvements
    1. _Changelog-enforcer_: Checks if the changelog has been updated with the new changes. The changelog should be updated with a short description of the change and the PR number. A change to the topmost section of the changelog is required for any new functionality or bug fix. This section is named unreleased until a new release, and changes to the latest release number on release branches. For hotfix releases, the changelog-enforcer will not find any changes to the topmost section, as it is written in its entirety in the same PR. In such cases, please add a GitHub label "Skip-Changelog" to the PR. This automatically passes the test.
	1. _Tests and coverage_: The PR should include tests for the new functionality or bug fix. The tests are run automatically and should pass. If the tests fail, please check the code and fix the issue before requesting a review. The coverage, as tallied by Codecov, should ideally always increase, or stay virtually identical with each PR.
	1. _Vulture_: Vulture is a tool that finds unused code. It is run on the code and reports if it finds any unused code. Please check the report and remove any unused code before requesting a review.
	1. _mkdocs_: The documentation is built automatically and should build without errors. If the documentation build fails, please check the code and fix the issue before requesting a review.
	1. _woke_: Woke is a tool that finds insensitive, inconsiderate, and inconsiderate language in code. It is run on the code and reports if it finds any insensitive language. Please check the report and fix any insensitive language before requesting a review.
	1. _Docker stage_: The PR is automatically built and ready for download to staging servers. Please check the build logs and fix any issues before requesting a review. Functional testing on staging servers is normally mandatory before merging. Tests are documented with screenshots or terminal output, and can be done by either the PR author or a reviewer, or ideally both.

### Coding standards

- We try to follow [PEP8][pep8] with an line length of 100
- Always include docstrings to explain functions/classes
- All code has to work for recent python versions. See the [pyproject.toml](pyproject.toml) file for the recommended version of Python and dependencies.

[release_flow]: https://www.nebbiatech.com/2019/03/15/git-branching-strategies-which-one-should-i-pick/
[pep8]: https://www.python.org/dev/peps/pep-0008/
[black]: https://github.com/psf/black
[pre-commit]: https://pre-commit.com/
[github-actions]: https://github.com/features/actions
