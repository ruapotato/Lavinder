# Copyright (c) 2011 Florian Mounier
# Copyright (c) 2011 Anshuman Bhaduri
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2013 xarvh
# Copyright (c) 2013 Craig Barnes
# Copyright (c) 2014 Sean Vig
# Copyright (c) 2014 Adi Sieker
# Copyright (c) 2014 Sebastien Blot
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

import logging
import pytest
import subprocess
import time

import liblavinder
import liblavinder.layout
import liblavinder.bar
import liblavinder.command
import liblavinder.widget
import liblavinder.core.manager
import liblavinder.config
import liblavinder.hook
import liblavinder.confreader


from .conftest import whereis, BareConfig, no_xinerama, Retry


class ManagerConfig:
    auto_fullscreen = True
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
        liblavinder.config.Group("c"),
        liblavinder.config.Group("d")
    ]
    layouts = [
        liblavinder.layout.stack.Stack(num_stacks=1),
        liblavinder.layout.stack.Stack(num_stacks=2),
        liblavinder.layout.tile.Tile(ratio=0.5),
        liblavinder.layout.max.Max()
    ]
    floating_layout = liblavinder.layout.floating.Floating(
        float_rules=[dict(wmclass="xclock")])
    keys = [
        liblavinder.config.Key(
            ["control"],
            "k",
            liblavinder.command._Call([("layout", None)], "up")
        ),
        liblavinder.config.Key(
            ["control"],
            "j",
            liblavinder.command._Call([("layout", None)], "down")
        ),
    ]
    mouse = []
    screens = [liblavinder.config.Screen(
        bottom=liblavinder.bar.Bar(
            [
                liblavinder.widget.GroupBox(),
            ],
            20
        ),
    )]
    main = None
    follow_mouse_focus = True


manager_config = pytest.mark.parametrize("lavinder", [ManagerConfig], indirect=True)


@manager_config
def test_screen_dim(lavinder):
    # self.c.restart()

    lavinder.test_xclock()
    assert lavinder.c.screen.info()["index"] == 0
    assert lavinder.c.screen.info()["x"] == 0
    assert lavinder.c.screen.info()["width"] == 800
    assert lavinder.c.group.info()["name"] == 'a'
    assert lavinder.c.group.info()["focus"] == 'xclock'

    lavinder.c.to_screen(1)
    lavinder.test_xeyes()
    assert lavinder.c.screen.info()["index"] == 1
    assert lavinder.c.screen.info()["x"] == 800
    assert lavinder.c.screen.info()["width"] == 640
    assert lavinder.c.group.info()["name"] == 'b'
    assert lavinder.c.group.info()["focus"] == 'xeyes'

    lavinder.c.to_screen(0)
    assert lavinder.c.screen.info()["index"] == 0
    assert lavinder.c.screen.info()["x"] == 0
    assert lavinder.c.screen.info()["width"] == 800
    assert lavinder.c.group.info()["name"] == 'a'
    assert lavinder.c.group.info()["focus"] == 'xclock'


@pytest.mark.parametrize("xephyr", [{"xoffset": 0}], indirect=True)
@manager_config
def test_clone_dim(lavinder):
    self = lavinder

    self.test_xclock()
    assert self.c.screen.info()["index"] == 0
    assert self.c.screen.info()["x"] == 0
    assert self.c.screen.info()["width"] == 800
    assert self.c.group.info()["name"] == 'a'
    assert self.c.group.info()["focus"] == 'xclock'

    assert len(self.c.screens()) == 1


@manager_config
def test_to_screen(lavinder):
    self = lavinder

    assert self.c.screen.info()["index"] == 0
    self.c.to_screen(1)
    assert self.c.screen.info()["index"] == 1
    self.test_window("one")
    self.c.to_screen(0)
    self.test_window("two")

    ga = self.c.groups()["a"]
    assert ga["windows"] == ["two"]

    gb = self.c.groups()["b"]
    assert gb["windows"] == ["one"]

    assert self.c.window.info()["name"] == "two"
    self.c.next_screen()
    assert self.c.window.info()["name"] == "one"
    self.c.next_screen()
    assert self.c.window.info()["name"] == "two"
    self.c.prev_screen()
    assert self.c.window.info()["name"] == "one"


