import os
import subprocess
import sys
import threading
import time
import psutil
from inputs import get_gamepad
import shutil
import stat
import customtkinter as ctk
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from io import BytesIO

# Load config from JSON
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Load Steam ID from steam.json
def load_steam_id():
    try:
        with open("steam.json", "r") as f:
            data = json.load(f)
            return data.get("steam_id", "")
    except Exception as e:
        print(f"Failed to load steam.json: {e}")
        return ""

STEAM_ID = load_steam_id()
if not STEAM_ID:
    print("Warning: Steam ID not found in steam.json. Please add your Steam ID!")

COD_MW_APP_ID = '2000950'

# flag to track if game is running
game_running = threading.Event()

def hang_while_game_running():
    time.sleep(16)
    while True:
        running = any(
            proc.info['name'] in ["ModernWarfare.exe", "game_dx12_ship_replay.exe"]
            for proc in psutil.process_iter(['name'])
        )
        if running:
            time.sleep(5)
        else:
            break
    game_running.clear()

def change_permissions_for_deletion(folder):
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                os.chmod(filepath, stat.S_IWRITE)
            except Exception as e:
                print(f"Failed to change permissions for file {filepath}: {e}")
        for name in dirs:
            dirpath = os.path.join(root, name)
            try:
                os.chmod(dirpath, stat.S_IWRITE)
            except Exception as e:
                print(f"Failed to change permissions for folder {dirpath}: {e}")
    try:
        os.chmod(folder, stat.S_IWRITE)
    except Exception as e:
        print(f"Failed to change permissions for folder {folder}: {e}")

def copy_folder(src, dst):
    print(f"Starting copy from {src} to {dst}")
    if not os.path.exists(src):
        print(f"Source folder {src} does not exist! Skipping copy.")
        return
    if not os.path.exists(dst):
        os.makedirs(dst)
        print(f"Created destination folder {dst}")
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, rel_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            print(f"Created subfolder {dest_dir}")
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            try:
                try:
                    with open(src_file, 'rb') as f:
                        f.read(1)
                except Exception as e:
                    print(f"Failed to hydrate {src_file}: {e}")
                shutil.copy2(src_file, dest_file)
                print(f"Copying file {src_file} to {dest_file}")
            except Exception as e:
                print(f"Failed to copy {src_file} to {dest_file}: {e}")

def update_status(message):
    status_label.configure(text=message)

def launch_game(choice):
    global game_running

    if game_running.is_set():
        update_status("Game already running! Close it first.")
        return

    if choice not in CONFIG:
        update_status("Invalid game choice!")
        return

    game_running.set()
    update_status("Launching game, please wait...")

    def game_thread():
        try:
            version_data = CONFIG[choice]
            path = version_data["path"]
            exe = version_data["exe"]
            shared_folder = version_data["save"]
            version_folder = version_data["backup"]

            if os.path.exists(shared_folder):
                print("Backing up current save data...")
                try:
                    if not os.path.exists(version_folder):
                        os.makedirs(version_folder)
                    copy_folder(shared_folder, version_folder)
                except Exception as e:
                    print(f"Backup failed: {e}")

            try:
                if os.path.exists(shared_folder):
                    print(f"Removing folder {shared_folder} with permission fixes...")
                    change_permissions_for_deletion(shared_folder)
                    shutil.rmtree(shared_folder)
                    print("Folder removed successfully.")
                if os.path.exists(version_folder):
                    copy_folder(version_folder, shared_folder)
                print(f"Prepared save data for {choice}")
            except Exception as e:
                print(f"Folder prep failed: {e}")
                update_status("Error preparing save data.")
                game_running.clear()
                return

            try:
                if exe is None:
                    os.startfile(path)
                else:
                    full_path = os.path.join(path, exe)
                    subprocess.Popen([full_path], cwd=path)
                update_status(f"Launched version {choice}!")
            except Exception as e:
                print(f"Failed to launch: {e}")
                update_status("Failed to launch game.")
                game_running.clear()
                return

            hang_while_game_running()

            try:
                print(f"Saving {choice} progress...")
                if not os.path.exists(version_folder):
                    os.makedirs(version_folder)
                copy_folder(shared_folder, version_folder)
                change_permissions_for_deletion(shared_folder)
                shutil.rmtree(shared_folder)
                update_status("Game closed. Ready to launch again!")
            except Exception as e:
                print(f"Cleanup failed: {e}")
                update_status("Cleanup failed after game close.")

        finally:
            game_running.clear()

    threading.Thread(target=game_thread, daemon=True).start()

version_order = list(CONFIG.keys())
current_selection = 0
buttons = {}

def update_ui_selection():
    for i, key in enumerate(version_order):
        if i == current_selection:
            buttons[key].configure(fg_color="blue", text_color="white")
        else:
            buttons[key].configure(fg_color="gray20", text_color="lightgray")

def on_button_click(choice):
    threading.Thread(target=lambda: (launch_game(choice), update_status(f"Launched {choice} version!")), daemon=True).start()

