Python version of the Open Baton CLI
====================================

This project contains a vnfm sdk for python projects.

Technical Requirements
----------------------

This section covers the requirements that must be met by the
python-vnfm-sdk in order to satisfy the demands for such a component:

-  python 2.7

How to install the Open Baton CLI
---------------------------------

The easier way to start is to use a `virtual environment <https://virtualenv.pypa.io/en/stable/>`__. Once activated, just run

.. code:: bash
 
   pip install openbaton-cli

How to use the Open Baton CLI
-----------------------------

After installing the CLI you have a new command:

.. code:: bash

    ./openbaton -h                                                                                                                                                                                                                                                                                                                                                  2 ↵
    usage: openbaton [-h] [-pid PROJECT_ID] [-u USERNAME] [-p PASSWORD] [-d]
                     [-ip NFVO_IP] [--nfvo-port NFVO_PORT] [-s]
                     agent action [params [params ...]]

    positional arguments:
      agent                 the agent you want to use. Possibilities are: ['project', 'vnfci',
                            'vdu', 'log', 'vnfd', 'csarnsd', 'nsd', 'csarvnfd', 'vim', 'vnfr',
                            'service', 'user', 'key', 'vnfpackage', 'nsr', 'event', 'market']
      action                the action you want to call. Possibilities are:
                            ['list', 'show', 'delete', 'create']
      params                The ID, file or JSON

    optional arguments:
      -h, --help            show this help message and exit
      -pid PROJECT_ID, --project-id PROJECT_ID
                            the project-id to use
      -u USERNAME, --username USERNAME
                            the openbaton username
      -p PASSWORD, --password PASSWORD
                            the openbaton password
      -d, --debug           show debug prints
      -ip NFVO_IP, --nfvo-ip NFVO_IP
                            the openbaton nfvo ip
      --nfvo-port NFVO_PORT
                            the openbaton nfvo port
      -s, --ssl             use HTTPS instead of HTTP


Where the agents are:

+------------+------------------+
| Agent      | description      |
+============+==================+
| nsd        | Agent requesting |
|            | Network Service  |
|            | Descriptor       |
+------------+------------------+
| vnfd       | Agent requesting |
|            | Network Service  |
|            | Records          |
+------------+------------------+
| nsr        | Agent requesting |
|            | Network Service  |
|            | Records          |
+------------+------------------+
| vnfr       | Agent requesting |
|            | Virtual Network  |
|            | Service Records  |
+------------+------------------+
| projects   | Agent requesting |
|            | Projects         |
+------------+------------------+
| vim        | Agent requesting |
|            | Point of         |
|            | Presence         |
+------------+------------------+
| user       | Agent requesting |
|            | Users            |
+------------+------------------+
| vnfpackages| Agent requesting |
|            | VNFPAckages      |
+------------+------------------+
| market     | Agent adding     |
|            | Network Service  |
|            | Descriptors from |
|            | the Marketplace  |
+------------+------------------+
| csarnsd    | Agent adding     |
|            | Network Service  |
|            | Descriptors in   |
|            | CSAR format      |
+------------+------------------+
| csarvnfd   | Agent adding     |
|            | Virtual Network  |
|            | Function         |
|            | Descriptors in   |
|            | CSAR format      |
+------------+------------------+
| event      | Agent requesting |
|            | Event Endpoints  |
+------------+------------------+
| service    | Agent requesting |
|            | Services         |
+------------+------------------+

And actions are:

+------------+------------------+
| action     | description      |
+============+==================+
| list       | Request the list |
|            | of agent's       |
|            | objects          |
+------------+------------------+
| show       | Show specific    |
|            | information of   |
|            | an object        |
+------------+------------------+
| create     | create the passed|
|            | object           |
+------------+------------------+
| delete     | delete the       |
|            | specified object |
+------------+------------------+

Issue tracker
-------------

Issues and bug reports should be posted to the GitHub Issue Tracker of
this project

What is Open Baton?
===================

OpenBaton is an open source project providing a comprehensive
implementation of the ETSI Management and Orchestration (MANO)
specification.

Open Baton is a ETSI NFV MANO compliant framework. Open Baton was part
of the OpenSDNCore (www.opensdncore.org) project started almost three
years ago by Fraunhofer FOKUS with the objective of providing a
compliant implementation of the ETSI NFV specification.

Open Baton is easily extensible. It integrates with OpenStack, and
provides a plugin mechanism for supporting additional VIM types. It
supports Network Service management either using a generic VNFM or
interoperating with VNF-specific VNFM. It uses different mechanisms
(REST or PUB/SUB) for interoperating with the VNFMs. It integrates with
additional components for the runtime management of a Network Service.
For instance, it provides autoscaling and fault management based on
monitoring information coming from the the monitoring system available
at the NFVI level.

Source Code and documentation
-----------------------------

The Source Code of the other Open Baton projects can be found
`here <http://github.org/openbaton>`__ and the documentation can be
found `here <http://openbaton.org/documentation>`__ .

News and Website
----------------

Check the `Open Baton Website <http://openbaton.org>`__ Follow us on
Twitter @\ `openbaton <https://twitter.com/openbaton>`__.

Licensing and distribution
--------------------------

Copyright [2015-2016] Open Baton project

Licensed under the Apache License, Version 2.0 (the "License");

you may not use this file except in compliance with the License. You may
obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Copyright © 2015-2016 `Open Baton <http://openbaton.org>`__. Licensed
under `Apache v2 License <http://www.apache.org/licenses/LICENSE-2.0>`__.

Support
-------

The Open Baton project provides community support through the Open Baton
Public Mailing List and through StackOverflow using the tags openbaton.

Supported by
------------

.. image:: https://raw.githubusercontent.com/openbaton/openbaton.github.io/master/images/fokus.png
   :width: 250 px

.. image:: https://raw.githubusercontent.com/openbaton/openbaton.github.io/master/images/tu.png
   :width: 250 px