@manager_config
def test_togroup(lavinder):
    self = lavinder

    self.test_window("one")
    with pytest.raises(liblavinder.command.CommandError):
        self.c.window.togroup("nonexistent")
    assert self.c.groups()["a"]["focus"] == "one"
    self.c.window.togroup("a")
    assert self.c.groups()["a"]["focus"] == "one"
    self.c.window.togroup("b")
    assert self.c.groups()["b"]["focus"] == "one"
    assert self.c.groups()["a"]["focus"] is None
    self.c.to_screen(1)
    self.c.window.togroup("c")
    assert self.c.groups()["c"]["focus"] == "one"


@manager_config
def test_resize(lavinder):
    self = lavinder
    self.c.screen[0].resize(x=10, y=10, w=100, h=100)

    @Retry(ignore_exceptions=(AssertionError), fail_msg="Screen didn't resize")
    def run():
        d = self.c.screen[0].info()
        assert d['width'] == 100
        assert d['height'] == 100
        return d
    d = run()
    assert d['x'] == d['y'] == 10


@no_xinerama
def test_minimal(lavinder):
    assert lavinder.c.status() == "OK"


@manager_config
@no_xinerama
def test_events(lavinder):
    assert lavinder.c.status() == "OK"


# FIXME: failing test disabled. For some reason we don't seem
# to have a keymap in Xnest or Xephyr 99% of the time.
@manager_config
@no_xinerama
def test_keypress(lavinder):
    self = lavinder

    self.test_window("one")
    self.test_window("two")
    with pytest.raises(liblavinder.command.CommandError):
        self.c.simulate_keypress(["unknown"], "j")
    assert self.c.groups()["a"]["focus"] == "two"
    self.c.simulate_keypress(["control"], "j")
    assert self.c.groups()["a"]["focus"] == "one"


@manager_config
@no_xinerama
def test_spawn(lavinder):
    # Spawn something with a pid greater than init's
    assert int(lavinder.c.spawn("true")) > 1


@manager_config
@no_xinerama
def test_spawn_list(lavinder):
    # Spawn something with a pid greater than init's
    assert int(lavinder.c.spawn(["echo", "true"])) > 1


@Retry(ignore_exceptions=(AssertionError,), fail_msg='Window did not die!')
def assert_window_died(client, window_info):
    client.sync()
    wid = window_info['id']
    assert wid not in set([x['id'] for x in client.windows()])


@manager_config
@no_xinerama
def test_kill_window(lavinder):
    lavinder.test_window("one")
    lavinder.testwindows = []
    window_info = lavinder.c.window.info()
    lavinder.c.window[window_info["id"]].kill()
    assert_window_died(lavinder.c, window_info)


@manager_config
@no_xinerama
def test_kill_other(lavinder):
    self = lavinder

    self.c.group.setlayout("tile")
    one = self.test_window("one")
    assert self.c.window.info()["width"] == 798
    window_one_info = self.c.window.info()
    assert self.c.window.info()["height"] == 578
    two = self.test_window("two")
    assert self.c.window.info()["name"] == "two"
    assert self.c.window.info()["width"] == 398
    assert self.c.window.info()["height"] == 578
    assert len(self.c.windows()) == 2

    self.kill_window(one)
    assert_window_died(self.c, window_one_info)

    assert self.c.window.info()["name"] == "two"
    assert self.c.window.info()["width"] == 798
    assert self.c.window.info()["height"] == 578
    self.kill_window(two)


@manager_config
@no_xinerama
def test_regression_groupswitch(lavinder):
    self = lavinder

    self.c.group["c"].toscreen()
    self.c.group["d"].toscreen()
    assert self.c.groups()["c"]["screen"] is None


@manager_config
@no_xinerama
def test_next_layout(lavinder):
    self = lavinder

    self.test_window("one")
    self.test_window("two")
    assert len(self.c.layout.info()["stacks"]) == 1
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.c.next_layout()
    self.c.next_layout()
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 1


@manager_config
@no_xinerama
def test_setlayout(lavinder):
    self = lavinder

    assert not self.c.layout.info()["name"] == "max"
    self.c.group.setlayout("max")
    assert self.c.layout.info()["name"] == "max"


