Ensure docker is installed. Clone the Chesster Github repository. Currently the project uses a single repository, so this is all you will need.
cd into the Chesster Github repository
run 
npm install && npm run start (make sure node.js is installed).
The app will run.
To edit any of the main app functions, edit main.js and the shell scripts in maia-individual. To edit the UI, look into renderer.js, index.html, and styles.css

## Our Repository Structure

```text
/
├── .github/            # CI/CD workflows
├── app/                # Main application logic (API routes, game logic)
├── models/             # Stores trained models
├── maia-individual/    # Custom model training, evaluation, and base maia models
├── Tests/              # Unit and integration tests for backend logic
├── scripts/            # To assist with data cleaning and other utilities
├── StatusReports/      # Project documentation, progress and status reports
├── README.md           # Description on the application and how to build/test it
```
The source code is in app/.
The tests are in Tests/

**Testing the system:**
- To install all required testing tools (requires Python and NodeJS):
```sh
npm i --save-dev vitest
npm i --save-dev @vitest/coverage-v8
pip install pytest
pip install coverage
```
- To run python tests with a coverage report:
```sh
coverage run -m pytest; coverage report -m
```
- To run TypeScript tests with a coverage report:
```sh
npm run test:coverage
```
- Alternative method for TypeScript tests:
```sh
vitest run --coverage
```
- CI: With GitHub Actions, all unit tests (Python and TypeScript) and their coverage reports are run on every push and pull request. A linter is also run over all code written by us (we exclude some config files that have a JavaScript or TypeScript file extension from the linter).
- `vitest`

Tests should be added to the \Tests folder. 

**Building the application**
To build the application into an executable installer
run
npm run build

This command uses Electron to package the app and create an installer executable.

Make sure to run this after running npm install to ensure latest dependencies and up to date. After building, make sure that the installer successfully installs the application and perform manual testing to confirm the app works as expected.
