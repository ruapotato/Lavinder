# Copyright (c) 2012, Tycho Andersen. All rights reserved.
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


class QtileState:
    """Represents the state of the lavinder object

    Primarily used for restoring state across restarts; any additional state
    which doesn't fit nicely into X atoms can go here.
    """
    def __init__(self, lavinder):
        # Note: window state is saved and restored via _NET_WM_STATE, so
        # the only thing we need to restore here is the layout and screen
        # configurations.
        self.groups = []
        self.screens = {}
        self.current_screen = 0

        for group in lavinder.groups:
            self.groups.append((group.name, group.layout.name, group.label))
        for index, screen in enumerate(lavinder.screens):
            self.screens[index] = screen.group.name
            if screen == lavinder.current_screen:
                self.current_screen = index

    def apply(self, lavinder):
        """
        Rearrange the windows in the specified Qtile object according to this
        QtileState.
        """
        for (group, layout, label) in self.groups:
            try:
                lavinder.groups_map[group].layout = layout
            except KeyError:
                lavinder.add_group(group, layout, label=label)

        for (screen, group) in self.screens.items():
            try:
                group = lavinder.groups_map[group]
                lavinder.screens[screen].set_group(group)
            except (KeyError, IndexError):
                pass  # group or screen missing

        lavinder.focus_screen(self.current_screen)
