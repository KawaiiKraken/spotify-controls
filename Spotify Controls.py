import configparser 
import subprocess
import keyboard
import os
import sys
import webbrowser
import ctypes
import win32gui
import pywinauto
import customtkinter as ctk
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image
#import win32api
#from time import sleep
#import win32ui
#import win32con
#import pyautogui
#import importlib
#import spotipy
#from timeout_decorator import timeout

def get_bundled_png_filepath(filename):
    # Get the path to the temporary directory where data is extracted
    data_dir = sys._MEIPASS

    # Construct the full path to the bundled .png file
    png_file_path = os.path.join(data_dir, "data", filename)

    return png_file_path


# Create a ConfigParser object
config = configparser.ConfigParser()
def attemptSetConfig():
    #print('setting config...')
    # Define global variables to be used in the function
    global pause_bind
    global vol_up_bind
    global vol_down_bind
    global next_track_bind
    global prev_track_bind
    global like_track_bind
    global toggle_shuffle_bind
    global toggle_repeat_bind
    global seek_forw_bind
    global seek_backw_bind
    # Check if the 'spotify_controls.ini' file exists
    if not os.path.isfile('spotify_controls.ini'):
        # If it doesn't exist, create it and set the initial configuration
        config['hotkeys'] = {'pause_bind': pause_bind,
                            'vol_up_bind': vol_up_bind,
                            'vol_down_bind': vol_down_bind,
                            'next_track_bind': next_track_bind,
                            'prev_track_bind': prev_track_bind,
                            'like_track_bind': like_track_bind,
                            'toggle_shuffle_bind': toggle_shuffle_bind,
                            'toggle_repeat_bind': toggle_repeat_bind,
                            'seek_forw_bind': seek_forw_bind,
                            'seek_backw_bind': seek_backw_bind}
        # Write the configuration to the 'spotify_controls.ini' file
        with open('spotify_controls.ini', 'w') as configfile:
            config.write(configfile)


def readConfig():
    global pause_bind
    global vol_up_bind
    global vol_down_bind
    global next_track_bind
    global prev_track_bind
    global like_track_bind
    global toggle_shuffle_bind
    global toggle_repeat_bind
    global seek_forw_bind
    global seek_backw_bind
    config.read('spotify_controls.ini')
    hotkeys = config['hotkeys']
    pause_bind = hotkeys['pause_bind']
    vol_up_bind = hotkeys['vol_up_bind']
    vol_down_bind = hotkeys['vol_down_bind']
    next_track_bind = hotkeys['next_track_bind']
    prev_track_bind = hotkeys['prev_track_bind']
    like_track_bind = hotkeys['like_track_bind']
    toggle_shuffle_bind = hotkeys['toggle_shuffle_bind']
    toggle_repeat_bind = hotkeys['toggle_repeat_bind']
    seek_forw_bind = hotkeys['seek_forw_bind']
    seek_backw_bind = hotkeys['seek_backw_bind']
    
        
def get_pid_from_hwnd(hwnd):
    process_id = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    return process_id.value

def sendKeysToSpotify(keys):
    hwnds = get_window_hwnds_by_executable_name('spotify.exe')
    hwnd = hwnds[0]
    #print('hwnd: ' + str(hwnd))
    if ((hwnd != 0) and (hwnd != None)):
        pid = get_pid_from_hwnd(hwnd)
        app = pywinauto.Application().connect(process=pid)
        window = app.Chrome_WidgetWin_0.set_keyboard_focus()
        window.send_keystrokes(keys, with_spaces=True, with_tabs=True, with_newlines=True)

    
