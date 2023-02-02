from django.core.wsgi import get_wsgi_application
import site
import sys
import os
activate_this = 'C:/Users/myuser/Envs/my_application/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
exec(open(activate_this).read(), dict(__file__=activate_this))


# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:\Python39\Lib\site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:\Users\Matthew Lagoe\Documents\GitHub\python-blogs')
sys.path.append('C:\Users\Matthew Lagoe\Documents\GitHub\python-blogs\gsoc')

os.environ['DJANGO_SETTINGS_MODULE'] = 'gsoc.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gsoc.settings")

application = get_wsgi_application()
