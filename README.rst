Babblelicious
=============

.. image:: https://travis-ci.org/smn/babblelicious.svg?branch=develop
     :target: https://travis-ci.org/smn/babblelicious


.. image:: https://coveralls.io/repos/smn/babblelicious/badge.png?branch=develop
     :target: https://coveralls.io/r/smn/babblelicious?branch=develop



.. code-block:: bash

    $ virtualenv ve
    (ve)$ pip install -e .
    (ve)$ ve/bin/twistd -n web --class=babblelicious.Server --port=8081
