Installation
============
```sudo apt-get update```
```sudo apt-get install libffi-dev nginx uwsgi-plugin-python python-werkzeug python-jinja2 python-setuptools python-wtforms python-serial python-smbus python-sqlite python-sqlalchemy python-pip memcached python-memcache python-flask sqlite3 -y```

```sudo pip install -r requirements.txt```

Raspberry Pi (Raspian)
----------------------
Additionally ```sudo apt-get install python-rpi.gpio -y```

If you're running the code on anything but an RPI (the python-rpi.gpio library is not found on the system) 
the server automatically starts in software mode.
You will see in the console output which GPIOs are switched on and of.


Starting Bartendro UI for the first time
========================================

Starting
--------

Then, once you're ready, run:

   sudo ./ui/bartendro_server.py [--debug] -t <your_ip>


Additional Information
----------------------
werkzeug - http://werkzeug.pocoo.org/docs/
jinja2 - http://jinja.pocoo.org/docs/
wtforms - http://wtforms.simplecodes.com/

flask-sqlalchemy & flask-login archives if not using pip:

   https://pypi.python.org/packages/source/F/Flask-SQLAlchemy/Flask-SQLAlchemy-0.16.tar.gz
   https://pypi.python.org/packages/source/F/Flask-Login/Flask-Login-0.1.3.tar.gz
