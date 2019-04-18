# Copyright (c) 2011 Florian Mounier
# Copyright (c) 2012-2013 Craig Barnes
# Copyright (c) 2012 roger
# Copyright (c) 2012, 2014-2015 Tycho Andersen
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

import liblavinder.layout
import liblavinder.bar
import liblavinder.widget
import liblavinder.config
import liblavinder.confreader


class GBConfig:
    auto_fullscreen = True
    keys = []
    mouse = []
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("bb"),
        liblavinder.config.Group("ccc"),
        liblavinder.config.Group("dddd"),
        liblavinder.config.Group("Pppy")
    ]
    layouts = [liblavinder.layout.stack.Stack(num_stacks=1)]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen(
            top=liblavinder.bar.Bar(
                [
                    liblavinder.widget.CPUGraph(
                        width=liblavinder.bar.STRETCH,
                        type="linefill",
                        border_width=20,
                        margin_x=1,
                        margin_y=1
                    ),
                    liblavinder.widget.MemoryGraph(type="line"),
                    liblavinder.widget.SwapGraph(type="box"),
                    liblavinder.widget.TextBox(name="text",
                                               background="333333"),
                ],
                50,
            ),
            bottom=liblavinder.bar.Bar(
                [
                    liblavinder.widget.GroupBox(),
                    liblavinder.widget.AGroupBox(),
                    liblavinder.widget.Prompt(),
                    liblavinder.widget.WindowName(),
                    liblavinder.widget.Sep(),
                    liblavinder.widget.Clock(),
                ],
                50
            ),
            # TODO: Add vertical bars and test widgets that support them
        )
    ]
    main = None


gb_config = pytest.mark.parametrize("lavinder", [GBConfig], indirect=True)


def test_completion():
    c = liblavinder.widget.prompt.CommandCompleter(None, True)
    c.reset()
    c.lookup = [
        ("a", "x/a"),
        ("aa", "x/aa"),
    ]
    assert c.complete("a") == "a"
    assert c.actual() == "x/a"
    assert c.complete("a") == "aa"
    assert c.complete("a") == "a"

    c = liblavinder.widget.prompt.CommandCompleter(None)
    r = c.complete("l")
    assert c.actual().endswith(r)

    c.reset()
    assert c.complete("/bi") == "/bin/"
    c.reset()
    assert c.complete("/bin") != "/bin/"
    c.reset()
    assert c.complete("~") != "~"

    c.reset()
    s = "thisisatotallynonexistantpathforsure"
    assert c.complete(s) == s
    assert c.actual() == s
    c.reset()


@gb_config
def test_draw(lavinder):
    lavinder.test_window("one")
    b = lavinder.c.bar["bottom"].info()
    assert b["widgets"][0]["name"] == "groupbox"


@gb_config
def test_prompt(lavinder):
    assert lavinder.c.widget["prompt"].info()["width"] == 0
    lavinder.c.spawncmd(":")
    lavinder.c.widget["prompt"].fake_keypress("a")
    lavinder.c.widget["prompt"].fake_keypress("Tab")

    lavinder.c.spawncmd(":")
    lavinder.c.widget["prompt"].fake_keypress("slash")
    lavinder.c.widget["prompt"].fake_keypress("Tab")


@gb_config
def test_event(lavinder):
    lavinder.c.group["bb"].toscreen()


@gb_config
def test_textbox(lavinder):
    assert "text" in lavinder.c.list_widgets()
    s = "some text"
    lavinder.c.widget["text"].update(s)
    assert lavinder.c.widget["text"].get() == s
    s = "Aye, much longer string than the initial one"
    lavinder.c.widget["text"].update(s)
    assert lavinder.c.widget["text"].get() == s
    lavinder.c.group["Pppy"].toscreen()
    lavinder.c.widget["text"].set_font(fontsize=12)


@gb_config
def test_textbox_errors(lavinder):
    lavinder.c.widget["text"].update(None)
    lavinder.c.widget["text"].update("".join(chr(i) for i in range(255)))
    lavinder.c.widget["text"].update("V\xE2r\xE2na\xE7\xEE")
    lavinder.c.widget["text"].update("\ua000")


