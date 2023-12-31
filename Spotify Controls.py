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
from PIL import Image, ImageTk
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageTk
import numpy as np
from PIL import Image

#import win32api
#from time import sleep
#import win32ui
#import win32con
#import pyautogui
#import importlib
#from timeout_decorator import timeout

def gen_gradient_image(width, height, colorArr1, colorArr2):
    # Make output image
    gradient = np.zeros((height, width, 3), np.uint8)

    # Fill R, G and B channels with linear gradient between two end colours
    gradient[:,:,0] = np.linspace(colorArr1[0], colorArr2[0], width, dtype=np.uint8)
    gradient[:,:,1] = np.linspace(colorArr1[1], colorArr2[1], width, dtype=np.uint8)
    gradient[:,:,2] = np.linspace(colorArr1[2], colorArr2[2], width, dtype=np.uint8)

    # Save result
    img = Image.fromarray(gradient)
    return img


def show_toast_notification():
    global SPOTIPY_CLIENT_ID
    global SPOTIPY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI

    # Creating the Spotify client with authorization
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                       client_secret=SPOTIPY_CLIENT_SECRET,
                                                       redirect_uri=SPOTIPY_REDIRECT_URI,
                                                       scope='user-read-playback-state'))

    # Create a hidden root window
    # Change the border color (frame color)
    ctk.set_default_color_theme("green")  
    root = ctk.CTk()
    root.withdraw()

    # Create the notification window
    notification_window = ctk.CTkToplevel()
    notification_window.configure(background='black')
    notification_window.geometry("280x100")  # Adjust the size as needed
    notification_window.overrideredirect(True)  # Remove window borders and title

    # Calculate the screen width and height
    #screen_width = root.winfo_screenwidth() - 100
    #screen_height = root.winfo_screenheight() + 50

    # Position the notification in the bottom-right corner
    #x = screen_width - notification_window.winfo_reqwidth()
    #y = screen_height - notification_window.winfo_reqheight()
    x = 0
    y = 0
    notification_window.geometry("+%d+%d" % (x, y))

    # Getting current playing song
    current_track = sp.current_user_playing_track()
    current_playback = sp.current_playback()
    track_name = current_track['item']['name']
    artist_name = current_track['item']['artists'][0]['name']

    # to get transparency 
    #canvas = ctk.CTkCanvas(notification_window, background='black', borderwidth = 0, highlightthickness = 0)
    canvas = ctk.CTkCanvas(notification_window, background='black', highlightbackground='black')
    # Define start and end colours and image height and width
    # colorArr1=[30, 215, 96] # spotiy colors
    colorArr1=[7, 53, 24]
    colorArr2=[0, 0, 0]
    bg_img = gen_gradient_image(350, 130, colorArr1, colorArr2)
    bg_img = ImageTk.PhotoImage(bg_img)
    #bg_img = bg_img.resize((100, 100), Image.LANCZOS) # Resize image
    # display bg image
    canvas.create_image(0, 0, image=bg_img, anchor=ctk.NW)
    # Getting album cover image URL
    album_cover_url = current_track['item']['album']['images'][0]['url']
    img = Image.open(requests.get(album_cover_url, stream=True).raw)
    img = img.resize((100, 100), Image.LANCZOS) # Resize image
    album_cover = ImageTk.PhotoImage(img)
    # Displaying album cover image
    canvas.create_image(10, 10, image=album_cover, anchor=ctk.NW)

    # Check if the current track is liked (hearted):
    #liked_tracks = sp.current_user_saved_tracks()
    #liked_track_ids = [track['track']['id'] for track in liked_tracks['items']]
    #if track_id in liked_track_ids:
    #    print("Track is liked by the user.")
    #else:
    #    print("Track is not liked by the user.")

    # TODO
    heart = load_png('heart_empty.png')
    heart = heart.resize((25, 25), Image.LANCZOS) # Resize image
    heart = ImageTk.PhotoImage(heart)
    canvas.create_image(130, 80, image=heart, anchor=ctk.NW)

    shuffle = current_playback['shuffle_state']
    if shuffle == False:
        shuffle = load_png('shuffle_off.png')
    elif shuffle == True:
        shuffle = load_png('shuffle_on.png')
    shuffle = shuffle.resize((25, 25), Image.LANCZOS) # Resize image
    shuffle = ImageTk.PhotoImage(shuffle)
    canvas.create_image(165, 80, image=shuffle, anchor=ctk.NW)

    is_playing = current_playback['is_playing']
    if is_playing == True:
        play_pause = load_png('pause.png')
    if is_playing == False:
        play_pause = load_png('play.png')
    play_pause = play_pause.resize((25, 25), Image.LANCZOS) # Resize image
    play_pause = ImageTk.PhotoImage(play_pause)
    canvas.create_image(200, 80, image=play_pause, anchor=ctk.NW)

    loop = current_playback['repeat_state']
    if loop == 'off':
        loop = load_png('loop_off.png')
    elif loop == 'context':
        loop = load_png('loop_on.png')
    elif loop == 'track':
        loop = load_png('loop_single.png')
    loop = loop.resize((25, 25), Image.LANCZOS) # Resize image
    loop = ImageTk.PhotoImage(loop)
    canvas.create_image(235, 80, image=loop, anchor=ctk.NW)

    # Displaying currently playing song info
    canvas.create_text(130, 20, text=f"{track_name}\nby: {artist_name}", font=(20), fill='white', anchor=ctk.NW)

    canvas.pack(side='left')
    notification_window.after(3000, notification_window.destroy)  # Change the time as needed
    root.after(3000, root.destroy)
    root.mainloop()


