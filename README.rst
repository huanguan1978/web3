WEB3
====

.. web3 is a microframework for Python3 based on WSGI2

`web3 <https://github.com/huanguan1978/web3>`_ is a microframework for Python3 based on `wsgi2 <http://www.python.org/dev/peps/pep-0444/>`_ 

Download
--------

    Clone the repository ::
      $ cd
      $ git clone http://github.com/huanguan1978/web3
      $ cd web3
      $ python3 setup.py install --user

Give It a Try
-------------

    Creating the Project ::
        $ web3tree.py -t 1 /home/MyName/MyProject
    Refresh latest javascript framework ::
        $ web3rejslib.py   /home/MyName/MyProject/MyProject/public/app/www/javascript/framework/

Running the project Application
-------------------------------

    visit you web3 static application in their browser by visiting http://localhost:8080/index.html ::
        $ web3tree.py /home/MyName/MyProject/MyProject/public

    visit you web3 dynamic application in their browser by visiting http://localhost:8080/test ::
        $ python3 /home/MyName/MyProject/MyProject/httpd.py /home/MyName/MyProject/MyProject/