@manager_config
@no_xinerama
def test_adddelgroup(lavinder):
    self = lavinder

    self.test_window("one")
    self.c.addgroup("dummygroup")
    self.c.addgroup("testgroup")
    assert "testgroup" in self.c.groups().keys()

    self.c.window.togroup("testgroup")
    self.c.delgroup("testgroup")
    assert "testgroup" not in self.c.groups().keys()
    # Assert that the test window is still a member of some group.
    assert sum(len(i["windows"]) for i in self.c.groups().values())

    for i in list(self.c.groups().keys())[:-1]:
        self.c.delgroup(i)
    with pytest.raises(liblavinder.command.CommandException):
        self.c.delgroup(list(self.c.groups().keys())[0])

    # Assert that setting layout via cmd_addgroup works
    self.c.addgroup("testgroup2", layout='max')
    assert self.c.groups()["testgroup2"]['layout'] == 'max'


@manager_config
@no_xinerama
def test_delgroup(lavinder):
    self = lavinder

    self.test_window("one")
    for i in ['a', 'd', 'c']:
        self.c.delgroup(i)
    with pytest.raises(liblavinder.command.CommandException):
        self.c.delgroup('b')


@manager_config
@no_xinerama
def test_nextprevgroup(lavinder):
    self = lavinder

    start = self.c.group.info()["name"]
    ret = self.c.screen.next_group()
    assert self.c.group.info()["name"] != start
    assert self.c.group.info()["name"] == ret
    ret = self.c.screen.prev_group()
    assert self.c.group.info()["name"] == start


@manager_config
@no_xinerama
def test_toggle_group(lavinder):
    self = lavinder

    self.c.group["a"].toscreen()
    self.c.group["b"].toscreen()
    self.c.screen.toggle_group("c")
    assert self.c.group.info()["name"] == "c"
    self.c.screen.toggle_group("c")
    assert self.c.group.info()["name"] == "b"
    self.c.screen.toggle_group()
    assert self.c.group.info()["name"] == "c"


@manager_config
@no_xinerama
def test_inspect_xeyes(lavinder):
    self = lavinder

    self.test_xeyes()
    assert self.c.window.inspect()


@manager_config
@no_xinerama
def test_inspect_xclock(lavinder):
    self = lavinder

    self.test_xclock()
    assert self.c.window.inspect()["wm_class"]


@manager_config
@no_xinerama
def test_static(lavinder):
    self = lavinder

    self.test_xeyes()
    self.test_window("one")
    self.c.window[self.c.window.info()["id"]].static(0, 0, 0, 100, 100)


@manager_config
@no_xinerama
def test_match(lavinder):
    self = lavinder

    self.test_xeyes()
    assert self.c.window.match(wname="xeyes")
    assert not self.c.window.match(wname="nonexistent")


@manager_config
@no_xinerama
def test_default_float(lavinder):
    self = lavinder

    # change to 2 col stack
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.test_xclock()

    assert self.c.group.info()['focus'] == 'xclock'
    assert self.c.window.info()['width'] == 164
    assert self.c.window.info()['height'] == 164
    assert self.c.window.info()['x'] == 318
    assert self.c.window.info()['y'] == 208
    assert self.c.window.info()['floating'] is True

    self.c.window.move_floating(10, 20, 42, 42)
    assert self.c.window.info()['width'] == 164
    assert self.c.window.info()['height'] == 164
    assert self.c.window.info()['x'] == 328
    assert self.c.window.info()['y'] == 228
    assert self.c.window.info()['floating'] is True

    self.c.window.set_position_floating(10, 20, 42, 42)
    assert self.c.window.info()['width'] == 164
    assert self.c.window.info()['height'] == 164
    assert self.c.window.info()['x'] == 10
    assert self.c.window.info()['y'] == 20
    assert self.c.window.info()['floating'] is True