def get_bundled_file_filepath(filename):
# Get the path to the temporary directory where data is extracted
    data_dir = sys._MEIPASS
    
    # Construct the full path to the bundled .png file
    png_file_path = os.path.join(data_dir, "data", filename)

    return png_file_path


# TODO finish this
def load_png(filename):
    try:
        # Attempt to load an image from a bundled file
        image_path = get_bundled_file_filepath(filename)
        image = Image.open(image_path)
    except:
        # If loading from the bundled file fails, load from the folder (assume to run as script not compiled)
        image = Image.open('resources/' + filename)
    return image
    

# Create a ConfigParser object
config = configparser.ConfigParser()
def set_config():
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
    global SPOTIPY_CLIENT_ID
    global SPOTIPY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI

    # Check if the 'spotify_controls.ini' file exists
    # If it doesn't exist, create it and set the initial configuration
    config['hotkeys'] = {'pause_bind': pause_bind.bind,
                        'vol_up_bind': vol_up_bind.bind,
                        'vol_down_bind': vol_down_bind.bind,
                        'next_track_bind': next_track_bind.bind,
                        'prev_track_bind': prev_track_bind.bind,
                        'like_track_bind': like_track_bind.bind,
                        'toggle_shuffle_bind': toggle_shuffle_bind.bind,
                        'toggle_repeat_bind': toggle_repeat_bind.bind,
                        'seek_forw_bind': seek_forw_bind.bind,
                        'seek_backw_bind': seek_backw_bind.bind
                        }
    config['spotify_creds'] = {'SPOTIPY_CLIENT_ID' : SPOTIPY_CLIENT_ID,
                                'SPOTIPY_CLIENT_SECRET' : SPOTIPY_CLIENT_SECRET,
                                'SPOTIPY_REDIRECT_URI' : SPOTIPY_REDIRECT_URI
                                }

    # Write the configuration to the 'spotify_controls.ini' file
    with open('spotify_controls.ini', 'w') as configfile:
        config.write(configfile)


