# Copyright (c) 2011 Florian Mounier
# Copyright (c) 2012, 2014 Tycho Andersen
# Copyright (c) 2013 Craig Barnes
# Copyright (c) 2014 Sean Vig
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

import liblavinder
import liblavinder.confreader
import liblavinder.config
import liblavinder.layout
import liblavinder.bar
import liblavinder.widget


class CallConfig:
    keys = [
        liblavinder.config.Key(
            ["control"], "j",
            liblavinder.command._Call([("layout", None)], "down")
        ),
        liblavinder.config.Key(
            ["control"], "k",
            liblavinder.command._Call([("layout", None)], "up"),
        ),
    ]
    mouse = []
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
    ]
    layouts = [
        liblavinder.layout.Stack(num_stacks=1),
        liblavinder.layout.Max(),
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen(
            bottom=liblavinder.bar.Bar(
                [
                    liblavinder.widget.GroupBox(),
                ],
                20
            ),
        )
    ]
    main = None
    auto_fullscreen = True


call_config = pytest.mark.parametrize("lavinder", [CallConfig], indirect=True)


@call_config
def test_layout_filter(lavinder):
    lavinder.test_window("one")
    lavinder.test_window("two")
    assert lavinder.c.groups()["a"]["focus"] == "two"
    lavinder.c.simulate_keypress(["control"], "j")
    assert lavinder.c.groups()["a"]["focus"] == "one"
    lavinder.c.simulate_keypress(["control"], "k")
    assert lavinder.c.groups()["a"]["focus"] == "two"


class TestCommands(liblavinder.command.CommandObject):
    @staticmethod
    def cmd_one():
        pass

    def cmd_one_self(self):
        pass

    def cmd_two(self, a):
        pass

    def cmd_three(self, a, b=99):
        pass

    def _items(self, name):
        return None

    def _select(self, name, sel):
        return None


def test_doc():
    c = TestCommands()
    assert "one()" in c.cmd_doc("one")
    assert "one_self()" in c.cmd_doc("one_self")
    assert "two(a)" in c.cmd_doc("two")
    assert "three(a, b=99)" in c.cmd_doc("three")


def test_commands():
    c = TestCommands()
    assert len(c.cmd_commands()) == 9


def test_command():
    c = TestCommands()
    assert c.command("one")
    assert not c.command("nonexistent")


class ConcreteCmdRoot(liblavinder.command._CommandRoot):
    def call(self, *args):
        return args

    def _items(self, name):
        return None

    def _select(self, name, sel):
        return None


def test_selectors():
    c = ConcreteCmdRoot()

    s = c.layout.screen.info
    assert s.selectors == [('layout', None), ('screen', None)]

    assert isinstance(c.info, liblavinder.command._Command)

    g = c.group
    assert isinstance(g, liblavinder.command._TGroup)
    assert g.myselector is None

    g = c.group["one"]
    assert isinstance(g, liblavinder.command._TGroup)
    assert g.myselector == "one"

    cmd = c.group["one"].foo
    assert cmd.name == "foo"
    assert cmd.selectors == [('group', 'one')]

    g = c.group["two"].layout["three"].screen
    assert g.selectors == [('group', 'two'), ('layout', 'three')]

    g = c.one
    assert g.selectors == []


class ServerConfig:
    auto_fullscreen = True
    keys = []
    mouse = []
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
        liblavinder.config.Group("c"),
    ]
    layouts = [
        liblavinder.layout.Stack(num_stacks=1),
        liblavinder.layout.Stack(num_stacks=2),
        liblavinder.layout.Stack(num_stacks=3),
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen(
            bottom=liblavinder.bar.Bar(
                [
                    liblavinder.widget.TextBox(name="one"),
                ],
                20
            ),
        ),
        liblavinder.config.Screen(
            bottom=liblavinder.bar.Bar(
                [
                    liblavinder.widget.TextBox(name="two"),
                ],
                20
            ),
        )
    ]
    main = None


server_config = pytest.mark.parametrize("lavinder", [ServerConfig], indirect=True)


@server_config
def test_cmd_commands(lavinder):
    assert lavinder.c.commands()
    assert lavinder.c.layout.commands()
    assert lavinder.c.screen.bar["bottom"].commands()


@server_config
def test_call_unknown(lavinder):
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.nonexistent()

    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.layout.nonexistent()


@server_config
def test_items_lavinder(lavinder):
    v = lavinder.c.items("group")
    assert v[0]
    assert sorted(v[1]) == ["a", "b", "c"]

    assert lavinder.c.items("layout") == (True, [0, 1, 2])

    v = lavinder.c.items("widget")
    assert not v[0]
    assert sorted(v[1]) == ['one', 'two']

    assert lavinder.c.items("bar") == (False, ["bottom"])
    t, lst = lavinder.c.items("window")
    assert t
    assert len(lst) == 2
    assert lavinder.c.window[lst[0]]
    assert lavinder.c.items("screen") == (True, [0, 1])