@manager_config
@no_xinerama
def test_last_float_size(lavinder):
    """
    When you re-float something it would be preferable to have it use the previous float size
    """
    self = lavinder

    self.test_xeyes()
    assert self.c.window.info()['name'] == 'xeyes'
    assert self.c.window.info()['width'] == 798
    assert self.c.window.info()['height'] == 578
    # float and it moves
    self.c.window.toggle_floating()
    assert self.c.window.info()['width'] == 150
    assert self.c.window.info()['height'] == 100
    # resize
    self.c.window.set_size_floating(50, 90, 42, 42)
    assert self.c.window.info()['width'] == 50
    assert self.c.window.info()['height'] == 90
    # back to not floating
    self.c.window.toggle_floating()
    assert self.c.window.info()['width'] == 798
    assert self.c.window.info()['height'] == 578
    # float again, should use last float size
    self.c.window.toggle_floating()
    assert self.c.window.info()['width'] == 50
    assert self.c.window.info()['height'] == 90

    # make sure it works through min and max
    self.c.window.toggle_maximize()
    self.c.window.toggle_minimize()
    self.c.window.toggle_minimize()
    self.c.window.toggle_floating()
    assert self.c.window.info()['width'] == 50
    assert self.c.window.info()['height'] == 90


@manager_config
@no_xinerama
def test_float_max_min_combo(lavinder):
    self = lavinder

    # change to 2 col stack
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.test_xcalc()
    self.test_xeyes()

    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0
    assert self.c.window.info()['floating'] is False

    self.c.window.toggle_maximize()
    assert self.c.window.info()['floating'] is True
    assert self.c.window.info()['maximized'] is True
    assert self.c.window.info()['width'] == 800
    assert self.c.window.info()['height'] == 580
    assert self.c.window.info()['x'] == 0
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_minimize()
    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['floating'] is True
    assert self.c.window.info()['minimized'] is True
    assert self.c.window.info()['width'] == 800
    assert self.c.window.info()['height'] == 580
    assert self.c.window.info()['x'] == 0
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_floating()
    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['floating'] is False
    assert self.c.window.info()['minimized'] is False
    assert self.c.window.info()['maximized'] is False
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0


@manager_config
@no_xinerama
def test_toggle_fullscreen(lavinder):
    self = lavinder

    # change to 2 col stack
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.test_xcalc()
    self.test_xeyes()

    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['float_info'] == {
        'y': 0, 'x': 400, 'width': 150, 'height': 100}
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_fullscreen()
    assert self.c.window.info()['floating'] is True
    assert self.c.window.info()['maximized'] is False
    assert self.c.window.info()['fullscreen'] is True
    assert self.c.window.info()['width'] == 800
    assert self.c.window.info()['height'] == 600
    assert self.c.window.info()['x'] == 0
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_fullscreen()
    assert self.c.window.info()['floating'] is False
    assert self.c.window.info()['maximized'] is False
    assert self.c.window.info()['fullscreen'] is False
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0


@manager_config
@no_xinerama
def test_toggle_max(lavinder):
    self = lavinder

    # change to 2 col stack
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.test_xcalc()
    self.test_xeyes()

    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['float_info'] == {
        'y': 0, 'x': 400, 'width': 150, 'height': 100}
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_maximize()
    assert self.c.window.info()['floating'] is True
    assert self.c.window.info()['maximized'] is True
    assert self.c.window.info()['width'] == 800
    assert self.c.window.info()['height'] == 580
    assert self.c.window.info()['x'] == 0
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_maximize()
    assert self.c.window.info()['floating'] is False
    assert self.c.window.info()['maximized'] is False
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0


@manager_config
@no_xinerama
def test_toggle_min(lavinder):
    self = lavinder

    # change to 2 col stack
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.test_xcalc()
    self.test_xeyes()

    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['float_info'] == {
        'y': 0, 'x': 400, 'width': 150, 'height': 100}
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_minimize()
    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['floating'] is True
    assert self.c.window.info()['minimized'] is True
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0

    self.c.window.toggle_minimize()
    assert self.c.group.info()['focus'] == 'xeyes'
    assert self.c.window.info()['floating'] is False
    assert self.c.window.info()['minimized'] is False
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['x'] == 400
    assert self.c.window.info()['y'] == 0