def readConfig():
    # Define global variables that will store the configuration values
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
    global SPOTIPY_CLIENT_ID
    global SPOTIPY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI
    
    # Read the configuration from 'spotify_controls.ini' file
    config.read('spotify_controls.ini')
    
    # Access the 'hotkeys' section in the configuration
    hotkeys = config['hotkeys']

    # Retrieve and assign the values of each configuration setting
    pause_bind.bind = hotkeys['pause_bind']
    vol_up_bind.bind = hotkeys['vol_up_bind']
    vol_down_bind.bind = hotkeys['vol_down_bind']
    next_track_bind.bind = hotkeys['next_track_bind']
    prev_track_bind.bind = hotkeys['prev_track_bind']
    like_track_bind.bind = hotkeys['like_track_bind']
    toggle_shuffle_bind.bind = hotkeys['toggle_shuffle_bind']
    toggle_repeat_bind.bind = hotkeys['toggle_repeat_bind']
    seek_forw_bind.bind = hotkeys['seek_forw_bind']
    seek_backw_bind.bind = hotkeys['seek_backw_bind']

    spotify_creds = config['spotify_creds']
    SPOTIPY_CLIENT_ID = spotify_creds['SPOTIPY_CLIENT_ID']
    SPOTIPY_CLIENT_SECRET = spotify_creds['SPOTIPY_CLIENT_SECRET']
    SPOTIPY_REDIRECT_URI = spotify_creds['SPOTIPY_REDIRECT_URI']
    
        
def get_pid_from_hwnd(hwnd):
    # Create a variable to store the process ID
    process_id = ctypes.wintypes.DWORD()

    # Call the Windows API function to get the process ID associated with the given window handle
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

    # Return the process ID as an integer value
    return process_id.value

def send_keys_to_spotify(keys):
    #threading.Thread(target=show_toast_notification).start()
    # Get window handles for all running windows of Spotify
    hwnds = get_window_hwnds_by_executable_name('spotify.exe')

    # Choose the first Spotify window 
    hwnd = hwnds[0] 

    # Check if a valid window handle was obtained
    if ((hwnd != 0) and (hwnd != None)):
        # Get the process ID associated with the window handle
        pid = get_pid_from_hwnd(hwnd)

        # Connect to the Spotify application using the process ID
        # pid because spotify is chromium based so window class or similar would match anything chromium
        # also title changes depending on song playing
        app = pywinauto.Application().connect(process=pid)

        # Set keyboard focus to the Spotify window
        # im kinda mad about this, its not part of the keyboard docs in pywinauto
        # just hidden in a random part of the docs
        window = app.Chrome_WidgetWin_0.set_keyboard_focus()

        # Send the specified keys to the Spotify window 
        window.send_keystrokes(keys, with_spaces=True, with_tabs=True, with_newlines=True)
        threading.Thread(target=show_toast_notification).start()

    
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
                
                # Close the process handle
                ctypes.windll.kernel32.CloseHandle(h_process)

                # Check if the current window's executable name matches the target name
                if executable_name.lower() == target_executable_name.lower():
                    #print("returned hwnd: " + str(hwnd) + " for exe: " + executable_name + "(" + str(pid) + ")")
                    window_hwnd.append(hwnd) 
        except Exception as e:
            pass
        return True 
    # Enumerate all top-level windows and filter by executable name
    win32gui.EnumWindows(enum_windows_callback, 0)
    return window_hwnd
    
    
def spotifyHide():
    # this isnt ready yet, 
    # will be used to stop spotify from popping up if it was minimized when send_keys_to_spotify was called
    # TODO: fix this
    #print("spotify hide")
    hwnds = get_window_hwnds_by_executable_name('spotify.exe')
    #print('hwnds: ' + str(hwnds))
    #SW_HIDE = 0
    #SW_RESTORE = 9
    #SW_SHOW = 5
    SW_MINIMIZE = 6
    for hwnd in hwnds:
        ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)

class hotkey:
    def __init__(self):
        self.bind = '' 

