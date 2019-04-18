# Copyright (c) 2011 Florian Mounier
# Copyright (c) 2012 Tycho Andersen
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
import liblavinder.sh
import liblavinder.confreader
import liblavinder.layout
import liblavinder.config


class ShConfig:
    keys = []
    mouse = []
    groups = [
        liblavinder.config.Group("a"),
        liblavinder.config.Group("b"),
    ]
    layouts = [
        liblavinder.layout.Max(),
    ]
    floating_layout = liblavinder.layout.floating.Floating()
    screens = [
        liblavinder.config.Screen()
    ]
    main = None


sh_config = pytest.mark.parametrize("lavinder", [ShConfig], indirect=True)


@sh_config
def test_columnize(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    assert lavinder.sh.columnize(["one", "two"]) == "one  two"

    lavinder.sh.termwidth = 1
    assert lavinder.sh.columnize(["one", "two"], update_termwidth=False) == "one\ntwo"

    lavinder.sh.termwidth = 15
    v = lavinder.sh.columnize(["one", "two", "three", "four", "five"], update_termwidth=False)
    assert v == 'one    two  \nthree  four \nfive '


@sh_config
def test_ls(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    lavinder.sh.do_cd("layout")
    lavinder.sh.do_ls("")


@sh_config
def test_find_node(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    n = lavinder.sh._find_node(lavinder.sh.current, "layout")
    assert n.path == "layout"
    assert n.parent

    n = lavinder.sh._find_node(n, "0")
    assert n.path == "layout[0]"

    n = lavinder.sh._find_node(n, "..")
    assert n.path == "layout"

    n = lavinder.sh._find_node(n, "0", "..")
    assert n.path == "layout"

    n = lavinder.sh._find_node(n, "..", "layout", 0)
    assert n.path == "layout[0]"

    assert not lavinder.sh._find_node(n, "wibble")
    assert not lavinder.sh._find_node(n, "..", "0", "wibble")


@sh_config
def test_do_cd(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    assert lavinder.sh.do_cd("layout") == 'layout'
    assert lavinder.sh.do_cd("0/wibble") == 'No such path.'
    assert lavinder.sh.do_cd("0/") == 'layout[0]'


@sh_config
def test_call(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    assert lavinder.sh._call("status", []) == "OK"

    v = lavinder.sh._call("nonexistent", "")
    assert "No such command" in v

    v = lavinder.sh._call("status", "(((")
    assert "Syntax error" in v

    v = lavinder.sh._call("status", "(1)")
    assert "Command exception" in v


@sh_config
def test_complete(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    assert lavinder.sh._complete("c", "c") == [
        "cd",
        "commands",
        "critical",
    ]

    assert lavinder.sh._complete("cd l", "l") == ["layout/"]
    assert lavinder.sh._complete("cd layout/", "layout/") == [
        "layout/" + x for x in ["group", "window", "screen", "0"]
    ]
    assert lavinder.sh._complete("cd layout/", "layout/g") == ["layout/group/"]


@sh_config
def test_help(lavinder):
    lavinder.sh = liblavinder.sh.QSh(lavinder.c)
    assert lavinder.sh.do_help("nonexistent").startswith("No such command")
    assert lavinder.sh.do_help("help")
