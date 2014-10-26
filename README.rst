Babblelicious
=============

.. code-block:: bash

    $ virtualenv ve
    (ve)$ pip install -e .
    (ve)$ ve/bin/twistd -n web --class=babblelicious.Server --port=8081