def bind_keys(label, label_text, hotkey_class, result_event=None):
    # Update the label with user instructions
    label.configure(text="Press keys to bind...")
    # Initialize a variable to store the key binding
    hotkey_class.bind = ''
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            # check if key was already added to hotkey
            if hotkey_class.bind.find(event.name) == -1:
                # if not found add the key
                hotkey_class.bind += '+' + event.name
                if hotkey_class.bind[0] == '+':
                    hotkey_class.bind = hotkey_class.bind[1:]

        if event.event_type == keyboard.KEY_UP:
            break

        # Update the label with the current key binding
        label.configure(text=label_text + hotkey_class.bind)
    set_hotkeys()
    set_config()


def join_server():
    # Open a web browser and navigate to the specified URL
    webbrowser.open("https://thrallway.com")

def reload_program():
    # Get the name of the current script
    current_script = sys.argv[0]  
    # Create a subprocess to start the script again 
    subprocess.Popen([sys.executable, current_script])
    # end currant script instance
    quit2()
    
def show_credits(app):
    # Create a pop-up window
    popup = ctk.CTkToplevel(app)
    popup.title("Credits")
    popup.geometry("200x120+200+200")  # Adjust the size and position as needed
    popup.resizable(False, False) # Make the popup window non-resizable

    # Create a label to display credits
    popup.label = ctk.CTkLabel(
        master=popup, font=ctk.CTkFont(size=15), 
        text="made with the help of:\n- LeopoldPrime\n- SniperAstra\n- Zenith"
        )
    popup.label.pack(fill=ctk.BOTH, expand=True)

    popup.transient(app)  # Makes the popup related to the main window
    popup.grab_set()  # Prevents interaction with the main window while the popup is open
    #app.wait_window(popup)  # Wait for the popup to be closed
    


def quit2():
    # i have no clue why but all other methods of exiting either froze the exe, script, or both
    os._exit(0)

