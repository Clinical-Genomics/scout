# Scout react
### prod: https://scout-react.scilifelab.se/
### staging: https://scout-react-stage.scilifelab.se/

You need to be connected to the Scilifelab VPN to access these URLs.

## About

This project contains React modules to be injected in the [Scout Python application](https://github.com/Clinical-Genomics/scout) as well as a React shell to be able to develop on these modules without the Python app.
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
- Deploy the bundle to the server farm
- Add the bundle to Scout. In the page and place where you want your bundle to appear you should add:
```
<div id="react-home"></div>
<script src="https://scout-react.scilifelab.com//institutes.js"></script>
```
- Add also the css to the Scout page:
```
{% block css %}
{{ super() }}
  <link rel="stylesheet" href="https://scout-react.scilifelab.com/institutes.css">
{% endblock %}
```

## Available Scripts

Once cloned the repo, install dependencies with:

### `yarn install`

To run the app three environment variables are needed:

- `GOOGLE_OAUTH_CLIENT_ID` Client ID for the authentication of Clinical Genomics applications via Google. It can be found in the Credentials page on the Clinical genomics Google Cloud Console.
- `BACKEND_URL` The URL for calls to the backend.
- `MOCK` A boolean to define whether to start the fake server using (Mirage js) to mock out backend APIs.

These variables are stored in the server farm and used when deploying the application to Staging and Production.
To run the app with the environment variables in development mode:

### `GOOGLE_OAUTH_CLIENT_ID="the-app-id-here" BACKEND_URL="the-backend-url-here" MOCK="true" yarn start`

Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn lint`
will display linting issues for Typescript and Javascript files.

### `yarn stylelint`
will display linting issues for CSS files.

### `GOOGLE_OAUTH_CLIENT_ID="the-app-id-here" BACKEND_URL="the-backend-url-here" MOCK="true" yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />


## Docker

The app is shipped to docker hub at every push in the `scout-react-stage` project and to `scout-react` when deploying via a workflow.
To pull the latest image from the Clinical Genomics dockerhub repository

```bash
 docker pull clinicalgenomics/scout-react:latest
```

Make sure you are logged in with your DockerHub account.
To run the image and serve the app on port 3000:

```bash
docker run --name scout-react -e BACKEND_URL="here-your-url" -e GOOGLE_OAUTH_CLIENT_ID="here-your-client-id" -e MOCK=true -e PORT=3000 -it -p 3000:3000 scout-react
```

To build a docker image

```bash
docker build --build-arg PORT="3000"  -t scout-react .
```

## Deployment
The app is deployed manually. For staging, in the [GitHub Action UI](https://github.com/Clinical-Genomics/scout-react/actions) by choosing the workflow `Publish and deploy staging`, then `Run workflow` and input the branch that you want to deploy.
For deploying to production, use the workflow `Publish and deploy production`, only the `master` branch can be deployed.

## API mocking library
Mirage JS is used in the project to mock the backend endpoints to continue the development before the actual endpoints are in place.
- The data are located as an object in __mocks__/ScoutResponses.ts

### Fake Rest API. [More info](https://github.com/Clinical-Genomics/scout-mocks-data)
There are some endpoints to test the API calls if the actual APIs are not in place or not working.
The API is created with JSON-server and deployed to Heroku.
- https://scout-mocks-data.herokuapp.com/cases
- https://scout-mocks-data.herokuapp.com/case_report

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
