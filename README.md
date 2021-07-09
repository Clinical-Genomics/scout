# Scout react https://scout-stage.web.app/

## About

## Available Scripts

Once cloned the repo, install dependencies with:

### `yarn install`

To run the app three environment variables are needed:

- `GOOGLE_OAUTH_CLIENT_ID` Client ID for the authentication of Clinical Genomics applications via Google. It can be found in the Credentials page on the Clinical genomics Google Cloud Console.

These variables are stored in this repo secrets and are used by GitHub actions when deploying the application to Staging and Production.
To run the app with the environment variables in development mode:

### `GOOGLE_OAUTH_CLIENT_ID="the-app-id-here" yarn start`

Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn lint`
will display linting issues.

### `yarn format`
will fix the errors.


### `GOOGLE_OAUTH_CLIENT_ID="the-app-id-here" yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />

## Standards to be used for commit messages
Type can be:
- `feature`: (new feature for the user, not a new feature for build script)
- `fix`: (bug fix for the user, not a fix to a build script)
- `docs`: (changes to the documentation)
- `style`: (formatting, missing semi colons, etc; no production code change)
- `refactor`: (refactoring production code, eg. renaming a variable)
- `test`: (adding missing tests, refactoring tests; no production code change)
- `chore`: (updating grunt tasks etc; no production code change)

### Message example
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


