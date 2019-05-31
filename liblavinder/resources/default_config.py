# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
# Copyright (c) 2019 David Hamner

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

from liblavinder.config import Key, Screen, Group, Drag, Click
from liblavinder.command import lazy
from liblavinder import layout, bar, widget, hook
import shutil
import sh


try:
    from typing import List  # noqa: F401
except ImportError:
    pass

# Misc settings
dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = False
bring_front_click = True
cursor_warp = False
auto_fullscreen = False
focus_on_window_activation = "smart"
debugging = True
critical_debug = True
volume_app = "mate-volume-control"
# We're lying here. Nobody uses this string besides java UI toolkits
# LG3D happens to be on java's whitelist.
wmname = "LG3D"

# colors
bar_color = (26, 0, 51)
#                   graph    border
net_graph_color = ['EBBA18', '785521']

# var init
zoom = 0
last_window_position = (0, 0)
windows_moved = (0, 0)
min_win_size = 25
last_drag = None
window_with_mouse = None
hot_corner_triggered = None
moving_win = None
open_new_menu = True
found_menu = False
menu_window = ""
WIN = "mod4"
ALT = "mod1"
CTRL = "control"
menu_cmd = "xterm "
# load janit if installed
if shutil.which('janit') is not None:
    menu_cmd = menu_cmd + shutil.which('janit')


# Called after lavinder starts managing a new client
@hook.subscribe.client_managed
def on_win_open(window):
    global open_new_menu
    global menu_window  # Janit menu
    if menu_window != "":
        # open new window over menu
        window.place(menu_window.x, menu_window.y, menu_window.width,
                     menu_window.height, 2, None)


@hook.subscribe.client_mouse_enter
def on_mouse_enter(window):
    global window_with_mouse
    window_with_mouse = window


def debug(error, new_line='\n', level=1):
    global debugging
    global critical_debug
    crit_bug = level > 1
    crit_bug = crit_bug and critical_debug

    if debugging or crit_bug:
        debug_log = open('/tmp/Debug.txt', 'a+')
        debug_log.write(str(error) + new_line)
        debug_log.close()


# zoom all windows out
def handle_mousewheel_down(lavinder, *args):
    global zoom

    mouse_x, mouse_y = lavinder.get_mouse_position()
    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)

        # blacklist the top Bar
        if win.group is None:
            continue

        topleft_point = (win.x, win.y)
        lowright_point = (int(win.x + win.width), int(win.y + win.height/2))

        zoom = zoom + 1

        topleft_change_x = (mouse_x - topleft_point[0]) * 0.1
        topleft_change_y = (mouse_y - topleft_point[1]) * 0.1

        lowright_change_x = (mouse_x - lowright_point[0]) * 0.1
        lowright_change_y = (mouse_y - lowright_point[1]) * 0.1

        topleft_point = (int(topleft_point[0] + topleft_change_x),
                         int(topleft_point[1] + topleft_change_y))
        lowright_point = (int(lowright_point[0] + lowright_change_x),
                          int(lowright_point[1] + lowright_change_y))
        new_height = int((lowright_point[1] - topleft_point[1]) * 2)
        new_width = int(lowright_point[0] - topleft_point[0])

        win.place(topleft_point[0], topleft_point[1],
                  new_width, new_height, 2, None)


def handle_mousewheel_up(lavinder, *args):
    global zoom

    mouse_x, mouse_y = lavinder.get_mouse_position()
    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)
        # blacklist the top Bar
        if win.group is None:
            continue

        topleft_point = (win.x, win.y)
        lowright_point = (int(win.x + win.width), int(win.y + win.height/2))

        zoom = zoom - 1
        topleft_change_x = (mouse_x - topleft_point[0]) * 0.1
        topleft_change_y = (mouse_y - topleft_point[1]) * 0.1

        lowright_change_x = (mouse_x - lowright_point[0]) * 0.1
        lowright_change_y = (mouse_y - lowright_point[1]) * 0.1

        topleft_point = (int(topleft_point[0] - topleft_change_x),
                         int(topleft_point[1] - topleft_change_y))
        lowright_point = (int(lowright_point[0] - lowright_change_x),
                          int(lowright_point[1] - lowright_change_y))
        new_height = (lowright_point[1] - topleft_point[1]) * 2
        new_width = lowright_point[0] - topleft_point[0]

        win.place(topleft_point[0], topleft_point[1],
                  new_width, new_height, 2, None)


# switch desktop left
def move_windows_left(lavinder, *args):
    global display_size

    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)
        # don't move top bar
        if win.group is None:
            continue

        topleft_point = (win.x + display_size[0], win.y)
        win.place(topleft_point[0], topleft_point[1],
                  win.width, win.height, 2, None)


# switch desktop right
def move_windows_right(lavinder, *args):
    global display_size

    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)
        # don't move top bar
        if win.group is None:
            continue

        topleft_point = (win.x - display_size[0], win.y)
        win.place(topleft_point[0], topleft_point[1],
                  win.width, win.height, 2, None)


