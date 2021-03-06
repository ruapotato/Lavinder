# Copyright (c) 2008, Aldo Cortesi. All rights reserved.
# Copyright (c) 2011, Florian Mounier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Set the locale before any widgets or anything are imported, so any widget
# whose defaults depend on a reasonable locale sees something reasonable.
import locale
import logging
from os import path, getenv

from liblavinder.log_utils import init_log, logger
from liblavinder import confreader
from liblavinder.core import xcore

locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())  # type: ignore

try:
    import pkg_resources
    VERSION = pkg_resources.require("lavinder")[0].version
except (pkg_resources.DistributionNotFound, ImportError):
    VERSION = 'dev'


def rename_process():
    """
    Try to rename the lavinder process if py-setproctitle is installed:

    http://code.google.com/p/py-setproctitle/

    Will fail silently if it's not installed. Setting the title lets you do
    stuff like "killall lavinder".
    """
    try:
        import setproctitle
        setproctitle.setproctitle("lavinder")
    except ImportError:
        pass


def make_lavinder():
    from argparse import ArgumentParser
    parser = ArgumentParser(
        description='A full-featured, pure-Python tiling window manager.',
        prog='lavinder',
    )
    parser.add_argument(
        '--version',
        action='version',
        version=VERSION,
    )
    parser.add_argument(
        "-c", "--config",
        action="store",
        default=path.expanduser(path.join(
            getenv('XDG_CONFIG_HOME', '~/.config'), 'lavinder', 'config.py')),
        dest="configfile",
        help='Use the specified configuration file',
    )
    parser.add_argument(
        "-s", "--socket",
        action="store",
        default=None,
        dest="socket",
        help='Path to Lavinder comms socket.'
    )
    parser.add_argument(
        "-n", "--no-spawn",
        action="store_true",
        default=False,
        dest="no_spawn",
        help='Avoid spawning apps. (Used for restart)'
    )
    parser.add_argument(
        '-l', '--log-level',
        default='WARNING',
        dest='log_level',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        help='Set lavinder log level'
    )
    parser.add_argument(
        '--with-state',
        default=None,
        dest='state',
        help='Pickled LavinderState object (typically used only internally)',
    )
    options = parser.parse_args()
    log_level = getattr(logging, options.log_level)
    init_log(log_level=log_level)

    kore = xcore.XCore()
    try:
        default_config_path = path.dirname(path.realpath(__file__))
        default_config_path = default_config_path + "/../resources/default_config.py"
        config = confreader.Config.from_file(kore, default_config_path)
    except Exception as e:
        logger.exception('Error while reading config file (%s)', e)
        exit()
    # XXX: the import is here because we need to call init_log
    # before start importing stuff
    from liblavinder.core import manager
    return manager.Lavinder(
        kore,
        config,
        fname=options.socket,
        no_spawn=options.no_spawn,
        state=options.state,
    )


def main():
    rename_process()
    q = make_lavinder()
    try:
        q.loop()
    except Exception:
        logger.exception('Lavinder crashed')
    logger.info('Exiting...')
