# Copyright (c) 2017 Dirk Hartmann
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

import pytest

import liblavinder.layout
import liblavinder.bar
import liblavinder.widget
import liblavinder.config
import liblavinder.scratchpad

# import .conftest
from .conftest import Retry
from .conftest import no_xinerama
from .layouts.layout_utils import assert_focused, assert_focus_path


class ScratchPadBaseConfic:
    auto_fullscreen = True
    main = None
    screens = []
    groups = [
        liblavinder.config.ScratchPad('SCRATCHPAD', dropdowns=[
            liblavinder.config.DropDown('dd-a', 'xterm -T dd-a sh', on_focus_lost_hide=False),
            liblavinder.config.DropDown('dd-b', 'xterm -T dd-b sh', on_focus_lost_hide=False),
            liblavinder.config.DropDown('dd-c', 'xterm -T dd-c sh', on_focus_lost_hide=True),
            liblavinder.config.DropDown('dd-d', 'xterm -T dd-d sh', on_focus_lost_hide=True)
        ]),
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
    ]
    layouts = [liblavinder.layout.max.Max()]
    floating_layout = liblavinder.layout.floating.Floating()
    keys = []
    mouse = []


# scratchpad_config = lambda x:
def scratchpad_config(x):
    return no_xinerama(pytest.mark.parametrize("lavinder", [ScratchPadBaseConfic], indirect=True)(x))


@Retry(ignore_exceptions=(KeyError,))
def is_spawned(lavinder, name):
    lavinder.c.group["SCRATCHPAD"].dropdown_info(name)['window']
    return True


@Retry(ignore_exceptions=(ValueError,))
def is_killed(lavinder, name):
    if 'window' not in lavinder.c.group["SCRATCHPAD"].dropdown_info(name):
        return True
    raise ValueError('not yet killed')


@scratchpad_config
def test_toggling(lavinder):
    # adjust command for current display
    lavinder.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-a',
                                                        command='xterm -T dd-a -display %s sh' % lavinder.display)

    lavinder.test_window("one")
    assert lavinder.c.group["a"].info()['windows'] == ['one']

    # First toggling: wait for window
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    is_spawned(lavinder, 'dd-a')

    # assert window in current group "a"
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-a', 'one']
    assert_focused(lavinder, 'dd-a')

    # toggle again --> "hide" xterm in scratchpad group
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    assert lavinder.c.group["a"].info()['windows'] == ['one']
    assert_focused(lavinder, 'one')
    assert lavinder.c.group["SCRATCHPAD"].info()['windows'] == ['dd-a']

    # toggle again --> show again
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-a', 'one']
    assert_focused(lavinder, 'dd-a')
    assert lavinder.c.group["SCRATCHPAD"].info()['windows'] == []


@scratchpad_config
def test_focus_cycle(lavinder):
    # adjust command for current display
==== BASE ====
    qtile.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-a', command='xterm -T dd-a -display %s sh' % qtile.display)
    qtile.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-b', command='xterm -T dd-b -display %s sh' % qtile.display)
==== BASE ====

    lavinder.test_window("one")
    # spawn dd-a by toggling
    assert_focused(lavinder, 'one')

    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    is_spawned(lavinder, 'dd-a')
    assert_focused(lavinder, 'dd-a')

    lavinder.test_window("two")
    assert_focused(lavinder, 'two')

    # spawn dd-b by toggling
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-b')
    is_spawned(lavinder, 'dd-b')
    assert_focused(lavinder, 'dd-b')

    # check all windows
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-a', 'dd-b', 'one', 'two']

    assert_focus_path(lavinder, 'one', 'two', 'dd-a', 'dd-b')


@scratchpad_config
def test_focus_lost_hide(lavinder):
    # adjust command for current display
==== BASE ====
    qtile.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-c', command='xterm -T dd-c -display %s sh' % qtile.display)
    qtile.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-d', command='xterm -T dd-d -display %s sh' % qtile.display)