# switch desktop up
def move_windows_up(lavinder, *args):
    global max_display_height

    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)
        # don't move top bar
        if win.group is None:
            continue

        topleft_point = (win.x, win.y + max_display_height)
        win.place(topleft_point[0], topleft_point[1],
                  win.width, win.height, 2, None)


# switch desktop down
def move_windows_down(lavinder, *args):
    global max_display_height

    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)
        # don't move top bar
        if win.group is None:
            continue

        topleft_point = (win.x, win.y - max_display_height)
        win.place(topleft_point[0], topleft_point[1],
                  win.width, win.height, 2, None)


def move_all_windows(lavinder, *args):
    global windows_moved
    mouse_position = lavinder.get_mouse_position()
    if mouse_position == windows_moved:
        return

    move = (mouse_position[0] - windows_moved[0],
            mouse_position[1] - windows_moved[1])
    # check if this is a new drag
    if abs(move[0]) > abs(args[0]):
        move = (args[0], move[1])
    if abs(move[1]) > abs(args[1]):
        move = (move[0], args[1])

    windows_moved = mouse_position

    for win in lavinder.windows_map:
        win = lavinder.windows_map.get(win)
        # don't move top bar
        if win.group is None:
            continue

        topleft_point = (win.x + move[0], win.y + move[1])
        win.place(topleft_point[0], topleft_point[1],
                  win.width, win.height, 2, None)


def move_window(lavinder, *args):
    global last_window_position
    global window_with_mouse
    global hot_corner_triggered
    global last_drag
    global moving_win
    global display_size

    # reset drag window and hot coners if this is a different drag event
    if last_drag != lavinder._drag:
        hot_corner_triggered = None
        moving_win = window_with_mouse
        moving_win.cmd_bring_to_front()

    mouse_position = lavinder.get_mouse_position()

    move = (mouse_position[0] - last_window_position[0],
            mouse_position[1] - last_window_position[1])
    if abs(move[0]) > abs(args[0]):
        move = (args[0], move[1])
    if abs(move[1]) > abs(args[1]):
        move = (move[0], args[1])

    last_window_position = mouse_position
    last_drag = lavinder._drag

    if moving_win != "":
        # check if we hit the top left corner
        if mouse_position[0] < 5 and mouse_position[1] < 5:
            hot_corner_triggered = (0, 0)
        # check if we hit the bottom right corner
        if mouse_position[0] + 5 >= display_size[0]:
            if mouse_position[1] + 5 >= display_size[1]:
                hot_corner_triggered = (display_size[0], display_size[1])

        new_win_size = [min_win_size, min_win_size]
        # left corner resize
        if hot_corner_triggered == (0, 0):
            # set new_win_size to new window size (But not smaller)
            if mouse_position[0] > new_win_size[0]:
                if mouse_position[1] > new_win_size[1]:
                    new_win_size[0] = mouse_position[0]
                    new_win_size[1] = mouse_position[1]
            moving_win.place(0, 0, new_win_size[0], new_win_size[1], 2, None)

        # low-right corner resize
        elif hot_corner_triggered == (display_size[0], display_size[1]):
            # set new_win_size to new window size (But not smaller)
            if mouse_position[0] < display_size[0] - new_win_size[0]:
                if mouse_position[1] < display_size[1] - new_win_size[1]:
                    new_win_size[0] = display_size[0] - mouse_position[0]
                    new_win_size[1] = display_size[1] - mouse_position[1]
            moving_win.place(mouse_position[0], mouse_position[1],
                             new_win_size[0], new_win_size[1], 2, None)

        # move window
        if hot_corner_triggered is None:
            new_position = (moving_win.x + move[0], moving_win.y + move[1])
            moving_win.place(new_position[0], new_position[1],
                             moving_win.width, moving_win.height, 2, None)


# alt + Button1 = open/move menu
def open_menu(lavinder, *args):
    global open_new_menu
    global all_open_windows
    global found_menu
    global menu_window
    cursor_x_movement = args[0]
    cursor_y_movement = args[1]
    drag_start_x = args[2]
    drag_start_y = args[3]

    if cursor_x_movement > min_win_size or cursor_y_movement > min_win_size:
        # old menu is no longer open
        if menu_window != "":
            if menu_window.info()['id'] not in list(lavinder.windows_map):
                open_new_menu = True
                menu_window = ""

        # open new menu/terminal
        if open_new_menu:
            all_open_windows = list(lavinder.windows_map)  # windows before
            # issuecomment-447843762
            # Thanks https://github.com/qtile/qtile/issues/1245
            lavinder.cmd_spawn(menu_cmd)
            found_menu = False
            open_new_menu = False
        else:
            # resize opened menu
            # look for new menu window
            found_window = ""
            if not found_menu:
                for win in lavinder.windows_map:
                    if win not in all_open_windows:
                        found_window = win
                        found_menu = True
                if not found_menu:
                    return

            if menu_window == "":
                menu_window = lavinder.windows_map.get(found_window)

            # place menu
            menu_window.place(drag_start_x - cursor_x_movement,
                              drag_start_y - cursor_y_movement,
                              cursor_x_movement, cursor_y_movement, 2, None)
            menu_window.cmd_disable_maximize()
            menu_window.focus(warp=None)
            menu_window.cmd_bring_to_front()