def get_window_hwnds_by_executable_name(target_executable_name):
    window_hwnd = []
    
    def enum_windows_callback(hwnd, _):
        nonlocal window_hwnd
        try:
            # Get the process ID of the window
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            # Constants for Windows API functions
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010

            # Open the process with required permissions
            h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            
            if h_process:
                # Get the executable file path of the process
                executable_path = ctypes.create_string_buffer(512)
                ctypes.windll.psapi.GetModuleFileNameExA(h_process, 0, executable_path, ctypes.sizeof(executable_path))
                # Extract the executable name from the path
                executable_name = os.path.basename(executable_path.value.decode())
                ##print(executable_name + "(" + str(hwnd) + ")")
                
                # Close the process handle
                ctypes.windll.kernel32.CloseHandle(h_process)

                # Check if the current window's executable name matches the target name
                if executable_name.lower() == target_executable_name.lower():
                    ##print("returned hwnd: " + str(hwnd) + " for exe: " + executable_name + "(" + str(pid) + ")")
                    window_hwnd.append(hwnd) 
        except Exception as e:
            #print("Error: " + str(e))
            pass
        return True 
    # Enumerate all top-level windows and filter by executable name
    win32gui.EnumWindows(enum_windows_callback, 0)
    return window_hwnd
    
    
def spotifyHide():
    #print("spotify hide")
    hwnds = get_window_hwnds_by_executable_name('spotify.exe')
    #print('hwnds: ' + str(hwnds))
    #SW_HIDE = 0
    #SW_RESTORE = 9
    #SW_SHOW = 5
    SW_MINIMIZE = 6
    for hwnd in hwnds:
        ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)

def bind_keys(label, labal_text, result, result_event):
    label.configure(text="Press keys to bind...")
    bind = ''
    while True:
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:
            #print('keydown:' + event.name)
            if bind .find(event.name) == -1:
                bind += '+' 
                bind += event.name

        if event.event_type == keyboard.KEY_UP:
            #print('keyup: ' + event.name)
            break

        # clean up the resulting string
        bind = bind.replace('++', '+')
        if len(bind) > 0:
            if bind[0] == '+':
                if len(bind) > 1:
                    bind = bind[1:]
                else:
                    bind = ''

        if len(bind) > 1:
            last_index = len(bind)-1
            if bind[last_index] == '+':
                bind = bind[:last_index-1]

        label.configure(text=labal_text + ": " + bind)

    #print("returned bind")
    result[0] = bind
    result_event.set()

def bind_pause(label):
    global pause_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "pause", result, result_event))
    thread.start()
    result_event.wait()
    pause_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_vol_up(label):
    global vol_up_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "volume up", result, result_event))
    thread.start()
    result_event.wait()
    vol_up_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_vol_down(label):
    global vol_down_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "volume down", result, result_event))
    thread.start()
    result_event.wait()
    vol_down_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_next_track(label):
    global next_track_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "next track", result, result_event))
    thread.start()
    result_event.wait()
    next_track_bind = result[0]
    set_hotkeys()
    attemptSetConfig()


def bind_prev_track(label):
    global prev_track_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "previous track", result, result_event))
    thread.start()
    result_event.wait()
    prev_track_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_like_track(label):
    global like_track_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "like track", result, result_event))
    thread.start()
    result_event.wait()
    like_track_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_toggle_shuffle(label):
    global toggle_shuffle_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "toggle shuffle", result, result_event))
    thread.start()
    result_event.wait()
    toggle_shuffle_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_toggle_repeat(label):
    global toggle_repeat_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "toggle repeat", result, result_event))
    thread.start()
    result_event.wait()
    toggle_repeat_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_seek_forw(label):
    global seek_forw_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "seek forward", result, result_event))
    thread.start()
    result_event.wait()
    seek_forw_bind = result[0]
    set_hotkeys()
    attemptSetConfig()

def bind_seek_backw(label):
    global seek_backw_bind
    result_event = threading.Event()
    result = [None]
    thread = threading.Thread(target=bind_keys, args=(label, "seek backward", result, result_event))
    thread.start()
    result_event.wait()
    seek_backw_bind = result[0]
    set_hotkeys()
    attemptSetConfig()
    

def join_server():
    webbrowser.open("https://thrallway.com")

def reload_program():
    current_script = sys.argv[0]  # Get the name of the current script
    subprocess.Popen([sys.executable, current_script])
    #sys.exit()
    #quit()
    #exit()
    quit2()
    