==== BASE ====

    lavinder.test_window("one")
    assert_focused(lavinder, 'one')

    # spawn dd-c by toggling
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-c')
    is_spawned(lavinder, 'dd-c')
    assert_focused(lavinder, 'dd-c')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-c', 'one']

    # New Window with Focus --> hide current DropDown
    lavinder.test_window("two")
    assert_focused(lavinder, 'two')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['one', 'two']
    assert sorted(lavinder.c.group["SCRATCHPAD"].info()['windows']) == ['dd-c']

    # spawn dd-b by toggling
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-d')
    is_spawned(lavinder, 'dd-d')
    assert_focused(lavinder, 'dd-d')

    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-d', 'one', 'two']
    assert sorted(lavinder.c.group["SCRATCHPAD"].info()['windows']) == ['dd-c']

    # focus next, is the first tiled window --> "hide" dd-d
    lavinder.c.group.next_window()
    assert_focused(lavinder, 'one')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['one', 'two']
    assert sorted(lavinder.c.group["SCRATCHPAD"].info()['windows']) == ['dd-c', 'dd-d']

    # Bring dd-c to front
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-c')
    assert_focused(lavinder, 'dd-c')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-c', 'one', 'two']
    assert sorted(lavinder.c.group["SCRATCHPAD"].info()['windows']) == ['dd-d']

    # Bring dd-d to front --> "hide dd-c
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-d')
    assert_focused(lavinder, 'dd-d')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-d', 'one', 'two']
    assert sorted(lavinder.c.group["SCRATCHPAD"].info()['windows']) == ['dd-c']

    # change current group to "b" hids DropDowns
    lavinder.c.group['b'].toscreen()
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['one', 'two']
    assert sorted(lavinder.c.group["SCRATCHPAD"].info()['windows']) == ['dd-c', 'dd-d']


@scratchpad_config
def test_kill(lavinder):
    # adjust command for current display
==== BASE ====
    qtile.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-a', command='xterm -T dd-a -display %s sh' % qtile.display)

    qtile.test_window("one")
    assert_focused(qtile, 'one')
==== BASE ====

    # dd-a has no window associated yet
    assert 'window' not in lavinder.c.group["SCRATCHPAD"].dropdown_info('dd-a')

    # First toggling: wait for window
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    is_spawned(lavinder, 'dd-a')
    assert_focused(lavinder, 'dd-a')
    assert lavinder.c.group["SCRATCHPAD"].dropdown_info('dd-a')['window']['name'] == 'dd-a'

    # kill current window "dd-a"
    lavinder.c.window.kill()
    is_killed(lavinder, 'dd-a')
    assert_focused(lavinder, 'one')
    assert 'window' not in lavinder.c.group["SCRATCHPAD"].dropdown_info('dd-a')


@scratchpad_config
def test_floating_toggle(lavinder):
    # adjust command for current display
==== BASE ====
    qtile.c.group["SCRATCHPAD"].dropdown_reconfigure('dd-a', command='xterm -T dd-a -display %s sh' % qtile.display)
==== BASE ====

    lavinder.test_window("one")
    assert_focused(lavinder, 'one')

    # dd-a has no window associated yet
    assert 'window' not in lavinder.c.group["SCRATCHPAD"].dropdown_info('dd-a')
    # First toggling: wait for window
    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    is_spawned(lavinder, 'dd-a')
    assert_focused(lavinder, 'dd-a')

    assert 'window' in lavinder.c.group["SCRATCHPAD"].dropdown_info('dd-a')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-a', 'one']

    lavinder.c.window.toggle_floating()
    # dd-a has no window associated any more, but is still in group
    assert 'window' not in lavinder.c.group["SCRATCHPAD"].dropdown_info('dd-a')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-a', 'one']

    lavinder.c.group["SCRATCHPAD"].dropdown_toggle('dd-a')
    is_spawned(lavinder, 'dd-a')
    assert sorted(lavinder.c.group["a"].info()['windows']) == ['dd-a', 'dd-a', 'one']