def config_gui():
    global thread_lock
    # make sure only one gui thread is running at a time
    with thread_lock:
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

        # Initialize and configure the graphical user interface
        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("green")  

        # Create the main application window
        app = ctk.CTk()
        app.resizable(False, False)
        app.title("Spotify Controls by _kreken")
        try:
            filepath = get_bundled_file_filepath('kreky.ico')
            app.wm_iconbitmap(filepath)
        except:
            app.wm_iconbitmap('resources/kreky.ico')
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)

        # Create a sidebar for additional stuff
        app.sidebar_frame = ctk.CTkFrame(app, width=140, corner_radius=0)
        app.sidebar_frame.pack(fill="both", side=ctk.LEFT)
        app.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Create labels, buttons, and links in the sidebar
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

    
        # Create a main frame for configuring hotkeys
        frame_1 = ctk.CTkFrame(master=app)
        frame_1.pack(pady=20, padx=60, fill="both", expand=True)

        # Create labels and buttons for each hotkey configuration
        macro1_label = ctk.CTkLabel(master=frame_1, text="pause: " + pause_bind.bind)
        macro1_label.grid(row=1, column=0, padx=20, pady=(15, 0))
        macro1_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro1_label, "pause: ", pause_bind)).start())
        macro1_button.grid(row=2, column=0, padx=20, pady=(0, 15))
    
        macro2_label = ctk.CTkLabel(master=frame_1, text="volume up: " + vol_up_bind.bind)
        macro2_label.grid(row=3, column=0, padx=20, pady=(15, 0))
        macro2_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro2_label, "volume up: ", vol_up_bind)).start())
        macro2_button.grid(row=4, column=0, padx=20, pady=(0, 15))

        macro3_label = ctk.CTkLabel(master=frame_1, text="volume down: " + vol_down_bind.bind)
        macro3_label.grid(row=5, column=0, padx=20, pady=(15, 0))
        macro3_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro3_label, "volume down: ", vol_down_bind)).start())
        macro3_button.grid(row=6, column=0, padx=20, pady=(0, 15))

        macro4_label = ctk.CTkLabel(master=frame_1, text="next track: " + next_track_bind.bind)
        macro4_label.grid(row=1, column=1, padx=20, pady=(15, 0))
        macro4_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro4_label, "next track: ", next_track_bind)).start())
        macro4_button.grid(row=2, column=1, padx=20, pady=(0, 15))

        macro5_label = ctk.CTkLabel(master=frame_1, text="previous track: " + prev_track_bind.bind)
        macro5_label.grid(row=3, column=1, padx=20, pady=(15, 0))
        macro5_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro5_label, "previous track: ", prev_track_bind)).start())
        macro5_button.grid(row=4, column=1, padx=20, pady=(0, 15))

        macro6_label = ctk.CTkLabel(master=frame_1, text="like track: " + like_track_bind.bind)
        macro6_label.grid(row=5, column=1, padx=20, pady=(15, 0))
        macro6_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro6_label, "like track: ", like_track_bind)).start())
        macro6_button.grid(row=6, column=1, padx=20, pady=(0, 15))

        macro7_label = ctk.CTkLabel(master=frame_1, text="toggle shuffle: " + toggle_shuffle_bind.bind)
        macro7_label.grid(row=1, column=2, padx=20, pady=(15, 0))
        macro7_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro7_label, "toggle shuffle: ", toggle_shuffle_bind)).start())
        macro7_button.grid(row=2, column=2, padx=20, pady=(0, 15))

        macro8_label = ctk.CTkLabel(master=frame_1, text="toggle repeat: " + toggle_repeat_bind.bind)
        macro8_label.grid(row=3, column=2, padx=20, pady=(15, 0))
        macro8_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro8_label, "toggle repeat: ", toggle_repeat_bind)).start())
        macro8_button.grid(row=4, column=2, padx=20, pady=(0, 15))

        macro9_label = ctk.CTkLabel(master=frame_1, text="seek forward: " + seek_forw_bind.bind)
        macro9_label.grid(row=5, column=2, padx=20, pady=(15, 0))
        macro9_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro9_label, "seek forward: ", seek_forw_bind)).start())
        macro9_button.grid(row=6, column=2, padx=20, pady=(0, 15))

        macro10_label = ctk.CTkLabel(master=frame_1, text="seek backward: " + seek_backw_bind.bind)
        macro10_label.grid(row=1, column=3, padx=20, pady=(15, 0))
        macro10_button = ctk.CTkButton(master=frame_1, text="Bind Key", command=lambda: threading.Thread(target=bind_keys, args=(macro10_label, "seek forward: ", seek_backw_bind)).start())
        macro10_button.grid(row=2, column=3, padx=20, pady=(0, 15))

        # allign so it looks good
        for i in range(10):
            frame_1.grid_rowconfigure(round(i/2)*2, weight=2)
            frame_1.grid_rowconfigure(round(i/2)*2+1, weight=2)
            frame_1.grid_columnconfigure(i, weight=2)
    
        # Start the main application loop
        app.mainloop()
    
    
def quit_window(tray_icon, item):
    # Stop the tray to prevent weird behavior
    tray_icon.stop()
    quit2()

def show_window(tray_icon, item):
    # start config gui thread
    threading.Thread(target=config_gui, args=()).start()

def run_tray():
    # Create the system tray icon and menu
    global tray_icon
    image = load_png('kreky.png')
    # Define the menu items for the system tray icon
    menu = (item('Open Settings', show_window), item('Close', quit_window))
    # Create the system tray icon with the specified image and menu items
    tray_icon = pystray.Icon("name", image, "spotify controls", menu)
    # Start running the system tray icon
    tray_icon.run()