def show_credits(app):
    popup = ctk.CTkToplevel(app)
    popup.title("Credits")
    popup.geometry("200x120+200+200")  # Adjust the size and position as needed
    popup.resizable(False, False)
    popup.label = ctk.CTkLabel(master=popup, font=ctk.CTkFont(size=15), text="made with the help of:\n- LeopoldPrime\n- SniperAstra\n- Zenith")
    popup.label.pack(fill=ctk.BOTH, expand=True)
    popup.transient(app)  # Makes the popup related to the main window
    popup.grab_set()  # Prevents interaction with the main window while the popup is open
    #app.wait_window(popup)  # Wait for the popup to be closed
    


def quit2():
    #quit()
    #sys.exit()
    #exit() # works?
    os._exit(0)

def config_gui():
    global thread_lock
    with thread_lock:
        #print('launching config gui...')
        global pause_bind
        global vol_up_bind
        global vol_down_bind
        global next_track_bind
        global prev_track_bind
        global like_track_bind
        global toggle_shuffle_bind
        global toggle_repeat_bind
        global seek_forw_bind
        global seek_backw_bind

        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")  

        app = ctk.CTk()
       # app.geometry("1100x450")
        app.resizable(False, False)
        app.title("Spotify Controls by _kreken")
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)

        app.sidebar_frame = ctk.CTkFrame(app, width=140, corner_radius=0)
        app.sidebar_frame.pack(fill="both", side=ctk.LEFT)
        app.sidebar_frame.grid_rowconfigure(4, weight=1)
        app.logo_label = ctk.CTkLabel(app.sidebar_frame, text="Spotify Controls", font=ctk.CTkFont(size=20))
        app.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        app.logo_label = ctk.CTkLabel(app.sidebar_frame, text="by _kreken", font=ctk.CTkFont(size=16))
        app.logo_label.grid(row=1, column=0, padx=20, pady=(5, 150))
        app.sidebar_button_1 = ctk.CTkButton(app.sidebar_frame, text="Credits", command=lambda: show_credits(app))
        app.sidebar_button_1.grid(row=4, column=0, padx=20, pady=10)
        app.sidebar_button_2 = ctk.CTkButton(app.sidebar_frame, text="Support Server", command=join_server)
        app.sidebar_button_2.grid(row=5, column=0, padx=20, pady=10)
        app.sidebar_button_3 = ctk.CTkButton(app.sidebar_frame, text="Reload", command=reload_program)
        app.sidebar_button_3.grid(row=6, column=0, padx=20, pady=10)
        app.sidebar_button_4 = ctk.CTkButton(app.sidebar_frame, text="Close", command=quit2)
        app.sidebar_button_4.grid(row=7, column=0, padx=20, pady=(10, 20))

    
        frame_1 = ctk.CTkFrame(master=app)
        frame_1.pack(pady=20, padx=60, fill="both", expand=True)

        macro1_label = ctk.CTkLabel(master=frame_1, text="pause: " + pause_bind)
        macro1_label.grid(row=1, column=0, padx=20, pady=(15, 0))
        macro1_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_pause, args=(macro1_label,)).start())
        macro1_button.grid(row=2, column=0, padx=20, pady=(0, 15))
    
        macro2_label = ctk.CTkLabel(master=frame_1, text="volume up: " + vol_up_bind)
        macro2_label.grid(row=3, column=0, padx=20, pady=(15, 0))
        macro2_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_vol_up, args=(macro2_label,)).start())
        macro2_button.grid(row=4, column=0, padx=20, pady=(0, 15))

        macro3_label = ctk.CTkLabel(master=frame_1, text="volume down: " + vol_down_bind)
        macro3_label.grid(row=5, column=0, padx=20, pady=(15, 0))
        macro3_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_vol_down, args=(macro3_label,)).start())
        macro3_button.grid(row=6, column=0, padx=20, pady=(0, 15))

        macro4_label = ctk.CTkLabel(master=frame_1, text="next track: " + next_track_bind)
        macro4_label.grid(row=1, column=1, padx=20, pady=(15, 0))
        macro4_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_next_track, args=(macro4_label,)).start())
        macro4_button.grid(row=2, column=1, padx=20, pady=(0, 15))

        macro5_label = ctk.CTkLabel(master=frame_1, text="previous track: " + prev_track_bind)
        macro5_label.grid(row=3, column=1, padx=20, pady=(15, 0))
        macro5_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_prev_track, args=(macro5_label,)).start())
        macro5_button.grid(row=4, column=1, padx=20, pady=(0, 15))

        macro6_label = ctk.CTkLabel(master=frame_1, text="like track: " + like_track_bind)
        macro6_label.grid(row=5, column=1, padx=20, pady=(15, 0))
        macro6_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_like_track, args=(macro6_label,)).start())
        macro6_button.grid(row=6, column=1, padx=20, pady=(0, 15))

        macro7_label = ctk.CTkLabel(master=frame_1, text="toggle shuffle: " + toggle_shuffle_bind)
        macro7_label.grid(row=1, column=2, padx=20, pady=(15, 0))
        macro7_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_toggle_shuffle, args=(macro7_label,)).start())
        macro7_button.grid(row=2, column=2, padx=20, pady=(0, 15))

        macro8_label = ctk.CTkLabel(master=frame_1, text="toggle repeat: " + toggle_repeat_bind)
        macro8_label.grid(row=3, column=2, padx=20, pady=(15, 0))
        macro8_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_toggle_repeat, args=(macro8_label,)).start())
        macro8_button.grid(row=4, column=2, padx=20, pady=(0, 15))

        macro9_label = ctk.CTkLabel(master=frame_1, text="seek forward: " + seek_forw_bind)
        macro9_label.grid(row=5, column=2, padx=20, pady=(15, 0))
        macro9_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_seek_forw, args=(macro9_label,)).start())
        macro9_button.grid(row=6, column=2, padx=20, pady=(0, 15))

        macro10_label = ctk.CTkLabel(master=frame_1, text="seek backward: " + seek_backw_bind)
        macro10_label.grid(row=1, column=3, padx=20, pady=(15, 0))
        macro10_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_seek_backw, args=(macro10_label,)).start())
        macro10_button.grid(row=2, column=3, padx=20, pady=(0, 15))

        for i in range(10):
            ##print("centering row: " + str(round(i/2)*2) + ', column: ' + str(i))
            frame_1.grid_rowconfigure(round(i/2)*2, weight=2)
            frame_1.grid_rowconfigure(round(i/2)*2+1, weight=2)
            frame_1.grid_columnconfigure(i, weight=2)

    

    
        app.mainloop()
    
    
