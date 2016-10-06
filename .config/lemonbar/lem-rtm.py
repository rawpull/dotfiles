#!/usr/bin/env python

# imports
import i3ipc,re,subprocess,time,os

# <Settings> 
I3_CONNECTION            = i3ipc.Connection()
PRIMARY_SOUND_DEV        = "alsa_output.usb-Logitech_Logitech_USB_Headset-00.analog-stereo"
SECONDARY_SOUND_DEV      = "alsa_output.pci-0000_00_1b.0.analog-stereo"
ETH                      = "enp8s0"
WL                       = "wlp7"
# Colors in hex
WS_COLOR_UNDERLINE       = "#62AFEE"
WS_COLOR_NORMAL          = "#dddddd"
WS_COLOR_HIGHLIGHT       = "#ffffff"
WS_COLOR_ICON            = "#62AFEE"
COLOR_UNDERLINE          = "%{F#62AFEE}"
COLOR_ICON               = "%{F#62AFEE}"
COLOR_TEXT               = "%{F#dddddd}"
COLOR_RED                = "%{F#FF0000}"
END_COLOR                = "%{F-}"
# Align bar objects
LEFT                     = "%{l}"
CENTER                   = "%{c}"
RIGHT                    = "%{r}"
GAP                      = "%{O10}"
SEP                      = " "
UNDERLINE_INIT           = "%{+u}%{U#62AFEE}"
UNDERLINE_END            = "%{U-}%{-u}"
OVERLINE_INIT            = "%{+o}%{O#62AFEE}"
OVERLINE_END             = "%{O-}%{-o}"
#icons - AwesomeFont
WORKSPACES               = ""
TIME                     = ""
DATE                     = ""
VOLUME                   = ""
HEADPHONES               = ""
PLAY                     = ""
PAUSE                    = ""
NEXT                     = ""
BACK                     = ""
STOP                     = ""
WALLPAPER                = ""
BATTERY_CRITICAL         = ""   #   5%
BATTERY_LOW              = ""   #  25%
BATTERY_HALF             = ""   #  50%
BATTERY_ALMOST           = ""   #  75%
BATTERY_FULL             = ""   # 100%
WIRED                    = ""
#</Settings>



# Run bash command
def run(arg):
  return subprocess.Popen(arg,stdout = subprocess.PIPE,stderr = subprocess.PIPE,shell = True).communicate()[0].decode("utf-8").strip()

# Create clickable area:
# (sh command, 1 - LMB                             , button color in hex)
#              2 - CMB > 4 ScrollUp | 5 ScrollDown    %{F#FF0000}" for example
#              3 - RMB
def action(arg,button,color):
  return color + "%{A" + "1" + ":" + arg + ":}" + button + "%{A}" + END_COLOR + GAP

# taken from stackoverflow user: Mark Byers
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

# taken from github user: nvnehi
def get_workspaces():
  # stores the name of the focused workspace
  focused_workspace = ""
  # get a list of workspace related objects
  workspaces = I3_CONNECTION.get_workspaces()
  # stores the names of each workspace
  workspace_names = []

  # iterate the workspaces and save their names to workspace_names
  for workspace in workspaces:
    workspace_names.append(workspace.name)
    if workspace.focused:
      focused_workspace = workspace.name

  # build the string to return
  s = "%{{A4:i3-msg workspace prev:}}%{{A5:i3-msg workspace next:}}%{{F{}}}{} %{{F-}}".format(WS_COLOR_ICON, WORKSPACES)

  # iterate the workspace names and build the string to return to lemonbar
  for workspace_name in ( natural_sort(workspace_names)):
    # if the workspace is the focused workspace, highlight it to represent the fact
    if workspace_name == focused_workspace:
      s += "%{{+u}}%{{U{}}}%{{F{}}} ".format(WS_COLOR_UNDERLINE, WS_COLOR_HIGHLIGHT) + workspace_name + " %{F-}%{U-}%{-u} "
    else:
      s += "%{{A:i3-msg workspace {}:}}%{{F{}}} ".format(workspace_name, WS_COLOR_NORMAL) + workspace_name + " %{F-}%{A} "

  s += "%{A}%{A}"

  return s

# Output battery percents
def get_battery():
  raw     = run("acpi")[11:-1]
  icon    = ""
  time    = ""
  time = raw[raw.find("%,")+4:raw.find("%,")+8]
  if "until" in raw:
    icon = COLOR_ICON + WIRED + " "
    if time == "unti": time = ""
  elif "Unknown" in raw:
    icon = COLOR_ICON + WIRED
    time = ""
  elif "Full" in raw:
    icon = COLOR_ICON + WIRED
    time = ""
  elif "remainin" in raw:
    percent = int(raw[raw.find(" ")+1:raw.find("%")])
    if   percent <= 5:   icon = COLOR_ICON + BATTERY_CRITICAL
    elif percent <= 25:  icon = COLOR_ICON + BATTERY_LOW
    elif percent <= 50:  icon = COLOR_ICON + BATTERY_HALF
    elif percent <= 75:  icon = COLOR_ICON + BATTERY_ALMOST
    elif percent <= 100: icon = COLOR_ICON + BATTERY_FULL
    icon += " "
    if icon == BATTERY_LOW + " ": return COLOR_RED + icon + time
  return icon + str(time)


