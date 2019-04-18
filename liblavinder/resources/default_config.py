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
from liblavinder import layout, bar, widget
from colorsys import rgb_to_hls, hls_to_rgb
import liblavinder.core.manager as manager
import types, time
from liblavinder.core.xcursors import Cursors

try:
    from typing import List  # noqa: F401
except ImportError:
    pass


#user setting
auto_fullscreen = False
debugging = True
CriticalDebug = True


#static
white = (0, 1, 0)
black = (0, 0, 0)
zoom = 0



def debug(error, newLine='\n', Level=1):
  global debugging
  global CriticalDebug
  critBug = Level > 1
  critBug = critBug and CriticalDebug
  
  if debugging or critBug:
    debugLog = open('/tmp/Debug.txt', 'a+')
    debugLog.write(str(error) + newLine)
    debugLog.close()

#zoom all windows in
def handleMouseWheelUp(*args):
  handleMouseWheel(*args, direction="Up")

def handleMouseWheelDown(*args):
  handleMouseWheel(*args, direction="Down")
#zoom all windows out
def handleMouseWheel(lavinder, *args, direction="Down"):
  global zoom

  mouseX, mouseY = lavinder.get_mouse_position()
  #debug('Zoom out')
  #debug(f'x:{mouseX} y:{mouseY}')
  for win in lavinder.windows_map:
    foundWinObj = lavinder.windows_map.get(win)
    #blacklist the top Bar
    if foundWinObj.group == None:
      debug("BLACKLIST")
      continue
    #debug(f"IT IS WORKING too {dir(foundWinObj)}")
    debug(f"IT IS WORKING too {foundWinObj.group}")
    #midX, midY = windowz[i][0].x + (windowz[i][0].height/2), windowz[i][0].y + (windowz[i][0].width/2)
    Point1 = (foundWinObj.x,foundWinObj.y)
    Point2 = (int(foundWinObj.x + foundWinObj.width), int(foundWinObj.y + foundWinObj.height/2))
    debug(f'x:{str(Point1)} y:{str(Point2)}')
    
    if direction == "Down":
      zoom = zoom + 1
      point1XMove = (mouseX - Point1[0]) * 0.1
      point1YMove = (mouseY - Point1[1]) * 0.1
      
      point2XMove = (mouseX - Point2[0]) * 0.1
      point2YMove = (mouseY - Point2[1]) * 0.1
      
      Point1 = int(Point1[0] + point1XMove), int(Point1[1] + point1YMove)
      Point2 = int(Point2[0] + point2XMove), int(Point2[1] + point2YMove)
      newHeight = int((Point2[1] - Point1[1]) *2)
      newWidth = int(Point2[0] - Point1[0])
    if direction == "Up":
      zoom = zoom - 1
      point1XMove = (mouseX - Point1[0]) * 0.1
      point1YMove = (mouseY - Point1[1]) * 0.1
      
      point2XMove = (mouseX - Point2[0]) * 0.1
      point2YMove = (mouseY - Point2[1]) * 0.1
      
      Point1 = int(Point1[0] - point1XMove), int(Point1[1] - point1YMove)
      Point2 = int(Point2[0] - point2XMove), int(Point2[1] - point2YMove)
      newHeight = (Point2[1] - Point1[1]) *2
      newWidth = Point2[0] - Point1[0]
    
    foundWinObj.place(Point1[0],Point1[1],newWidth,newHeight,2, None)

              
def moveAllWindows(lavinder, *args):
  MoveX = args[0]
  MoveY = args[1]
  for win in lavinder.windows_map:
    foundWinObj = lavinder.windows_map.get(win)
    if foundWinObj.group == None:
      debug("BLACKLIST")
      continue
    Point1 = (foundWinObj.x,foundWinObj.y)
    debug("Move ALL: " + str(MoveX) + " " + str(MoveY) + " " + str(args))


#alt + Button1 = drag out new window
firstClick = []
OpenNew = False
found = False
foundWinObj = ""
def openNewWindow(lavinder, *args):
  global OpenNew
  global startWindows
  global found
  global foundWinObj
  MoveX = args[0]
  MoveY = args[1]
  x = args[2]
  y = args[3]
  threshold = 50
  if MoveX > threshold or MoveY > threshold:
    if not OpenNew:
      #open new menu/terminal 
      #setup current window
      startWindows = list(lavinder.windows_map)
      lavinder.cmd_spawn("xterm") # Thanks https://github.com/lavinder/lavinder/issues/1245#issuecomment-447843762
      found = False
      #time.sleep(0.2)
      #debug("Info: " + str(lavinder.currentWindow.place), Level=2)
      #lazy.spawn("xterm")
      OpenNew = True
      debug ("OpenNew at " + str(x) + " " + str(y))
    else:
      #resize newly opened
      newWidth = MoveX
      newHeight = MoveY
      #wait for window
      maxCount = 10
      count = 0
      
      #look for new window
      foundWin = ""
      if not found:
        for win in lavinder.windows_map:
          if win not in startWindows:
            debug("Found New windows " + str(win))
            foundWin = win
            found = True
        if not found:
          debug("No Window??? " + str(len(startWindows)) + " " + str(len(lavinder.windows_map)))
          return

      if foundWinObj == "":
        foundWinObj = lavinder.windows_map.get(foundWin)
      foundWinObj.place(x - newWidth,y - newHeight,newWidth,newHeight,2, None)
      foundWinObj.cmd_disable_maximize()
      #cmd_disable_fullscreen()
      #lavinder.currentWindow.place(x,y,newWidth,newHeight,2, None)
      debug ("Resize " + str(x) + " " + str(y))
  else:
    OpenNew = False
    foundWinObj = ""
    
    #lazy.window.set_size_floating()
  #Move window to x and y



