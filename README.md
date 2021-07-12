# Scout react https://scout-stage.web.app/

## About

This project contains react modules to be injected in the [Scout Python application](https://github.com/Clinical-Genomics/scout) as well as a React shell to be able to develop on these modules without the Python app.
The modules are listed in the `/modules` directory

### How to add a module

- Add a directory with a React component in the `/modules` directory.
- Add an `index.tsx` file that will be the webpack entry for the module. The file should include where the module will be rendered and which component:
```
ReactDOM.render(<Institutes />, document.getElementById('react-insitutes'))
```
- Edit the `webpack.config.js` file to include the new module entry point. When running `yarn build` react will create two bundle, one called `[name].js` and one `[name].css` (for example, for the institutes component, the files will be called `institutes.js` and `institutes.css`)
```
  entry: {
    institutes: '/src/modules/Institutes/index.tsx',
    home: '/src/modules/Home/index.tsx',
    appShell: './src/index.tsx',
  },
```
- Deploy the bundle to firebase
- Add the bundle to Scout. In the page and place where you want your bundle to appear you should add:
```  
<div id="react-home"></div>
<script src="https://scout-stage.web.app//institutes.js"></script>
```
- Add also the css to the Scout page:
```
{% block css %}
{{ super() }}
  <link rel="stylesheet" href="https://scout-stage.web.app/institutes.css">
{% endblock %}
```

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
Commit messages should be a concise description of the task done in imperative present tense

Examples:
- `Update standards for commit message`
- `Adding navigation menu`

### Branch name standard
[type]/[concise description of the issue]

- `feature`: (new feature for the user, not a new feature for build script)
- `fix`: (bug fix for the user, not a fix to a build script)
- `docs`: (changes to the documentation)
- `refactor`: (refactoring production code, eg. renaming a variable)

Examples: 
- `feature/add-institutes-endpoint`
- `fix/dialog-not-showing-on-safari`


