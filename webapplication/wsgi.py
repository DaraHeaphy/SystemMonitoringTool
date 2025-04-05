import sys

# Add the path to your project
project_home = '/home/DaraHeaphy/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app from your webapplication package
from webapplication import app as application