# key bindings
keys = [
  Key([ALT, CTRL], "t",
      lazy.spawn("xterm")),                # open xterm
  Key([WIN],       "k",
      lazy.window.kill()),                 # kill window
  Key([WIN, CTRL], "r",
      lazy.restart()),                     # restart lavinder
  Key([WIN, CTRL], "q",
      lazy.shutdown()),                    # quit lavinder
  Key([CTRL, ALT], "Left",
      lazy.function(move_windows_left)),   # move all windows left
  Key([CTRL, ALT], "Right",
      lazy.function(move_windows_right)),  # move all windows Right
  Key([CTRL, ALT], "Down",
      lazy.function(move_windows_down)),   # move all windows Down
  Key([CTRL, ALT], "Up",
      lazy.function(move_windows_up)),     # move all windows Up
  ]

# Drag layouts
mouse = [
  Click([ALT], "Button4",                           # Zoom Out
        lazy.function(handle_mousewheel_up)),
  Click([ALT], "Button5",                           # Zoom In
        lazy.function(handle_mousewheel_down)),
  Drag([WIN],  "Button1",                           # Move single win
       lazy.function(move_window),      start=0),
  Drag([CTRL], "Button1",                           # Open/Move Menu
       lazy.function(open_menu),        start=0),
  Drag([ALT],  "Button1",                           # Move all win
       lazy.function(move_all_windows), start=0),
  Drag([WIN],  "Button3",                           # resize single win
       lazy.window.set_size_floating(), start=lazy.window.get_size()),
  ]

groups = [Group(i) for i in "asdfuiop"]

layouts = [
  layout.Floating(),
  layout.Stack(num_stacks=2)
  ]

widget_defaults = dict(
  font='sans',
  fontsize=12,
  padding=3,
  )
extension_defaults = widget_defaults.copy()
floating_layout = layout.Floating()

# Define battery widget settings
battery_name = ""
"""
import utile
battery_name = util.find_battery_name()
battery_settings   = dict(
  battery_name   = battery_name,
  low_percentage = 0.1,
  format         = "{percent:2.0%}",
)
battery_icon_settings = dict(
  battery_name = battery_name,
  theme_path   = os.path.expanduser("~/.config/lavinder/icons/battery"),
)
"""


# Define bars on screens
def make_topbar(screen):
    global bar_color

    # All Screens
    widgets = [
      widget.TaskList(rounded=True, border='0000FF',
                      unfocused_border='215578'),
      widget.TextBox("Lavinder 0.02", name="configName"),
      widget.Sep(),
      widget.TextBox("Volume: "),
      widget.Volume(fontsize=12, volume_app=volume_app),
      widget.Sep(),
      widget.Notify(),
      ]

    # Stuff to only show on first screen
    if screen == 0:
        if battery_name:
            widgets.extend([
              # Battery widget not tested
              # widget.BatteryIcon(**battery_icon_settings),
              # widget.Battery(**battery_settings),
              ])
        widgets.extend([
          widget.Systray(),
          widget.Sep(),
          widget.TextBox("CPU: "),
          widget.CPUGraph(),
          widget.TextBox("Net: "),
          widget.NetGraph(border_color=net_graph_color[1],
                          graph_color=net_graph_color[0]),
          widget.Clock(format='%a %d %b %Y %H:%M:%S',
                       font='xft:monospace', fontsize=12),
          widget.Sep(),
          widget.Spacer(length=8),
          ])
    return bar.Bar(widgets, 25, background=bar_color)


screens = [
  Screen(top=make_topbar(0)),
  ]


# Configure each screen found by lavinder.
def screen_config(lavinder):
    global display_size
    global max_display_height  # biggest screen height

    # find screen_size
    display_size = [0, 0]
    max_display_height = 0
    num_screens = 0
    for screen in lavinder.conn.pseudoscreens:
        num_screens = num_screens + 1
        # append all screen width
        display_size[0] = display_size[0] + screen.width
        # keep last screen height
        # We might have issues if the displays are different sizes
        display_size[1] = screen.height
        # find tallest screen
        if screen.height > max_display_height:
            max_display_height = screen.height

    return [Screen(top=make_topbar(i)) for i in range(num_screens)]


def main(lavinder):
    # TODO, Remove 'sh' as dependency
    sh.nm_applet(_bg=True)
    lavinder.config.screens = screen_config(lavinder)
    lavinder.cmd_info()
