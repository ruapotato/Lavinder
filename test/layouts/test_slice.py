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
from .layout_utils import assert_dimensions, assert_focused, assert_focus_path
from ..conftest import no_xinerama


class SliceConfig:
    auto_fullscreen = True
    main = None
    groups = [
        liblavinder.config.Group("a"),
    ]
    layouts = [
        layout.Slice(side='left', width=200, wname='slice',
                     fallback=layout.Stack(num_stacks=1, border_width=0)),
        layout.Slice(side='right', width=200, wname='slice',
                     fallback=layout.Stack(num_stacks=1, border_width=0)),
        layout.Slice(side='top', width=200, wname='slice',
                     fallback=layout.Stack(num_stacks=1, border_width=0)),
        layout.Slice(side='bottom', width=200, wname='slice',
                     fallback=layout.Stack(num_stacks=1, border_width=0)),
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    keys = []
    mouse = []
    screens = []
    follow_mouse_focus = False


def slice_config(x):
    return no_xinerama(pytest.mark.parametrize("lavinder", [SliceConfig], indirect=True)(x))


@slice_config
def test_no_slice(lavinder):
    lavinder.test_window('one')
    assert_dimensions(lavinder, 200, 0, 600, 600)
    lavinder.test_window('two')
    assert_dimensions(lavinder, 200, 0, 600, 600)


@slice_config
def test_slice_first(lavinder):
    lavinder.test_window('slice')
    assert_dimensions(lavinder, 0, 0, 200, 600)
    lavinder.test_window('two')
    assert_dimensions(lavinder, 200, 0, 600, 600)


@slice_config
def test_slice_last(lavinder):
    lavinder.test_window('one')
    assert_dimensions(lavinder, 200, 0, 600, 600)
    lavinder.test_window('slice')
    assert_dimensions(lavinder, 0, 0, 200, 600)


@slice_config
def test_slice_focus(lavinder):
    lavinder.test_window('one')
    assert_focused(lavinder, 'one')
    two = lavinder.test_window('two')
    assert_focused(lavinder, 'two')
    slice = lavinder.test_window('slice')
    assert_focused(lavinder, 'slice')
    assert_focus_path(lavinder, 'slice')
    lavinder.test_window('three')
    assert_focus_path(lavinder, 'two', 'one', 'slice', 'three')
    lavinder.kill_window(two)
    assert_focus_path(lavinder, 'one', 'slice', 'three')
    lavinder.kill_window(slice)
    assert_focus_path(lavinder, 'one', 'three')
    slice = lavinder.test_window('slice')
    assert_focus_path(lavinder, 'three', 'one', 'slice')


@slice_config
def test_all_slices(lavinder):
    lavinder.test_window('slice')  # left
    assert_dimensions(lavinder, 0, 0, 200, 600)
    lavinder.c.next_layout()  # right
    assert_dimensions(lavinder, 600, 0, 200, 600)
    lavinder.c.next_layout()  # top
    assert_dimensions(lavinder, 0, 0, 800, 200)
    lavinder.c.next_layout()  # bottom
    assert_dimensions(lavinder, 0, 400, 800, 200)
    lavinder.c.next_layout()  # left again
    lavinder.test_window('one')
    assert_dimensions(lavinder, 200, 0, 600, 600)
    lavinder.c.next_layout()  # right
    assert_dimensions(lavinder, 0, 0, 600, 600)
    lavinder.c.next_layout()  # top
    assert_dimensions(lavinder, 0, 200, 800, 400)
    lavinder.c.next_layout()  # bottom
    assert_dimensions(lavinder, 0, 0, 800, 400)


@slice_config
def test_command_propagation(lavinder):
    lavinder.test_window('slice')
    lavinder.test_window('one')
    lavinder.test_window('two')
    info = lavinder.c.layout.info()
    assert info['name'] == 'slice', info['name']
    org_height = lavinder.c.window.info()['height']
    lavinder.c.layout.toggle_split()
    assert lavinder.c.window.info()['height'] != org_height
