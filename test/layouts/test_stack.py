# Copyright (c) 2011 Florian Mounier
# Copyright (c) 2012, 2014-2015 Tycho Andersen
# Copyright (c) 2013 Mattias Svala
# Copyright (c) 2013 Craig Barnes
# Copyright (c) 2014 ramnes
# Copyright (c) 2014 Sean Vig
# Copyright (c) 2014 Adi Sieker
# Copyright (c) 2014 Chris Wesseling
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

from liblavinder import layout
import liblavinder.config
from ..conftest import no_xinerama
from .layout_utils import assert_focused, assert_focus_path


class StackConfig:
    auto_fullscreen = True
    main = None
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
        liblavinder.config.Group("c"),
        liblavinder.config.Group("d")
    ]
    layouts = [
        layout.Stack(num_stacks=2),
        layout.Stack(num_stacks=1),
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    keys = []
    mouse = []
    screens = []
    follow_mouse_focus = False


def stack_config(x):
    return no_xinerama(pytest.mark.parametrize("lavinder", [StackConfig], indirect=True)(x))


def _stacks(self):
    stacks = []
    for i in self.c.layout.info()["stacks"]:
        windows = i["clients"]
        current = i["current"]
        stacks.append(windows[current:] + windows[:current])
    return stacks


@stack_config
def test_stack_commands(lavinder):
    assert lavinder.c.layout.info()["current_stack"] == 0
    lavinder.test_window("one")
    assert _stacks(lavinder) == [["one"], []]
    assert lavinder.c.layout.info()["current_stack"] == 0
    lavinder.test_window("two")
    assert _stacks(lavinder) == [["one"], ["two"]]
    assert lavinder.c.layout.info()["current_stack"] == 1
    lavinder.test_window("three")
    assert _stacks(lavinder) == [["one"], ["three", "two"]]
    assert lavinder.c.layout.info()["current_stack"] == 1

    lavinder.c.layout.delete()
    assert _stacks(lavinder) == [["one", "three", "two"]]
    info = lavinder.c.groups()["a"]
    assert info["focus"] == "one"
    lavinder.c.layout.delete()
    assert len(_stacks(lavinder)) == 1

    lavinder.c.layout.add()
    assert _stacks(lavinder) == [["one", "three", "two"], []]

    lavinder.c.layout.rotate()
    assert _stacks(lavinder) == [[], ["one", "three", "two"]]


@stack_config
def test_stack_cmd_down(lavinder):
    lavinder.c.layout.down()


@stack_config
def test_stack_addremove(lavinder):
    one = lavinder.test_window("one")
    lavinder.c.layout.next()
    two = lavinder.test_window("two")
    three = lavinder.test_window("three")
    assert _stacks(lavinder) == [['one'], ['three', 'two']]
    assert lavinder.c.layout.info()["current_stack"] == 1
    lavinder.kill_window(three)
    assert lavinder.c.layout.info()["current_stack"] == 1
    lavinder.kill_window(two)
    assert lavinder.c.layout.info()["current_stack"] == 0
    lavinder.c.layout.next()
    two = lavinder.test_window("two")
    lavinder.c.layout.next()
    assert lavinder.c.layout.info()["current_stack"] == 0
    lavinder.kill_window(one)
    assert lavinder.c.layout.info()["current_stack"] == 1


@stack_config
def test_stack_rotation(lavinder):
    lavinder.c.layout.delete()
    lavinder.test_window("one")
    lavinder.test_window("two")
    lavinder.test_window("three")
    assert _stacks(lavinder) == [["three", "two", "one"]]
    lavinder.c.layout.down()
    assert _stacks(lavinder) == [["one", "three", "two"]]
    lavinder.c.layout.up()
    assert _stacks(lavinder) == [["three", "two", "one"]]
    lavinder.c.layout.down()
    lavinder.c.layout.down()
    assert _stacks(lavinder) == [["two", "one", "three"]]


@stack_config
def test_stack_nextprev(lavinder):
    lavinder.c.layout.add()
    one = lavinder.test_window("one")
    two = lavinder.test_window("two")
    three = lavinder.test_window("three")

    assert lavinder.c.groups()["a"]["focus"] == "three"
    lavinder.c.layout.next()
    assert lavinder.c.groups()["a"]["focus"] == "one"

    lavinder.c.layout.previous()
    assert lavinder.c.groups()["a"]["focus"] == "three"
    lavinder.c.layout.previous()
    assert lavinder.c.groups()["a"]["focus"] == "two"

    lavinder.c.layout.next()
    lavinder.c.layout.next()
    lavinder.c.layout.next()
    assert lavinder.c.groups()["a"]["focus"] == "two"

    lavinder.kill_window(three)
    lavinder.c.layout.next()
    assert lavinder.c.groups()["a"]["focus"] == "one"
    lavinder.c.layout.previous()
    assert lavinder.c.groups()["a"]["focus"] == "two"
    lavinder.c.layout.next()
    lavinder.kill_window(two)
    lavinder.c.layout.next()
    assert lavinder.c.groups()["a"]["focus"] == "one"

    lavinder.kill_window(one)
    lavinder.c.layout.next()
    assert lavinder.c.groups()["a"]["focus"] is None
    lavinder.c.layout.previous()
    assert lavinder.c.groups()["a"]["focus"] is None


@stack_config
def test_stack_window_removal(lavinder):
    lavinder.c.layout.next()
    lavinder.test_window("one")
    two = lavinder.test_window("two")
    lavinder.c.layout.down()
    lavinder.kill_window(two)


@stack_config
def test_stack_split(lavinder):
    lavinder.test_window("one")
    lavinder.test_window("two")
    lavinder.test_window("three")
    stacks = lavinder.c.layout.info()["stacks"]
    assert not stacks[1]["split"]
    lavinder.c.layout.toggle_split()
    stacks = lavinder.c.layout.info()["stacks"]
    assert stacks[1]["split"]


@stack_config
def test_stack_shuffle(lavinder):
    lavinder.c.next_layout()
    lavinder.test_window("one")
    lavinder.test_window("two")
    lavinder.test_window("three")

    stack = lavinder.c.layout.info()["stacks"][0]
    assert stack["clients"][stack["current"]] == "three"
    for i in range(5):
        lavinder.c.layout.shuffle_up()
        stack = lavinder.c.layout.info()["stacks"][0]
        assert stack["clients"][stack["current"]] == "three"
    for i in range(5):
        lavinder.c.layout.shuffle_down()
        stack = lavinder.c.layout.info()["stacks"][0]
        assert stack["clients"][stack["current"]] == "three"


@stack_config
def test_stack_client_to(lavinder):
    lavinder.test_window("one")
    lavinder.test_window("two")
    assert lavinder.c.layout.info()["stacks"][0]["clients"] == ["one"]
    lavinder.c.layout.client_to_previous()
    assert lavinder.c.layout.info()["stacks"][0]["clients"] == ["two", "one"]
    lavinder.c.layout.client_to_previous()
    assert lavinder.c.layout.info()["stacks"][0]["clients"] == ["one"]
    assert lavinder.c.layout.info()["stacks"][1]["clients"] == ["two"]
    lavinder.c.layout.client_to_next()
    assert lavinder.c.layout.info()["stacks"][0]["clients"] == ["two", "one"]


@stack_config
def test_stack_info(lavinder):
    lavinder.test_window("one")
    assert lavinder.c.layout.info()["stacks"]


@stack_config
def test_stack_window_focus_cycle(lavinder):
    # setup 3 tiled and two floating clients
    lavinder.test_window("one")
    lavinder.test_window("two")
    lavinder.test_window("float1")
    lavinder.c.window.toggle_floating()
    lavinder.test_window("float2")
    lavinder.c.window.toggle_floating()
    lavinder.test_window("three")

    # test preconditions, stack adds clients at pos of current
    assert lavinder.c.layout.info()['clients'] == ['three', 'one', 'two']
    # last added window has focus
    assert_focused(lavinder, "three")

    # assert window focus cycle, according to order in layout
    assert_focus_path(lavinder, 'one', 'two', 'float1', 'float2', 'three')
