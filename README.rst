summitsched - A proxy to edit the OpenStack Design Summit sched.org
===================================================================

summitsched is the Django app used for the OpenStack Design Summit
session scheduling on sched.org. It makes use of the cheddar
component.

Configuration and Usage
-----------------------

Copy local_settings.py.sample to local_settings.py and change
settings there.

Create empty database:
./manage.py syncdb

Copy sched.json.sample to sched.json and edit the file to match
the tracks and trackleads you want to have. Then run:

./manage.py loadsched sched.json

Then run a dev server using:
./manage.py runserver
