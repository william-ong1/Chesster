# Config

Tool and project config files live here to keep the repo root clean.

- **requirements.txt** – Python dependencies. Install with: `pip install -r config/requirements.txt`
- **pyproject.toml** – Pytest (and Black) config. Run tests with: `pytest -c config/pyproject.toml` or `coverage run -m pytest -c config/pyproject.toml`
- **pylintrc** – Pylint config. Lint with: `pylint --rcfile=config/pylintrc .`

CI uses these paths automatically.
