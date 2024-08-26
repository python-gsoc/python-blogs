# Python-GSoC Blogging platform

Blog and management platform for PSF for running GSoC.  This system was in use until 2024 but will no longer be maintained.

## Build Status

[![Build Status](https://travis-ci.org/python-gsoc/python-blogs.svg?branch=master)](https://travis-ci.org/python-gsoc/python-blogs)

## Installation

- Tested with python 3.7.3

To install development dependncies:

```
$ pip install -r requirements.txt
```

To setup settings copy settings_local.py.template to the root of the dir
```
cp settings_local.py.template settings_local.py
```

## Setup database
- Download and install [XAMPP](https://www.apachefriends.org/download.html) or any other MySQL server
- Open Xampp/MySql Shell
- Login to MySql (default user:'root', default pass:'')
```
mysql -u root 
```
- Create a database
```
CREATE DATABASE python_blogs;
```
- Update username and password in the settings_local.py
- Run migrate command
```
python manage.py migrate
```
- Run command to load data
```
python manage.py loaddata data.json
```

## Usage

```python
python manage.py runserver 0.0.0.0:8000
```

You can then access the site with the login bar with http://127.0.0.1:8000/en/?edit

Default user/pass is `admin` for the superuser

Default student users are `student-1`, `student-2`, `student-3` and `student-4` with pass `^vM7d5*wK2R77V`

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Google OAuth
- Go to https://console.cloud.google.com/ and create a new project
- Enable Google Calendar API and create an OAuth 2.0 client ID
- add following on the Authorised redirect URIs of OAuth client ID
```bash
http://localhost/
```
- Download the JSON file and rename it to `credentials.json`
- Move the file to the root folder of the project

## Virtualenv

A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated python virtual environments for them. This means that each project can have its own dependencies, regardless of what dependencies every other project has. We use a module named `virtualenv` which is a tool to create isolated Python environments. `virtualenv` creates a folder which contains all the necessary executables to use the packages that a Python project would need.

### Installing virtualenv

```bash
$ pip install virtualenv
```

### Test your installation

```bash
$ virtualenv --version
```

### Using virtualenv

You can create a virtualenv using the following command:

```bash
$ virtualenv virtualenv_name
```

After running this command, a directory named my_name will be created. This is the directory which contains all the necessary executables to use the packages that a Python project would need. This is where Python packages will be installed.

Now after creating virtual environment, you need to activate it. Remember to activate the relevant virtual environment every time you work on the project. This can be done using the following command:

```
$ source virtualenv_name/bin/activate
```

Once the virtual environment is activated, the name of your virtual environment will appear on left side of terminal. This will let you know that the virtual environment is currently active.
Now you can install dependencies related to the project in this virtual environment. For example if you are using Django 1.9 for a project, you can install it like you install other packages.

```
(virtualenv_name) $ pip install Django==1.9
```

Once you are done with the work, you can deactivate the virtual environment by the following command:

```
(virtualenv_name) $ deactivate
```

Now you will be back to system’s default Python installation.

