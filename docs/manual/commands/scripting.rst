=========
Scripting
=========

Client-Server Scripting Model
=============================

Lavinder has a client-server control model - the main Lavinder instance listens on a
named pipe, over which marshalled command calls and response data is passed.
This allows Lavinder to be controlled fully from external scripts. Remote
interaction occurs through an instance of the :class:`liblavinder.command.Client`
class. This class establishes a connection to the currently running instance of
Lavinder, and sources the user's configuration file to figure out which commands
should be exposed. Commands then appear as methods with the appropriate
signature on the ``Client`` object.  The object hierarchy is described in the
:doc:`/manual/commands/index` section of this manual. Full command
documentation is available through the :doc:`Lavinder Shell
</manual/commands/qshell>`.


Example
=======

Below is a very minimal example script that inspects the current lavinder
instance, and returns the integer offset of the current screen.

.. code-block:: python

    from liblavinder.command import Client
    c = Client()
    print c.screen.info()["index"]

Reference
=========

.. lavinder_class:: liblavinder.command.Client
