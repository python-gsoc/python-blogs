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

Default student user is `Test-Student1` pass `^vM7d5*wK2R77V'`
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Git

To see diff's on the database you will need to run the following command :-
```bash
git config --local include.path ../.gitconfig
```
Also make sure sqlite3 is available.
