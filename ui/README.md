Installation
============
```sudo apt-get update```
```sudo apt-get install nginx uwsgi-plugin-python python-werkzeug python-jinja2 python-setuptools python-wtforms python-serial python-smbus python-sqlite python-sqlalchemy python-pip memcached python-memcache python-flask sqlite3 -y```

```sudo pip install flask-sqlalchemy flask-login```

Raspberry Pi (Raspian)
----------------------
Additionally ```sudo apt-get install python-rpi.gpio -y```



Starting Bartendro UI for the first time
========================================

Database
--------

To start Bartendro for the first time, you'll need to copy the bartendro.db.default
file to bartendro.db in the ui directory. This provides a clean database with all
the required tables for you to start playing with.

Configuration
-------------

You'll need to copy the config.py.default file to config.py . This will assume
the basic sane setting for your Bartendro configuration. These settings will be migrated
to the DB soon, so please take a look at the file to see what can be changed.

Starting
--------

Then, once you're ready, run:

   # sudo ./ui/bartendro_server.py --debug

That should start the server on all interfaces on your machine. 

Software only mode
------------------

If you're running the code on anything but an RPI connected to full Bartendro hardware,
you'll need to do:

   # export BARTENDRO_SOFTWARE_ONLY=1

Otherwise the software will attempt to communicate with the hardware that isn't present
and fail. In the software only mode the bartendro UI will run an attempt to do everything
it can, short of actually communicating with the hardware. If you are running in
software only mode, you do no need to run the bartendro_server.py program under sudo. Sudo
rights are only needed to communicate with the hardware.

Additional Information
----------------------
werkzeug - http://werkzeug.pocoo.org/docs/
jinja2 - http://jinja.pocoo.org/docs/
wtforms - http://wtforms.simplecodes.com/

flask-sqlalchemy & flask-login archives if not using pip:

   https://pypi.python.org/packages/source/F/Flask-SQLAlchemy/Flask-SQLAlchemy-0.16.tar.gz
   https://pypi.python.org/packages/source/F/Flask-Login/Flask-Login-0.1.3.tar.gz