@gb_config
def test_groupbox_button_press(lavinder):
    lavinder.c.group["ccc"].toscreen()
    assert lavinder.c.groups()["a"]["screen"] is None
    lavinder.c.bar["bottom"].fake_button_press(0, "bottom", 10, 10, 1)
    assert lavinder.c.groups()["a"]["screen"] == 0


class GeomConf:
    auto_fullscreen = False
    main = None
    keys = []
    mouse = []
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
        liblavinder.config.Group("c"),
        liblavinder.config.Group("d")
    ]
    layouts = [liblavinder.layout.stack.Stack(num_stacks=1)]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen(
            top=liblavinder.bar.Bar([], 10),
            bottom=liblavinder.bar.Bar([], 10),
            left=liblavinder.bar.Bar([], 10),
            right=liblavinder.bar.Bar([], 10),
        )
    ]


geom_config = pytest.mark.parametrize("lavinder", [GeomConf], indirect=True)


class DBarH(liblavinder.bar.Bar):
    def __init__(self, widgets, size):
        liblavinder.bar.Bar.__init__(self, widgets, size)
        self.horizontal = True


class DBarV(liblavinder.bar.Bar):
    def __init__(self, widgets, size):
        liblavinder.bar.Bar.__init__(self, widgets, size)
        self.horizontal = False


class DWidget:
    def __init__(self, length, length_type):
        self.length, self.length_type = length, length_type


@geom_config
def test_geometry(lavinder):
    lavinder.test_xeyes()
    g = lavinder.c.screens()[0]["gaps"]
    assert g["top"] == (0, 0, 800, 10)
    assert g["bottom"] == (0, 590, 800, 10)
    assert g["left"] == (0, 10, 10, 580)
    assert g["right"] == (790, 10, 10, 580)
    assert len(lavinder.c.windows()) == 1
    geom = lavinder.c.windows()[0]
    assert geom["x"] == 10
    assert geom["y"] == 10
    assert geom["width"] == 778
    assert geom["height"] == 578
    internal = lavinder.c.internal_windows()
    assert len(internal) == 4
    wid = lavinder.c.bar["bottom"].info()["window"]
    assert lavinder.c.window[wid].inspect()


@geom_config
def test_resize(lavinder):
    def wd(l):
        return [i.length for i in l]

    def offx(l):
        return [i.offsetx for i in l]

    def offy(l):
        return [i.offsety for i in l]

    for DBar, off in ((DBarH, offx), (DBarV, offy)):  # noqa: N806
        b = DBar([], 100)

        dwidget_list = [
            DWidget(10, liblavinder.bar.CALCULATED),
            DWidget(None, liblavinder.bar.STRETCH),
            DWidget(None, liblavinder.bar.STRETCH),
            DWidget(10, liblavinder.bar.CALCULATED),
        ]
        b._resize(100, dwidget_list)
        assert wd(dwidget_list) == [10, 40, 40, 10]
        assert off(dwidget_list) == [0, 10, 50, 90]

        b._resize(101, dwidget_list)
        assert wd(dwidget_list) == [10, 40, 41, 10]
        assert off(dwidget_list) == [0, 10, 50, 91]

        dwidget_list = [
            DWidget(10, liblavinder.bar.CALCULATED)
        ]
        b._resize(100, dwidget_list)
        assert wd(dwidget_list) == [10]
        assert off(dwidget_list) == [0]

        dwidget_list = [
            DWidget(10, liblavinder.bar.CALCULATED),
            DWidget(None, liblavinder.bar.STRETCH)
        ]
        b._resize(100, dwidget_list)
        assert wd(dwidget_list) == [10, 90]
        assert off(dwidget_list) == [0, 10]

        dwidget_list = [
            DWidget(None, liblavinder.bar.STRETCH),
            DWidget(10, liblavinder.bar.CALCULATED),
        ]
        b._resize(100, dwidget_list)
        assert wd(dwidget_list) == [90, 10]
        assert off(dwidget_list) == [0, 90]

        dwidget_list = [
            DWidget(10, liblavinder.bar.CALCULATED),
            DWidget(None, liblavinder.bar.STRETCH),
            DWidget(10, liblavinder.bar.CALCULATED),
        ]
        b._resize(100, dwidget_list)
        assert wd(dwidget_list) == [10, 80, 10]
        assert off(dwidget_list) == [0, 10, 90]