def quit_window(tray_icon, item):
    tray_icon.stop()
    #exit()
    quit2()

def show_window(tray_icon, item):
    threading.Thread(target=config_gui, args=()).start()

def run_tray():
    #print('launching tray...')
    global tray_icon
    try:
        image_path = get_bundled_png_filepath("kreky.png")
        image = Image.open(image_path)
    except:
        image = Image.open("kreky.png")
    menu = (item('Open Settings', show_window), item('Close', quit_window))
    tray_icon = pystray.Icon("name", image, "spotify controls", menu)
    tray_icon.run()

def set_hotkeys():
    #print('setting up hotkeys...')
    global pause_bind
    global vol_up_bind
    global vol_down_bind
    global next_track_bind
    global prev_track_bind
    global like_track_bind
    global toggle_shuffle_bind
    global toggle_repeat_bind
    global seek_forw_bind
    global seek_backw_bind
    TOGGLE_PAUSE      =  '{VK_SPACE}'
    VOLUME_UP         =  '^{VK_UP}'
    VOLUME_DOWN       =  '^{VK_DOWN}'
    NEXT_TRACK 	      =  '^{VK_RIGHT}'
    PREV_TRACK 	      =  '^{VK_LEFT}'
    LIKE_TRACK        =  '!+{b}'
    TOGGLE_SHUFFLE 	  =  '^{s}'
    TOGGLE_REPEAT 	  =  '^{r}'
    SEEK_FORWD 	      =  '+{VK_RIGHT}'
    SEEK_BACKW 		  =  '+{VK_LEFT}'

    try:
        keyboard.unhook_all_hotkeys()
    except:
        pass
    if pause_bind != '':
        keyboard.add_hotkey(pause_bind,          lambda: sendKeysToSpotify(TOGGLE_PAUSE),    suppress=True, timeout=0, trigger_on_release=False )
        #print('set pause to ' + pause_bind)

    if vol_up_bind != '':
        keyboard.add_hotkey(vol_up_bind,         lambda: sendKeysToSpotify(VOLUME_UP),       suppress=True, timeout=0, trigger_on_release=False )
        #print('set volup to ' + vol_up_bind)

    if vol_down_bind != '':
        keyboard.add_hotkey(vol_down_bind,       lambda: sendKeysToSpotify(VOLUME_DOWN),     suppress=True, timeout=0, trigger_on_release=False )
        #print('set voldown to ' + vol_down_bind)

    if next_track_bind != '':
        keyboard.add_hotkey(next_track_bind,     lambda: sendKeysToSpotify(NEXT_TRACK),      suppress=True, timeout=0, trigger_on_release=False )
        #print('set next track to ' + next_track_bind)

    if prev_track_bind != '':
        keyboard.add_hotkey(prev_track_bind,     lambda: sendKeysToSpotify(PREV_TRACK),      suppress=True, timeout=0, trigger_on_release=False )
        #print('set prev track to ' + prev_track_bind)

    if like_track_bind != '':
        keyboard.add_hotkey(like_track_bind,     lambda: sendKeysToSpotify(LIKE_TRACK),      suppress=True, timeout=0, trigger_on_release=False )
        #print('set like track to ' + like_track_bind)

    if toggle_shuffle_bind != '':
        keyboard.add_hotkey(toggle_shuffle_bind, lambda: sendKeysToSpotify(TOGGLE_SHUFFLE),  suppress=True, timeout=0, trigger_on_release=False )
        #print('set shuffle to ' + toggle_shuffle_bind)

    if toggle_repeat_bind != '':
        keyboard.add_hotkey(toggle_repeat_bind,  lambda: sendKeysToSpotify(TOGGLE_REPEAT),   suppress=True, timeout=0, trigger_on_release=False )
        #print('set repeat to ' + toggle_repeat_bind)

    if seek_forw_bind != '':
        keyboard.add_hotkey(seek_forw_bind,      lambda: sendKeysToSpotify(SEEK_FORWD),      suppress=True, timeout=0, trigger_on_release=False )
        #print('set seek forward to ' + seek_forw_bind)

    if seek_backw_bind != '':
        keyboard.add_hotkey(seek_backw_bind,     lambda: sendKeysToSpotify(SEEK_BACKW),      suppress=True, timeout=0, trigger_on_release=False )
        #print('set seek back to ' + seek_backw_bind)

    #keyboard.add_hotkey( 'ctrl+m', spotifyHide, args = ( ) )





def main():
    #print('wow this is from the top of main')
    global pause_bind
    global vol_up_bind
    global vol_down_bind
    global next_track_bind
    global prev_track_bind
    global like_track_bind
    global toggle_shuffle_bind
    global toggle_repeat_bind
    global seek_forw_bind
    global seek_backw_bind

    pause_bind = ''
    vol_up_bind = ''
    vol_down_bind = ''
    next_track_bind = ''
    prev_track_bind = ''
    like_track_bind = ''
    toggle_shuffle_bind = ''
    toggle_repeat_bind = ''
    seek_forw_bind = ''
    seek_backw_bind = ''

    global thread_lock
    thread_lock = threading.Lock()
    
    if os.path.isfile('spotify_controls.ini'):
        #print('config file found')
        #print('reading config...')
        readConfig()
        set_hotkeys()
    else:
        #print('config file not found')
        threading.Thread(target=config_gui, args=()).start()

    run_tray()
    global tray_icon
    tray_icon.stop()


if __name__ == "__main__":
    main()