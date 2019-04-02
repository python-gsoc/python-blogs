# Python-GSoC Blogging platform

Blog and management platform for PSF for running GSoC

## Installation

Requires python 3.6+

```bash
pip install -r requirements.txt
```

## Usage

```python
python manage.py runserver 0.0.0.0:8000
```

You can then access the site with the login bar with http://127.0.0.1:8000/en/?edit
```
Default user/pass is `admin` for the superuser

Default student user is `Test-Student1` pass `^vM7d5*wK2R77V`
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Git

To see diff's on the database you will need to run the following command :-
```bash
git config --local include.path ../.gitconfig
```
Also make sure sqlite3 is available.

## Usage

It is recommended to set up virtual environment on your local machine, to seprate this project package from the package you have on your local machine.

#### For virtualenv
[Installation](https://virtualenv.pypa.io/en/latest/userguide/)  [Setup Guide](https://virtualenv.pypa.io/en/latest/userguide/)
#### For virtualenvwrapper
[Installation](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)  [Setup Guide](https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html)
#### For pyenv
[Installation](https://github.com/pyenv/pyenv#installation)  [Setup Guide](https://github.com/pyenv/pyenv#command-reference)
#### For pipenv
[Installation](https://pipenv.readthedocs.io/en/latest/#install-pipenv-today)  [Setup Guide](https://pipenv.readthedocs.io/en/latest/#pipenv-usage)
#### For anaconda
[Installation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)  [Setup Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