def controller_navigation(event_code, event_state):
    global current_selection
    if event_code == "ABS_HAT0Y":
        if event_state == -1:
            current_selection = (current_selection - 1) % len(version_order)
            update_ui_selection()
            time.sleep(0.2)
        elif event_state == 1:
            current_selection = (current_selection + 1) % len(version_order)
            update_ui_selection()
            time.sleep(0.2)
    elif event_code == "ABS_Y":
        if event_state > 10000:
            current_selection = (current_selection - 1) % len(version_order)
            update_ui_selection()
            time.sleep(0.2)
        elif event_state < -10000:
            current_selection = (current_selection + 1) % len(version_order)
            update_ui_selection()
            time.sleep(0.2)
    elif event_code == "BTN_SOUTH" and event_state == 1:
        selected = version_order[current_selection]
        on_button_click(selected)

def listen_controller():
    while True:
        if game_running.is_set():
            time.sleep(1)
            continue
        events = get_gamepad()
        for event in events:
            if event.ev_type in ["Key", "Absolute"]:
                controller_navigation(event.code, event.state)

# -------------- STEAM PROFILE & ACHIEVEMENTS SCRAPER --------------

def get_steam_profile(steam_id):
    url = f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        from xml.etree import ElementTree as ET
        root = ET.fromstring(resp.content)
        name = root.findtext('steamID')
        avatar = root.findtext('avatarMedium')
        return {'name': name, 'avatar': avatar}
    except Exception as e:
        print(f"Error fetching steam profile: {e}")
        return None

def get_steam_achievements(steam_id, app_id=COD_MW_APP_ID):
    url = f'https://steamcommunity.com/profiles/{steam_id}/stats/{app_id}/?tab=achievements'
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch achievements page: {e}")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    achievements = []

    for div in soup.find_all('div', class_='achieveRow'):
        title_div = div.find('h3')
        unlocked = 'achieved' in div.get('class', []) or div.find('div', class_='achieveUnlockTime') is not None
        icon_img = div.find('img')

        title = title_div.text.strip() if title_div else "Unknown Achievement"
        icon_url = icon_img['src'] if icon_img else ""

        achievements.append({
            'title': title,
            'unlocked': unlocked,
            'icon': icon_url
        })

    return achievements

def load_steam_profile_ui():
    profile = get_steam_profile(STEAM_ID)
    if profile:
        steam_name = profile['name']
        steam_avatar_url = profile['avatar']

        def load_avatar():
            try:
                resp = requests.get(steam_avatar_url)
                resp.raise_for_status()
                img_data = resp.content
                img = Image.open(BytesIO(img_data))
                img = img.resize((64, 64))
                avatar_img = ImageTk.PhotoImage(img)

                def update_avatar():
                    avatar_label.configure(image=avatar_img)
                    avatar_label.image = avatar_img

                app.after(0, update_avatar)
            except Exception as e:
                print(f"Failed to load avatar image: {e}")

        threading.Thread(target=load_avatar, daemon=True).start()

        steam_name_label.configure(text=f"Steam Achievements")
        welcome_label.configure(text=f"Welcome, {steam_name}."
        def load_achievements():
            achs = get_steam_achievements(STEAM_ID)
            def update_achievements():
                for widget in achievements_frame.winfo_children():
                    widget.destroy()
                if not achs:
                    ctk.CTkLabel(achievements_frame, text="No achievements found or profile private.").pack()
                    return
                for ach in achs:
                    status = "✅" if ach['unlocked'] else "❌"
                    text = f"{status} {ach['title']}"
                    ctk.CTkLabel(achievements_frame, text=text, anchor="w").pack(fill='x', pady=2)
            app.after(0, update_achievements)

        threading.Thread(target=load_achievements, daemon=True).start()
    else:
        steam_name_label.configure(text="Steam profile not found.")
        welcome_label.configure(text="")
        avatar_label.configure(image=None)

# -------------- UI SETUP --------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("COD MW Launcher")
app.geometry("700x600")

title_label = ctk.CTkLabel(app, text="Call of Duty Modern Warfare Launcher", font=("Segoe UI", 20, "bold"))
title_label.place(x=20, y=10)

instruction_label = ctk.CTkLabel(app, text="Navigate with D-Pad / Left Joystick, launch with A", font=("Segoe UI", 14))
instruction_label.place(x=20, y=50)

avatar_label = ctk.CTkLabel(app, text="", width=64, height=64)
avatar_label.place(x=620, y=10)

steam_name_label = ctk.CTkLabel(app, font=("Arial", 14))
steam_name_label.place(x=480, y=75)

achievements_frame = ctk.CTkScrollableFrame(app, width=300, height=400)
achievements_frame.place(x=380, y=110)

welcome_label = ctk.CTkLabel(app, font=("Arial", 12, "italic"))
welcome_label.place(x=380, y=520)

button_frame = ctk.CTkFrame(app, width=300, height=500) 
button_frame.place(x=20, y=90)

for i, version in enumerate(version_order):
    btn = ctk.CTkButton(button_frame, text=version, width=260, height=40,
                        fg_color="gray20", text_color="lightgray",
                        command=lambda v=version: on_button_click(v))
    btn.place(x=20, y=10 + i * 50)
    buttons[version] = btn

status_label = ctk.CTkLabel(app, text="Ready!", anchor="w", width=660)
status_label.place(x=20, y=570)

update_ui_selection()
load_steam_profile_ui()

# Start controller listening thread
threading.Thread(target=listen_controller, daemon=True).start()

app.mainloop()
