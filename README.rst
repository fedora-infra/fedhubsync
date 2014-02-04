fedhubsync
==========

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>


fedhubsyncis a sync service to mirror github project in the Fedora infrastructure

This is flask application offers an API that can be called post-push and
that will update a local mirror of the git repository specified.


Get this project:
-----------------
Source:  https://github.com/fedora-infra/fedhubsync


Dependencies:
-------------
* `python <http://www.python.org>`_
* `python-flask <http://flask.pocoo.org/>`_


Running a development instance:
-------------------------------

Clone the source::

 git clone https://github.com/fedora-infra/fedhubsync.git


Run the server::

 python runserver.py

You should be able to access the server at http://localhost:5000


License:
--------

This project is licensed GPLv3+.