@manager_config
@no_xinerama
def test_toggle_floating(lavinder):
    self = lavinder

    self.test_xeyes()
    assert self.c.window.info()['floating'] is False
    self.c.window.toggle_floating()
    assert self.c.window.info()['floating'] is True
    self.c.window.toggle_floating()
    assert self.c.window.info()['floating'] is False
    self.c.window.toggle_floating()
    assert self.c.window.info()['floating'] is True

    # change layout (should still be floating)
    self.c.next_layout()
    assert self.c.window.info()['floating'] is True


@manager_config
@no_xinerama
def test_floating_focus(lavinder):
    self = lavinder

    # change to 2 col stack
    self.c.next_layout()
    assert len(self.c.layout.info()["stacks"]) == 2
    self.test_xcalc()
    self.test_xeyes()
    # self.test_window("one")
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    self.c.window.toggle_floating()
    self.c.window.move_floating(10, 20, 42, 42)
    assert self.c.window.info()['name'] == 'xeyes'
    assert self.c.group.info()['focus'] == 'xeyes'
    # check what stack thinks is focus
    assert [x['current'] for x in self.c.layout.info()['stacks']] == [0, 0]

    # change focus to xcalc
    self.c.group.next_window()
    assert self.c.window.info()['width'] == 398
    assert self.c.window.info()['height'] == 578
    assert self.c.window.info()['name'] != 'xeyes'
    assert self.c.group.info()['focus'] != 'xeyes'
    # check what stack thinks is focus
    # check what stack thinks is focus
    assert [x['current'] for x in self.c.layout.info()['stacks']] == [0, 0]

    # focus back to xeyes
    self.c.group.next_window()
    assert self.c.window.info()['name'] == 'xeyes'
    # check what stack thinks is focus
    assert [x['current'] for x in self.c.layout.info()['stacks']] == [0, 0]

    # now focusing via layout is borked (won't go to float)
    self.c.layout.up()
    assert self.c.window.info()['name'] != 'xeyes'
    self.c.layout.up()
    assert self.c.window.info()['name'] != 'xeyes'
    # check what stack thinks is focus
    assert [x['current'] for x in self.c.layout.info()['stacks']] == [0, 0]

    # focus back to xeyes
    self.c.group.next_window()
    assert self.c.window.info()['name'] == 'xeyes'
    # check what stack thinks is focus
    assert [x['current'] for x in self.c.layout.info()['stacks']] == [0, 0]


@manager_config
@no_xinerama
def test_move_floating(lavinder):
    self = lavinder

    self.test_xeyes()
    # self.test_window("one")
    assert self.c.window.info()['width'] == 798
    assert self.c.window.info()['height'] == 578

    assert self.c.window.info()['x'] == 0
    assert self.c.window.info()['y'] == 0
    self.c.window.toggle_floating()
    assert self.c.window.info()['floating'] is True

    self.c.window.move_floating(10, 20, 42, 42)
    assert self.c.window.info()['width'] == 150
    assert self.c.window.info()['height'] == 100
    assert self.c.window.info()['x'] == 10
    assert self.c.window.info()['y'] == 20

    self.c.window.set_size_floating(50, 90, 42, 42)
    assert self.c.window.info()['width'] == 50
    assert self.c.window.info()['height'] == 90
    assert self.c.window.info()['x'] == 10
    assert self.c.window.info()['y'] == 20

    self.c.window.resize_floating(10, 20, 42, 42)
    assert self.c.window.info()['width'] == 60
    assert self.c.window.info()['height'] == 110
    assert self.c.window.info()['x'] == 10
    assert self.c.window.info()['y'] == 20

    self.c.window.set_size_floating(10, 20, 42, 42)
    assert self.c.window.info()['width'] == 10
    assert self.c.window.info()['height'] == 20
    assert self.c.window.info()['x'] == 10
    assert self.c.window.info()['y'] == 20

    # change layout (x, y should be same)
    self.c.next_layout()
    assert self.c.window.info()['width'] == 10
    assert self.c.window.info()['height'] == 20
    assert self.c.window.info()['x'] == 10
    assert self.c.window.info()['y'] == 20


@manager_config
@no_xinerama
def test_screens(lavinder):
    self = lavinder

    assert len(self.c.screens())


