# please credit! made by @lompendans on youtube
# commented by an idiot, for idiots so they can understand a bit of the code

import time
import subprocess
from datetime import datetime, timezone
import pytchat


VIDEO_ID = "STREAM_ID"  # remember to change this section at every stream! (USE THE PART AFTER watch?v=)
VBOX = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM_NAME = "vmname" # CHANGE THIS TO YOUR VM NMAE IN VIRTUALBOX
POLL_DELAY = 1
WATCHDOG = True

# SAFETY STUFF - these are the commands that get blocked in chat (feel free to modify)
BLOCKED_WORDS = {
    "shutdown",
    "shutdown /s",
    "shutdown -s",
    "poweroff",
    "halt",
    "logoff",
    "-force",
    "stop"
}

def contains_blocked(text):
    # Just doing a simple lowercase check for now
    txt = text.lower()
    for bad in BLOCKED_WORDS:
        if bad in txt:
            return True
    return False

# VM STATE CHECKING
RESTORING_VM = False  # flag to prevent command spam during restore

def vm_is_running():
    # Check if the VM is actually running
    try:
        result = subprocess.check_output(
            [VBOX, "showvminfo", VM_NAME, "--machinereadable"],
            stderr=subprocess.DEVNULL
        )
        info = result.decode()
        if 'VMState="running"' in info:
            return True
        else:
            return False
    except Exception as e:
        # If something goes wrong, assume it's not running
        return False

