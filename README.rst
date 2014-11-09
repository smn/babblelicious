Babblelicious
=============

.. image:: https://travis-ci.org/smn/babblelicious.svg?branch=develop
     :target: https://travis-ci.org/smn/babblelicious


.. image:: https://coveralls.io/repos/smn/babblelicious/badge.png?branch=develop
     :target: https://coveralls.io/r/smn/babblelicious?branch=develop

.. code-block:: bash

    $ virtualenv ve
    (ve)$ pip install -e .
    (ve)$ babblelicious -a <fb-app-id> -u http://fb-auth-callback/url/

Use something like ngrok_ to expose your locally running service on the
Internet and use that url as the url for ``-u`` / `--fb-auth-url`
parameter.

.. _Ngrok: https://ngrok.com/