mod = "mod4"
mod2 = "mod1"

keys = [
  
  # Switch between windows in current stack pane
  Key([mod], "k", lazy.layout.down()),
  Key([mod], "j", lazy.layout.up()),

  # Move windows up or down in current stack
  Key([mod, "control"], "k", lazy.layout.shuffle_down()),
  Key([mod, "control"], "j", lazy.layout.shuffle_up()),

  # Switch window focus to other pane(s) of stack
  Key([mod], "space", lazy.layout.next()),

  # Swap panes of split stack
  Key([mod, "shift"], "space", lazy.layout.rotate()),

  # Toggle between split and unsplit sides of stack.
  # Split = all windows displayed
  # Unsplit = 1 window displayed, like Max layout, but still with
  # multiple stack panes
  Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
  Key([mod], "Return", lazy.spawn("xterm")),

  # Toggle between different layouts as defined below
  Key([mod], "Tab", lazy.next_layout()),
  Key([mod], "w", lazy.window.kill()),

  Key([mod, "control"], "r", lazy.restart()),
  Key([mod, "control"], "q", lazy.shutdown()),
  Key([mod], "r", lazy.spawncmd()),
]



   
groups = [Group(i) for i in "asdfuiop"]
for i in groups:
  keys.extend([
    # mod1 + letter of group = switch to group
    Key([mod], i.name, lazy.group[i.name].toscreen()),

    # mod1 + shift + letter of group = switch to & move focused window to group
    Key([mod, "shift"], i.name, lazy.window.togroup(i.name)),
  ])

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

# Drag floating layouts.
mouse = [
  Click([mod2], "Button4", lazy.function(handleMouseWheelUp)),
  Click([mod2], "Button5", lazy.function(handleMouseWheelDown)),
  Drag([mod], "Button1", lazy.window.set_position_floating(),start=lazy.window.get_position()),
  Drag([mod2], "Button1",  lazy.function(openNewWindow),start=0),
  Drag([mod2], "Button3",  lazy.function(moveAllWindows),start=0),
  Drag([mod], "Button3", lazy.window.set_size_floating(),start=lazy.window.get_size()),
  Click([mod], "Button2", lazy.window.bring_to_front())
]




# Misc settings
dgroups_key_binder         = None
dgroups_app_rules          = []
follow_mouse_focus         = False
bring_front_click          = False
cursor_warp                = False
auto_fullscreen            = False
#focus_on_window_activation = "smart"
wmname = "LG3D" # Because Java is braindead.



focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, github issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"




# Define layout color settings #taken from: https://github.com/de-vri-es/lavinder-config/blob/master/config.py
def screenColor(screen):
  if screen == 0: return 220 / 360.0, 0.1, 0.1
  if screen == 1: return  40 / 360.0, 0.1, 0.1
  if screen == 2: return 270 / 360.0, 0.1, 0.1
  return 270 / 360.0, 0.5, 0.5

def toHexColor(hls):
  r, g, b = hls_to_rgb(*hls)
  return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))
def fade(hls):
  return lsMultiply(hls, 0.7, 0.8)
def lsMultiply(hls, l, s):
  return hls[0], hls[1] * l, hls[2] * s

layout_color = dict(
  border_focus  = toHexColor(fade(screenColor(0))),
  border_normal = toHexColor(fade(fade(white))),
  border_width  = 1,
)
floating_layout            = layout.Floating(**layout_color)


def background(hls):
  return lsMultiply(hls, 0.4, 0.7)

def toQtileColor(hls):
  r, g, b = hls_to_rgb(*hls)
  return r * 255, g * 255, b * 255




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


#Bar settings
def makeBar(screen):
  widgets = [
    # Current layout
    #widget.Prompt(),
    widget.WindowName(),
    widget.TextBox("Lavinder 0.01", name="configName"),
    widget.Systray(),
    #widget.Clock(format='%Y-%m-%d %a %I:%M %p'),
  ]

  if screen == 0:
    if battery_name:
      widgets.extend([
        # Battery widget
        widget.BatteryIcon(**battery_icon_settings),
        widget.Battery(**battery_settings),
      ])

    widgets.extend([
      # System tray
      widget.Systray(),
      widget.Spacer(length=8),
    ])

  widgets.extend([
    # Clock
    widget.Clock(format='%a %d %b %Y %H:%M:%S', font='xft:monospace', fontsize=12, foreground='#ffaa00'),
    widget.Spacer(length=8),
  ])

  bg_color =  toQtileColor(background(screenColor(screen)))

  return bar.Bar(widgets, 16, background=bg_color)

# Define bars on screens
screens = [
  Screen(top=makeBar(0)),
]

def makeScreensConfig(lavinder):
  ''' Configure each screen found by lavinder. '''
  screens = len(lavinder.conn.pseudoscreens)
  return [Screen(top=makeBar(i)) for i in range(screens)]


def main(lavinder):
  lavinder.config.screens = makeScreensConfig(lavinder)
  lavinder.cmd_info()
  
  