class ExampleWidget(liblavinder.widget.base._Widget):
    orientations = liblavinder.widget.base.ORIENTATION_HORIZONTAL

    def __init__(self):
        liblavinder.widget.base._Widget.__init__(self, 10)

    def draw(self):
        pass


class IncompatibleWidgetConf:
    main = None
    keys = []
    mouse = []
    groups = [liblavinder.config.Group("a")]
    layouts = [liblavinder.layout.stack.Stack(num_stacks=1)]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen(
            left=liblavinder.bar.Bar(
                [
                    # This widget doesn't support vertical orientation
                    ExampleWidget(),
                ],
                10
            ),
        )
    ]


def test_incompatible_widget(lavinder_nospawn):
    config = IncompatibleWidgetConf

    # Ensure that adding a widget that doesn't support the orientation of the
    # bar raises ConfigError
    with pytest.raises(liblavinder.confreader.ConfigError):
        lavinder_nospawn.create_manager(config)


class MultiStretchConf:
    main = None
    keys = []
    mouse = []
    groups = [liblavinder.config.Group("a")]
    layouts = [liblavinder.layout.stack.Stack(num_stacks=1)]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen(
            top=liblavinder.bar.Bar(
                [
                    liblavinder.widget.Spacer(liblavinder.bar.STRETCH),
                    liblavinder.widget.Spacer(liblavinder.bar.STRETCH),
                ],
                10
            ),
        )
    ]


def test_multiple_stretches(lavinder_nospawn):
    config = MultiStretchConf

    # Ensure that adding two STRETCH widgets to the same bar raises ConfigError
    with pytest.raises(liblavinder.confreader.ConfigError):
        lavinder_nospawn.create_manager(config)


def test_basic(lavinder_nospawn):
    config = GeomConf
    config.screens = [
        liblavinder.config.Screen(
            bottom=liblavinder.bar.Bar(
                [
                    ExampleWidget(),
                    liblavinder.widget.Spacer(liblavinder.bar.STRETCH),
                    ExampleWidget()
                ],
                10
            )
        )
    ]

    lavinder_nospawn.start(config)

    i = lavinder_nospawn.c.bar["bottom"].info()
    assert i["widgets"][0]["offset"] == 0
    assert i["widgets"][1]["offset"] == 10
    assert i["widgets"][1]["width"] == 780
    assert i["widgets"][2]["offset"] == 790
    liblavinder.hook.clear()


def test_singlespacer(lavinder_nospawn):
    config = GeomConf
    config.screens = [
        liblavinder.config.Screen(
            bottom=liblavinder.bar.Bar(
                [
                    liblavinder.widget.Spacer(liblavinder.bar.STRETCH),
                ],
                10
            )
        )
    ]

    lavinder_nospawn.start(config)

    i = lavinder_nospawn.c.bar["bottom"].info()
    assert i["widgets"][0]["offset"] == 0
    assert i["widgets"][0]["width"] == 800
    liblavinder.hook.clear()


def test_nospacer(lavinder_nospawn):
    config = GeomConf
    config.screens = [
        liblavinder.config.Screen(
            bottom=liblavinder.bar.Bar(
                [
                    ExampleWidget(),
                    ExampleWidget()
                ],
                10
            )
        )
    ]

    lavinder_nospawn.start(config)

    i = lavinder_nospawn.c.bar["bottom"].info()
    assert i["widgets"][0]["offset"] == 0
    assert i["widgets"][1]["offset"] == 10
    liblavinder.hook.clear()