def get_time():
  hour = time.strftime("%I")
  minute = time.strftime("%M")
  day = time.strftime("%d")
  month = time.strftime("%m")
  year = time.strftime("%y")
  separator = COLOR_ICON + "/"
  __time =  COLOR_ICON + TIME + " " + COLOR_TEXT + hour + END_COLOR + COLOR_ICON + ":" + END_COLOR + COLOR_TEXT + minute
  __date = COLOR_ICON + DATE + " " + COLOR_TEXT + day + separator + COLOR_TEXT + month + separator + COLOR_TEXT + year + END_COLOR
  return __time + " " + __date


def get_volume(pdev,sdev):
  raw = run("pactl list sinks"); icon = ""; action = "" ; nn = 0
  if pdev in raw:
    dev = pdev; icon = HEADPHONES; nn = 150
    actions = "%{A1:pavucontrol:}%{A4:amixer -q -D sysdefault sset Headphone 10%+ unmute:}%{A5:amixer -q -D sysdefault sset Headphone 10%- unmute:}"
  elif sdev in raw:
    dev = sdev; icon = VOLUME; nn = 100
    actions = "%{A1:pavucontrol:}%{A4:amixer -q sset Master 10%+ unmute:}%{A5:amixer -q sset Master 10%- unmute:}"
  else:
    return COLOR_ICON + VOLUME + COLOR_TEXT + "nosnd"

  find = raw.splitlines()[8]
  sraw = raw.splitlines()
  y = 0; x = 0; n = 0
  for x in range (0,nn):
    if dev in sraw[x]:
      y = x
      for y in range (x,nn):
        if find in sraw[y]:
          n = y
          break
      break
  num = n+1
  s = sraw[num:num+1][0]
  value = s[s.find("/ ")+2:s.find("%")]
  if "IDL" in value: #<<< FIX THIS SHIT
    value = "muted"
    return COLOR_ICON + actions + icon + "%{A}%{A}%{A}" + COLOR_TEXT + value
  else:
    return COLOR_ICON + actions + icon + "%{A}%{A}%{A}" + COLOR_TEXT + value +"%"


def get_rhythm_buttons():
  back_btn = action('rhythmbox-client --previous',BACK,COLOR_ICON)
  next_btn = action('rhythmbox-client --next',NEXT,COLOR_ICON)
  raw = run("qdbus org.mpris.MediaPlayer2.rhythmbox /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get org.mpris.MediaPlayer2.Player PlaybackStatus")
  if raw == "Playing":
    return back_btn + action('rhythmbox-client --pause',PAUSE,COLOR_ICON) + action('rhythmbox-client --stop',STOP,COLOR_ICON) + next_btn
  elif raw == "Paused":
    return back_btn + action('rhythmbox-client --play',PLAY,COLOR_ICON) + action('rhythmbox-client --stop',STOP,COLOR_ICON) + next_btn
  else:
    return back_btn + action('rhythmbox-client --play',PLAY,COLOR_ICON) + next_btn
                      

def get_rhythm_song():
  raw = run("qdbus org.mpris.MediaPlayer2.rhythmbox /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get org.mpris.MediaPlayer2.Player PlaybackStatus")
  song = run("rhythmbox-client --print-playing")
  time = run("rhythmbox-client --print-playing-format=%te/%td")
  if raw == "Playing" or raw == "Paused":
    return UNDERLINE_INIT + COLOR_TEXT + song + GAP + time + END_COLOR + UNDERLINE_END + GAP
  else:
    return ""

def set_randomwp():
  return action("feh --randomize --bg-fill ~/.bg/*",WALLPAPER,COLOR_ICON)

def get_layout():
  value = run("xkblayout-state print %s")
  return COLOR_TEXT + value + GAP

def get_netstat():
  run("cat /sys/class/net" + eth + "/operstate")

def get_status():
  return LEFT + GAP + get_workspaces() + CENTER + get_rhythm_song() + get_rhythm_buttons() + RIGHT + UNDERLINE_INIT + get_layout() + set_randomwp() + get_volume(PRIMARY_SOUND_DEV,SECONDARY_SOUND_DEV) + GAP + get_time() + GAP + get_battery() + UNDERLINE_END + GAP

def main():
  # print the status and sleep until interrupted
  while True:
    print(get_status())
    time.sleep(.4)
  begin

main()