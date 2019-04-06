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
A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated python virtual environments for them.
This means that each project can have its own dependencies, regardless of what dependencies every other project has.
We use a module named virtualenv which is a tool to create isolated Python environments.
virtualenv creates a folder which contains all the necessary executables to use the packages that a Python project would need.

Installing virtualenv:

$ pip install virtualenv

Test your installation:

$ virtualenv --version

Using virtualenv

You can create a virtualenv using the following command:

$ virtualenv my_name

After running this command, a directory named my_name will be created. This is the directory which contains all the necessary executables to use the packages that a Python project would need. This is where Python packages will be installed.
Now you can install dependencies related to the project in this virtual environment. For example if you are using Django 1.9 for a project, you can install it like you install other packages.

(virtualenv_name)$ pip install Django==1.9

Once you are done with the work, you can deactivate the virtual environment by the following command:

(virtualenv_name)$ deactivate

Now you will be back to system’s default Python installation.



