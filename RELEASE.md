# Instructions to release a new version of Scout

1. Create a release branch with the release name, e.g. `release-2.0.0` and checkout

    ```bash
    git checkout -b release-2.0.0
    ```

1. Update version to, e.g. 2.0.0

   - in `scout/pyproject.toml`

1. Upgrade dependencies that are not frozen to their latest compatible version e.g.
   ```bash
   uv lock --upgrade
   git add uv.lock
   git commit -m 'Upgrade dependencies'
   ```

1. Make sure CHANGELOG.md is up to date for the release

1. Create a new blog post for the documentation

    - in `scout/docs/blog/new-2.0.0.md`
    - Update `scout/docs/README.md` to include the blog post

1. You can check the the new blog post looks as expected by running `mkdocs serve`. This way the updated pages will show in you browser if you open up the url written in the terminal (in general http://127.0.0.1:8000/ or http://0.0.0.0:4000/). Pages will rebuild automatically any time a change is introduced, so there is no need to run this command more than once.

1. Commit changes, push to github and create a pull request

    ```bash
    git add -u
    git commit -m "Release notes version 2.0.0"
    git push -u origin release-2.0.0
    ```

1. On github click "Create pull request"

1. After getting the pull request approved by a reviewer merge it to master.

1. Draft a new release on GitHub, add some text - e.g. an abbreviated CHANGELOG - and release.
This adds a version tag, builds and submits to PyPi.

1. *Skip if using GitHub Action* Pull the new version of master and **tag** the release:

    ```bash
    git tag -a v2.0.0 -m "version 2.0.0 release"
    git push origin v2.0.0
    ```

1. build and publish docs (Make sure no unwanted files are added when doing `git add .`, run `git status` first)

    ```bash
    mkdocs gh-deploy
    ```