@manager_config
@no_xinerama
def test_rotate(lavinder):
    self = lavinder

    self.test_window("one")
    s = self.c.screens()[0]
    height, width = s["height"], s["width"]
    subprocess.call(
        [
            "xrandr",
            "--output", "default",
            "-display", self.display,
            "--rotate", "left"
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    @Retry(ignore_exceptions=(AssertionError,), fail_msg="Screen did not rotate")
    def run():
        s = self.c.screens()[0]
        assert s['width'] == height
        assert s['height'] == width
        return True
    run()


# TODO: see note on test_resize
@manager_config
@no_xinerama
def test_resize_(lavinder):
    self = lavinder

    self.test_window("one")
    subprocess.call(
        [
            "xrandr",
            "-s", "480x640",
            "-display", self.display
        ]
    )

    @Retry(ignore_exceptions=(AssertionError,), fail_msg="Screen did not resize")
    def run():
        d = self.c.screen.info()
        assert d['width'] == 480
        assert d['height'] == 640
        return True
    run()


@manager_config
@no_xinerama
def test_focus_stays_on_layout_switch(lavinder):
    lavinder.test_window("one")
    lavinder.test_window("two")

    # switch to a double stack layout
    lavinder.c.next_layout()

    # focus on a different window than the default
    lavinder.c.layout.next()

    # toggle the layout
    lavinder.c.next_layout()
    lavinder.c.prev_layout()

    assert lavinder.c.window.info()['name'] == 'one'


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_xeyes(lavinder):
    lavinder.test_xeyes()


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_xcalc(lavinder):
    lavinder.test_xcalc()


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_xcalc_kill_window(lavinder):
    self = lavinder

    self.test_xcalc()
    window_info = self.c.window.info()
    self.c.window.kill()
    assert_window_died(self.c, window_info)


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_map_request(lavinder):
    self = lavinder

    self.test_window("one")
    info = self.c.groups()["a"]
    assert "one" in info["windows"]
    assert info["focus"] == "one"

    self.test_window("two")
    info = self.c.groups()["a"]
    assert "two" in info["windows"]
    assert info["focus"] == "two"


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_unmap(lavinder):
    self = lavinder

    one = self.test_window("one")
    two = self.test_window("two")
    three = self.test_window("three")
    info = self.c.groups()["a"]
    assert info["focus"] == "three"

    assert len(self.c.windows()) == 3
    self.kill_window(three)

    assert len(self.c.windows()) == 2
    info = self.c.groups()["a"]
    assert info["focus"] == "two"

    self.kill_window(two)
    assert len(self.c.windows()) == 1
    info = self.c.groups()["a"]
    assert info["focus"] == "one"

    self.kill_window(one)
    assert len(self.c.windows()) == 0
    info = self.c.groups()["a"]
    assert info["focus"] is None


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_setgroup(lavinder):
    self = lavinder

    self.test_window("one")
    self.c.group["b"].toscreen()
    self.groupconsistency()
    if len(self.c.screens()) == 1:
        assert self.c.groups()["a"]["screen"] is None
    else:
        assert self.c.groups()["a"]["screen"] == 1
    assert self.c.groups()["b"]["screen"] == 0
    self.c.group["c"].toscreen()
    self.groupconsistency()
    assert self.c.groups()["c"]["screen"] == 0


@pytest.mark.parametrize("lavinder", [BareConfig, ManagerConfig], indirect=True)
@pytest.mark.parametrize("xephyr", [{"xinerama": True}, {"xinerama": False}], indirect=True)
def test_unmap_noscreen(lavinder):
    self = lavinder
    self.test_window("one")
    pid = self.test_window("two")
    assert len(self.c.windows()) == 2
    self.c.group["c"].toscreen()
    self.groupconsistency()
    self.c.status()
    assert len(self.c.windows()) == 2
    self.kill_window(pid)
    assert len(self.c.windows()) == 1
    assert self.c.groups()["a"]["focus"] == "one"


# def test_init():
#     with pytest.raises(liblavinder.core.manager.LavinderError):
#         liblavinder.config.Key([], "unknown", liblavinder.command._Call("base", None, "foo"))
#     with pytest.raises(liblavinder.core.manager.LavinderError):
#         liblavinder.config.Key(["unknown"], "x", liblavinder.command._Call("base", None, "foo"))


class TScreen(liblavinder.config.Screen):
    def set_group(self, x, save_prev=True):
        pass


def test_dx():
    s = TScreen(left=liblavinder.bar.Gap(10))
    s._configure(None, 0, 0, 0, 100, 100, None)
    assert s.dx == 10


def test_dwidth():
    s = TScreen(left=liblavinder.bar.Gap(10))
    s._configure(None, 0, 0, 0, 100, 100, None)
    assert s.dwidth == 90
    s.right = liblavinder.bar.Gap(10)
    assert s.dwidth == 80


def test_dy():
    s = TScreen(top=liblavinder.bar.Gap(10))
    s._configure(None, 0, 0, 0, 100, 100, None)
    assert s.dy == 10


def test_dheight():
    s = TScreen(top=liblavinder.bar.Gap(10))
    s._configure(None, 0, 0, 0, 100, 100, None)
    assert s.dheight == 90
    s.bottom = liblavinder.bar.Gap(10)
    assert s.dheight == 80


class _Config:
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
        liblavinder.config.Group("c"),
        liblavinder.config.Group("d")
    ]
    layouts = [
        liblavinder.layout.stack.Stack(num_stacks=1),
        liblavinder.layout.stack.Stack(num_stacks=2)
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    keys = [
        liblavinder.config.Key(
            ["control"],
            "k",
            liblavinder.command._Call([("layout", None)], "up")
        ),
        liblavinder.config.Key(
            ["control"],
            "j",
            liblavinder.command._Call([("layout", None)], "down")
        ),
    ]
    mouse = []
    screens = [liblavinder.config.Screen(
        bottom=liblavinder.bar.Bar(
            [
                liblavinder.widget.GroupBox(),
            ],
            20
        ),
    )]
    auto_fullscreen = True


class ClientNewStaticConfig(_Config):
    @staticmethod
    def main(c):
        def client_new(c):
            c.static(0)
        liblavinder.hook.subscribe.client_new(client_new)


clientnew_config = pytest.mark.parametrize("lavinder", [ClientNewStaticConfig], indirect=True)


@clientnew_config
def test_clientnew_config(lavinder):
    self = lavinder

    a = self.test_window("one")
    self.kill_window(a)


@pytest.mark.skipif(whereis("gkrellm") is None, reason="gkrellm not found")
@clientnew_config
def test_gkrellm(lavinder):
    lavinder.test_gkrellm()
    time.sleep(0.1)


class ToGroupConfig(_Config):
    @staticmethod
    def main(c):
        def client_new(c):
            c.togroup("d")
        liblavinder.hook.subscribe.client_new(client_new)


togroup_config = pytest.mark.parametrize("lavinder", [ToGroupConfig], indirect=True)


@togroup_config
def test_togroup_config(lavinder):
    lavinder.c.group["d"].toscreen()
    lavinder.c.group["a"].toscreen()
    a = lavinder.test_window("one")
    assert len(lavinder.c.group["d"].info()["windows"]) == 1
    lavinder.kill_window(a)


@manager_config
def test_color_pixel(lavinder):
    # test for #394
    lavinder.c.eval("self.color_pixel(\"ffffff\")")


@manager_config
def test_change_loglevel(lavinder):
    assert lavinder.c.loglevel() == logging.INFO
    assert lavinder.c.loglevelname() == 'INFO'
    lavinder.c.debug()
    assert lavinder.c.loglevel() == logging.DEBUG
    assert lavinder.c.loglevelname() == 'DEBUG'
    lavinder.c.info()
    assert lavinder.c.loglevel() == logging.INFO
    assert lavinder.c.loglevelname() == 'INFO'
    lavinder.c.warning()
    assert lavinder.c.loglevel() == logging.WARNING
    assert lavinder.c.loglevelname() == 'WARNING'
    lavinder.c.error()
    assert lavinder.c.loglevel() == logging.ERROR
    assert lavinder.c.loglevelname() == 'ERROR'
    lavinder.c.critical()
    assert lavinder.c.loglevel() == logging.CRITICAL
    assert lavinder.c.loglevelname() == 'CRITICAL'
