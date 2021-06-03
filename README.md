# Scout react https://scout-stage.web.app/
## Standards 
Type can be:
- `feature`: (new feature for the user, not a new feature for build script)
- `fix`: (bug fix for the user, not a fix to a build script)
- `docs`: (changes to the documentation)
- `style`: (formatting, missing semi colons, etc; no production code change)
- `refactor`: (refactoring production code, eg. renaming a variable)
- `test`: (adding missing tests, refactoring tests; no production code change)
- `chore`: (updating grunt tasks etc; no production code change)

### Commit message stanadard
The message will have form:
[type] (main component): [description] (#[issue number])

Examples:
- `Chore: Update standards for commit message and user story (#2, #3)`
- `Feature (Nav): Adding navigation menu (#1)`

### Branch name standard
[type]/[issue number]

Examples: 
- `feature/3`
- `fix/4`


### Bump the version on master (by code-owner):
- Cloning the master branch locally or pull master into local existing clone
- Run: `bump2version patch|minor|major` if applicable
- Push version bump: `git push && git push --tags` if applicable
