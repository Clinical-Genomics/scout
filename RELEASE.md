# Instructions to release a new version of Scout

1. Create a release branch with the release name, e.g. `release-2.0.0` and checkout

    ```bash
    git checkout -b release-2.0.0
    ```
    
1. Update version to, e.g. 2.0.0

   - in `scout/__version__.py`

1. Make sure CHANGELOG.md is up to date for the release

1. Create a new blog post for the documentation
    
    - in `scout/docs/blog/new-2.0.0.md`
    - Update `scout/docs/README.md` to include the blog post
    - Update `scout/docs/SUMMARY.md` to include the blog post

1. Commit changes, push to github and create a pull request

    ```bash
    git add scout/__version__.py
    git add ...
    git commit -m "Release notes version 2.0.0"
    git push -u origin release-2.0.0
    ```
    
1. On github click "create pull request"

1. Merge the pull request, at least one person should review and approve first

1. Pull the new version of master and **tag** the release:

    ```bash
    git tag -a v2.0.0 -m "version 2.0.0 release"
    git push origin v2.0.0
    ```
    
1. Publish to PyPI (Requires correct PyPI owner permissions)

    ```bash
    python setup.py upload
    ```
    
1. build and publish docs (Make sure no unwanted files are added when doing `git add .`, run `git status` first)

    ```bash
    mkdocs gh-deploy
    ```
    
1. update version to, e.g. 2.1.0dev

   - in `scout/__version__.py`

1. add a new `CHANGELOG.md` entry for the unreleased version

1. Commit change and push to master

    ```bash
    git add scout/__version__.py
    git add scout/CHANGELOG.md
    git commit -m "Bump version to 2.1.0dev"
    git push origin master
    ```
    
1. Create new PRs, update CHANGELOG and so forth