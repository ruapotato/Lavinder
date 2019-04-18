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
from time import sleep

from liblavinder import layout
import liblavinder.config
from ..conftest import no_xinerama
from .layout_utils import assert_focused, assert_focus_path


class RatioTileConfig:
    auto_fullscreen = True
    main = None
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
        liblavinder.config.Group("c"),
        liblavinder.config.Group("d")
    ]
    layouts = [
        layout.RatioTile(ratio=.5),
        layout.RatioTile(),
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    keys = []
    mouse = []
    screens = []
    follow_mouse_focus = False


def ratiotile_config(x):
    return no_xinerama(pytest.mark.parametrize("lavinder", [RatioTileConfig], indirect=True)(x))


@ratiotile_config
def test_ratiotile_add_windows(lavinder):
    for i in range(12):
        lavinder.test_window(str(i))
        if i == 0:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 800, 600)]
        elif i == 1:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 400, 600), (400, 0, 400, 600)]
        elif i == 2:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 266, 600), (266, 0, 266, 600), (532, 0, 268, 600)]
        elif i == 3:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 200, 600), (200, 0, 200, 600), (400, 0, 200, 600),
                (600, 0, 200, 600)]
        elif i == 4:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 160, 600), (160, 0, 160, 600), (320, 0, 160, 600),
                (480, 0, 160, 600), (640, 0, 160, 600)]
        elif i == 5:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 133, 600), (133, 0, 133, 600), (266, 0, 133, 600),
                (399, 0, 133, 600), (532, 0, 133, 600), (665, 0, 135, 600)]
        elif i == 6:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 200, 300), (200, 0, 200, 300), (400, 0, 200, 300),
                (600, 0, 200, 300), (0, 300, 266, 300),
                (266, 300, 266, 300), (532, 300, 268, 300)]
        elif i == 7:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 200, 300), (200, 0, 200, 300), (400, 0, 200, 300),
                (600, 0, 200, 300), (0, 300, 200, 300),
                (200, 300, 200, 300), (400, 300, 200, 300),
                (600, 300, 200, 300)]
        elif i == 8:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 160, 300), (160, 0, 160, 300), (320, 0, 160, 300),
                (480, 0, 160, 300), (640, 0, 160, 300), (0, 300, 200, 300),
                (200, 300, 200, 300), (400, 300, 200, 300),
                (600, 300, 200, 300)]
        elif i == 9:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 160, 300), (160, 0, 160, 300), (320, 0, 160, 300),
                (480, 0, 160, 300), (640, 0, 160, 300), (0, 300, 160, 300),
                (160, 300, 160, 300), (320, 300, 160, 300),
                (480, 300, 160, 300), (640, 300, 160, 300)]
        elif i == 10:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 133, 300), (133, 0, 133, 300), (266, 0, 133, 300),
                (399, 0, 133, 300), (532, 0, 133, 300), (665, 0, 135, 300),
                (0, 300, 160, 300), (160, 300, 160, 300),
                (320, 300, 160, 300), (480, 300, 160, 300),
                (640, 300, 160, 300)]
        elif i == 11:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 133, 300), (133, 0, 133, 300), (266, 0, 133, 300),
                (399, 0, 133, 300), (532, 0, 133, 300), (665, 0, 135, 300),
                (0, 300, 133, 300), (133, 300, 133, 300),
                (266, 300, 133, 300), (399, 300, 133, 300),
                (532, 300, 133, 300), (665, 300, 135, 300)]
        else:
            assert False


@ratiotile_config
def test_ratiotile_add_windows_golden_ratio(lavinder):
    lavinder.c.next_layout()
    for i in range(12):
        lavinder.test_window(str(i))
        if i == 0:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 800, 600)]
        elif i == 4:
            # the rest test col order
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 400, 200), (0, 200, 400, 200), (0, 400, 400, 200),
                (400, 0, 400, 300), (400, 300, 400, 300)]
        elif i == 5:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 400, 200), (0, 200, 400, 200), (0, 400, 400, 200),
                (400, 0, 400, 200), (400, 200, 400, 200),
                (400, 400, 400, 200)]

        elif i == 9:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 266, 150), (0, 150, 266, 150), (0, 300, 266, 150),
                (0, 450, 266, 150), (266, 0, 266, 150),
                (266, 150, 266, 150), (266, 300, 266, 150),
                (266, 450, 266, 150), (532, 0, 266, 300),
                (532, 300, 266, 300)]
        elif i == 10:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 266, 150), (0, 150, 266, 150), (0, 300, 266, 150),
                (0, 450, 266, 150), (266, 0, 266, 150),
                (266, 150, 266, 150), (266, 300, 266, 150),
                (266, 450, 266, 150), (532, 0, 266, 200),
                (532, 200, 266, 200), (532, 400, 266, 200)]
        elif i == 11:
            assert lavinder.c.layout.info()['layout_info'] == [
                (0, 0, 266, 150), (0, 150, 266, 150), (0, 300, 266, 150),
                (0, 450, 266, 150), (266, 0, 266, 150),
                (266, 150, 266, 150), (266, 300, 266, 150),
                (266, 450, 266, 150), (532, 0, 266, 150),
                (532, 150, 266, 150), (532, 300, 266, 150),
                (532, 450, 266, 150)]


@ratiotile_config
def test_ratiotile_basic(lavinder):
    lavinder.test_window("one")
    lavinder.test_window("two")
    lavinder.test_window("three")
    sleep(0.1)
    assert lavinder.c.window.info()['width'] == 264
    assert lavinder.c.window.info()['height'] == 598
    assert lavinder.c.window.info()['x'] == 0
    assert lavinder.c.window.info()['y'] == 0
    assert lavinder.c.window.info()['name'] == 'three'

    lavinder.c.group.next_window()
    assert lavinder.c.window.info()['width'] == 264
    assert lavinder.c.window.info()['height'] == 598
    assert lavinder.c.window.info()['x'] == 266
    assert lavinder.c.window.info()['y'] == 0
    assert lavinder.c.window.info()['name'] == 'two'

    lavinder.c.group.next_window()
    assert lavinder.c.window.info()['width'] == 266
    assert lavinder.c.window.info()['height'] == 598
    assert lavinder.c.window.info()['x'] == 532
    assert lavinder.c.window.info()['y'] == 0
    assert lavinder.c.window.info()['name'] == 'one'


@ratiotile_config
def test_ratiotile_window_focus_cycle(lavinder):
    # setup 3 tiled and two floating clients
    lavinder.test_window("one")
    lavinder.test_window("two")
    lavinder.test_window("float1")
    lavinder.c.window.toggle_floating()
    lavinder.test_window("float2")
    lavinder.c.window.toggle_floating()
    lavinder.test_window("three")

    # test preconditions, RatioTile adds clients to head
    assert lavinder.c.layout.info()['clients'] == ['three', 'two', 'one']
    # last added window has focus
    assert_focused(lavinder, "three")

    # assert window focus cycle, according to order in layout
    assert_focus_path(lavinder, 'two', 'one', 'float1', 'float2', 'three')