def set_hotkeys():
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
    
    # define hotkeys that spotify can receive
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
        # Unhook any previously set hotkeys
        keyboard.unhook_all_hotkeys()
    except:
        pass

    if pause_bind.bind != '':
        # Add hotkey for toggling pause with the specified key combination... same thing for other ones, won't comment
        keyboard.add_hotkey(pause_bind.bind,          lambda: send_keys_to_spotify(TOGGLE_PAUSE),    suppress=True, timeout=0, trigger_on_release=False )

    if vol_up_bind.bind != '':
        keyboard.add_hotkey(vol_up_bind.bind,         lambda: send_keys_to_spotify(VOLUME_UP),       suppress=True, timeout=0, trigger_on_release=False )

    if vol_down_bind.bind != '':
        keyboard.add_hotkey(vol_down_bind.bind,       lambda: send_keys_to_spotify(VOLUME_DOWN),     suppress=True, timeout=0, trigger_on_release=False )

    if next_track_bind.bind != '':
        keyboard.add_hotkey(next_track_bind.bind,     lambda: send_keys_to_spotify(NEXT_TRACK),      suppress=True, timeout=0, trigger_on_release=False )

    if prev_track_bind.bind != '':
        keyboard.add_hotkey(prev_track_bind.bind,     lambda: send_keys_to_spotify(PREV_TRACK),      suppress=True, timeout=0, trigger_on_release=False )

    if like_track_bind.bind != '':
        keyboard.add_hotkey(like_track_bind.bind,     lambda: send_keys_to_spotify(LIKE_TRACK),      suppress=True, timeout=0, trigger_on_release=False )

    if toggle_shuffle_bind.bind != '':
        keyboard.add_hotkey(toggle_shuffle_bind.bind, lambda: send_keys_to_spotify(TOGGLE_SHUFFLE),  suppress=True, timeout=0, trigger_on_release=False )

    if toggle_repeat_bind.bind != '':
        keyboard.add_hotkey(toggle_repeat_bind.bind,  lambda: send_keys_to_spotify(TOGGLE_REPEAT),   suppress=True, timeout=0, trigger_on_release=False )

    if seek_forw_bind.bind != '':
        keyboard.add_hotkey(seek_forw_bind.bind,      lambda: send_keys_to_spotify(SEEK_FORWD),      suppress=True, timeout=0, trigger_on_release=False )

    if seek_backw_bind.bind != '':
        keyboard.add_hotkey(seek_backw_bind.bind,     lambda: send_keys_to_spotify(SEEK_BACKW),      suppress=True, timeout=0, trigger_on_release=False )


def main():
    # Initialize global variables for hotkey bindings
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
    global config
    global SPOTIPY_CLIENT_ID
    global SPOTIPY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI

    
    # obv dont do it HERE, put it in the config file
    SPOTIPY_CLIENT_ID = 'put you client id here'
    SPOTIPY_CLIENT_SECRET = 'put you client secret here'
    SPOTIPY_REDIRECT_URI = 'put you redirect uri here'

    # Initialize hotkey bindings to empty strings (prevents error when saving empty hotkeys to config)
    pause_bind = hotkey()
    vol_up_bind = hotkey() 
    vol_down_bind = hotkey()
    next_track_bind = hotkey()
    prev_track_bind = hotkey()
    like_track_bind = hotkey()
    toggle_shuffle_bind = hotkey()
    toggle_repeat_bind = hotkey()
    seek_forw_bind = hotkey()
    seek_backw_bind = hotkey()

    # Create a lock for gui thread synchronization
    global thread_lock
    thread_lock = threading.Lock()
    
    threading.Thread(target=config_gui, args=()).start() # debug reasons
    # Check if the configuration file exists
    #if os.path.isfile('spotify_controls.ini'):
        #readConfig()
        # set hotkeys to config
    #    set_hotkeys()
    #else:
        # Configuration file doesn't exist, so launch the config GUI in a separate thread
    #    threading.Thread(target=config_gui, args=()).start()

    # Run the system tray icon
    run_tray()

    # idk why but it would randomly freeze or exit without this part
    global tray_icon
    tray_icon.stop()


if __name__ == "__main__":
    main()