@server_config
def test_select_lavinder(lavinder):
    assert lavinder.c.foo.selectors == []
    assert lavinder.c.layout.info()["group"] == "a"
    assert len(lavinder.c.layout.info()["stacks"]) == 1
    assert len(lavinder.c.layout[2].info()["stacks"]) == 3
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.layout[99].info()

    assert lavinder.c.group.info()["name"] == "a"
    assert lavinder.c.group["c"].info()["name"] == "c"
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.group["nonexistent"].info()

    assert lavinder.c.widget["one"].info()["name"] == "one"
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.widget.info()

    assert lavinder.c.bar["bottom"].info()["position"] == "bottom"

    lavinder.test_window("one")
    wid = lavinder.c.window.info()["id"]
    assert lavinder.c.window[wid].info()["id"] == wid

    assert lavinder.c.screen.info()["index"] == 0
    assert lavinder.c.screen[1].info()["index"] == 1
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.screen[22].info()
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.screen["foo"].info()


@server_config
def test_items_group(lavinder):
    g = lavinder.c.group
    assert g.items("layout") == (True, [0, 1, 2])

    lavinder.test_window("test")
    wid = lavinder.c.window.info()["id"]
    assert g.items("window") == (True, [wid])

    assert g.items("screen") == (True, None)


@server_config
def test_select_group(lavinder):
    g = lavinder.c.group
    assert g.layout.info()["group"] == "a"
    assert len(g.layout.info()["stacks"]) == 1
    assert len(g.layout[2].info()["stacks"]) == 3

    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.group.window.info()
    lavinder.test_window("test")
    wid = lavinder.c.window.info()["id"]

    assert g.window.info()["id"] == wid
    assert g.window[wid].info()["id"] == wid
    with pytest.raises(liblavinder.command.CommandError):
        g.window["foo"].info()

    assert g.screen.info()["index"] == 0
    assert g["b"].screen.info()["index"] == 1
    with pytest.raises(liblavinder.command.CommandError):
        g["b"].screen[0].info()


@server_config
def test_items_screen(lavinder):
    s = lavinder.c.screen
    assert s.items("layout") == (True, [0, 1, 2])

    lavinder.test_window("test")
    wid = lavinder.c.window.info()["id"]
    assert s.items("window") == (True, [wid])

    assert s.items("bar") == (False, ["bottom"])


@server_config
def test_select_screen(lavinder):
    s = lavinder.c.screen
    assert s.layout.info()["group"] == "a"
    assert len(s.layout.info()["stacks"]) == 1
    assert len(s.layout[2].info()["stacks"]) == 3

    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.window.info()
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.window[2].info()
    lavinder.test_window("test")
    wid = lavinder.c.window.info()["id"]
    assert s.window.info()["id"] == wid
    assert s.window[wid].info()["id"] == wid

    with pytest.raises(liblavinder.command.CommandError):
        s.bar.info()
    with pytest.raises(liblavinder.command.CommandError):
        s.bar["top"].info()
    assert s.bar["bottom"].info()["position"] == "bottom"


@server_config
def test_items_bar(lavinder):
    assert lavinder.c.bar["bottom"].items("screen") == (True, None)


@server_config
def test_select_bar(lavinder):
    assert lavinder.c.screen[1].bar["bottom"].screen.info()["index"] == 1
    b = lavinder.c.bar
    assert b["bottom"].screen.info()["index"] == 0
    with pytest.raises(liblavinder.command.CommandError):
        b.screen.info()


@server_config
def test_items_layout(lavinder):
    assert lavinder.c.layout.items("screen") == (True, None)
    assert lavinder.c.layout.items("group") == (True, None)


@server_config
def test_select_layout(lavinder):
    assert lavinder.c.layout.screen.info()["index"] == 0
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.layout.screen[0].info()

    assert lavinder.c.layout.group.info()["name"] == "a"
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.layout.group["a"].info()


@server_config
def test_items_window(lavinder):
    lavinder.test_window("test")
    lavinder.c.window.info()["id"]

    assert lavinder.c.window.items("group") == (True, None)
    assert lavinder.c.window.items("layout") == (True, [0, 1, 2])
    assert lavinder.c.window.items("screen") == (True, None)


@server_config
def test_select_window(lavinder):
    lavinder.test_window("test")
    lavinder.c.window.info()["id"]

    assert lavinder.c.window.group.info()["name"] == "a"
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.window.group["a"].info()

    assert len(lavinder.c.window.layout.info()["stacks"]) == 1
    assert len(lavinder.c.window.layout[1].info()["stacks"]) == 2

    assert lavinder.c.window.screen.info()["index"] == 0
    with pytest.raises(liblavinder.command.CommandError):
        lavinder.c.window.screen[0].info()


@server_config
def test_items_widget(lavinder):
    assert lavinder.c.widget["one"].items("bar") == (True, None)


@server_config
def test_select_widget(lavinder):
    w = lavinder.c.widget["one"]
    assert w.bar.info()["position"] == "bottom"
    with pytest.raises(liblavinder.command.CommandError):
        w.bar["bottom"].info()