def start_vm():
    print(" Starting VM...", flush=True)
    # Starting with GUI because headless mode is boring
    subprocess.run(
        [VBOX, "startvm", VM_NAME, "--type", "gui"],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

# SCANCODE SENDER - the core functionality
def send_scancode(press, release):
    # Send the press codes first
    subprocess.run(
        [VBOX, "controlvm", VM_NAME, "keyboardputscancode"] + press,
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    time.sleep(0.05)  # Small delay between press and release
    # Then release
    subprocess.run(
        [VBOX, "controlvm", VM_NAME, "keyboardputscancode"] + release,
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )


# SCANCODES - took forever to map all these out
SCANCODES = {
    # Letters (lowercase)
    "a": (["1e"], ["9e"]), 
    "b": (["30"], ["b0"]), 
    "c": (["2e"], ["ae"]),
    "d": (["20"], ["a0"]), 
    "e": (["12"], ["92"]), 
    "f": (["21"], ["a1"]),
    "g": (["22"], ["a2"]), 
    "h": (["23"], ["a3"]), 
    "i": (["17"], ["97"]),
    "j": (["24"], ["a4"]), 
    "k": (["25"], ["a5"]), 
    "l": (["26"], ["a6"]),
    "m": (["32"], ["b2"]), 
    "n": (["31"], ["b1"]), 
    "o": (["18"], ["98"]),
    "p": (["19"], ["99"]), 
    "q": (["10"], ["90"]), 
    "r": (["13"], ["93"]),
    "s": (["1f"], ["9f"]), 
    "t": (["14"], ["94"]), 
    "u": (["16"], ["96"]),
    "v": (["2f"], ["af"]), 
    "w": (["11"], ["91"]), 
    "x": (["2d"], ["ad"]),
    "y": (["15"], ["95"]), 
    "z": (["2c"], ["ac"]),

    # Number row
    "1": (["02"], ["82"]), 
    "2": (["03"], ["83"]), 
    "3": (["04"], ["84"]),
    "4": (["05"], ["85"]), 
    "5": (["06"], ["86"]), 
    "6": (["07"], ["87"]),
    "7": (["08"], ["88"]), 
    "8": (["09"], ["89"]), 
    "9": (["0a"], ["8a"]),
    "0": (["0b"], ["8b"]),

    # Shifted number symbols
    "!": (["02"], ["82"]),
    "@": (["03"], ["83"]),
    "#": (["04"], ["84"]),
    "$": (["05"], ["85"]),
    "%": (["06"], ["86"]),
    "^": (["07"], ["87"]),
    "&": (["08"], ["88"]),
    "*": (["09"], ["89"]),
    "(": (["0a"], ["8a"]),
    ")": (["0b"], ["8b"]),

    # Special keys that chat needs the most because of enter
    "space": (["39"], ["b9"]),
    "enter": (["1c"], ["9c"]),
    "tab": (["0f"], ["8f"]),
    "backspace": (["0e"], ["8e"]),
    "esc": (["01"], ["81"]),
    "capslock": (["3a"], ["ba"]),

    # Modifier keys that they also need because of the beloved win key
    "shift": (["2a"], ["aa"]),
    "ctrl": (["1d"], ["9d"]),
    "alt": (["38"], ["b8"]),
    "win": (["e0","5b"], ["e0","db"]),
    "menu": (["e0","5d"], ["e0","dd"]),

    # Punctuation and symbols
    "-": (["0c"], ["8c"]),
    "=": (["0d"], ["8d"]),
    "[": (["1a"], ["9a"]),
    "]": (["1b"], ["9b"]),
    "\\": (["2b"], ["ab"]),
    ";": (["27"], ["a7"]),
    "'": (["28"], ["a8"]),
    "`": (["29"], ["a9"]),
    ",": (["33"], ["b3"]),
    ".": (["34"], ["b4"]),
    "/": (["35"], ["b5"]),

    # Arrow keys - these use extended scancodes
    "up": (["e0","48"], ["e0","c8"]),
    "down": (["e0","50"], ["e0","d0"]),
    "left": (["e0","4b"], ["e0","cb"]),
    "right": (["e0","4d"], ["e0","cd"]),

    # Function keys F1-F12
    "f1": (["3b"], ["bb"]),
    "f2": (["3c"], ["bc"]),
    "f3": (["3d"], ["bd"]),
    "f4": (["3e"], ["be"]),
    "f5": (["3f"], ["bf"]),
    "f6": (["40"], ["c0"]),
    "f7": (["41"], ["c1"]),
    "f8": (["42"], ["c2"]),
    "f9": (["43"], ["c3"]),
    "f10": (["44"], ["c4"]),
    "f11": (["57"], ["d7"]),
    "f12": (["58"], ["d8"]),

    # Navigation cluster
    "insert": (["e0","52"], ["e0","d2"]),
    "delete": (["e0","53"], ["e0","d3"]),
    "home": (["e0","47"], ["e0","c7"]),
    "end": (["e0","4f"], ["e0","cf"]),
    "pageup": (["e0","49"], ["e0","c9"]),
    "pagedown": (["e0","51"], ["e0","d1"]),
}

def press_key(key):
    # Simple key press function
    k = key.lower()
    if k in SCANCODES:
        press_codes, release_codes = SCANCODES[k]
        send_scancode(press_codes, release_codes)

# KEY COMBINATION HANDLER
def combo(keys):
    # For handling stuff like ctrl+alt+del
    presses = []
    releases = []
    
    for k in keys:
        if k not in SCANCODES:
            continue
        p, r = SCANCODES[k]
        presses.extend(p)
        # Need to reverse order for releases
        releases = r + releases
    
    if presses:
        send_scancode(presses, releases)

# TEXT TYPING
def type_text(text):
    # using VBox's built-in text typing - easier than scancodes for strings
    subprocess.run(
        [VBOX, "controlvm", VM_NAME, "keyboardputstring", text],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

def send_text(text):
    # Type text and hit enter
    type_text(text)
    press_key("enter")

# VM CONTROL FUNCTIONS
def restart_vm():
    print("Restarting VM...", flush=True)
    subprocess.run(
        [VBOX, "controlvm", VM_NAME, "reset"],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

def restore_snapshot():
    global RESTORING_VM
    RESTORING_VM = True
    print("Restoring VM! Do not touch the commands...", flush=True)

    # Power off first
    subprocess.run(
        [VBOX, "controlvm", VM_NAME, "poweroff"],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)  # Give it a moment to actually power off

    # Restore the snapshot
    subprocess.run(
        [VBOX, "snapshot", VM_NAME, "restore", "snapshotname"], # change snapshotname to your snapshot name
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # Start it back up
    subprocess.run(
        [VBOX, "startvm", VM_NAME, "--type", "gui"],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

    RESTORING_VM = False
    print("VM restored", flush=True)

# COMMAND CHAINING - my streams chat really needs this feature or else they crash out

# ok lompendans here from like 2 months after making this, my streams chat destroyed my channel
def split_commands(message):
    # Split message into individual commands
    commands = []
    current_cmd = ""

    parts = message.split()
    for part in parts:
        if part.startswith("!") and current_cmd:
            # Found a new command, save the previous one
            commands.append(current_cmd.strip())
            current_cmd = part
        else:
            current_cmd += " " + part

    # Don't forget the last command
    if current_cmd.strip():
        commands.append(current_cmd.strip())

    return commands

def execute_command(cmd):
    # Execute a single command
    lower_cmd = cmd.lower()

    if lower_cmd == "!restartvm":
        restart_vm()
    elif lower_cmd == "!restore":
        restore_snapshot()
    elif lower_cmd.startswith("!key "):
        key_name = cmd.split(" ", 1)[1]
        press_key(key_name)
    elif lower_cmd.startswith("!combo "):
        # Parse combo like "ctrl+alt+del"
        combo_str = cmd.replace("!combo", "").replace("+", " ")
        keys = combo_str.split()
        combo(keys)
    elif lower_cmd.startswith("!type "):
        text = cmd.split(" ", 1)[1]
        type_text(text)
    elif lower_cmd.startswith("!send "):
        text = cmd.split(" ", 1)[1]
        send_text(text)

# MAIN LOOP
print("Code is running. Connected to stream {VIDEO_ID})", flush=True) # you CAN understand this. You WILL understand this

# Initialize chat connection
chat = pytchat.create(video_id=VIDEO_ID)
bot_start_time = datetime.now(timezone.utc)

while chat.is_alive():
    # Get chat messages
    for c in chat.get().sync_items():
        # Parse message timestamp
        try:
            msg_time = datetime.strptime(
                c.datetime.strip(), "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        except:
            continue

        # Skip old messages from before bot started
        if msg_time < bot_start_time:
            continue

        msg = c.message.strip()
        lower = msg.lower()
        user = c.author.name

        print(f"{user} → {msg}", flush=True)

        # Safety check
        if contains_blocked(msg):
            print(f"Blocked dangerous command from {user}.", flush=True)
            continue

        # Don't process commands during restore
        if RESTORING_VM:
            print("Restoring VM! Do not touch the commands...", flush=True)
            continue

        # Check if VM is running
        if not vm_is_running():
            print("VM is powered off! Type !startvm to start it.", flush=True)
            if lower == "!startvm":
                start_vm()
            continue

        # Watchdog check
        if not WATCHDOG:
            continue

        # Execute command chain
        commands = split_commands(msg)
        for command in commands:
            execute_command(command)


    time.sleep(POLL_DELAY)
