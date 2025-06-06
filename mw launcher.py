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

# Load config from JSON
with open("config.json", "r") as f:
    CONFIG = json.load(f)

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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("MW Launcher (Xinput Support)")
app.geometry("500x650")

ctk.CTkLabel(app, text="Call of Duty Modern Warfare Launcher", font=("Segoe UI", 20, "bold")).pack(pady=15)
ctk.CTkLabel(app, text="Navigate with D-Pad / Left Joystick, launch with A", font=("Segoe UI", 14)).pack(pady=5)

for version in version_order:
    label = version if version != "steam" else "Steam (latest)"
    buttons[version] = ctk.CTkButton(app, text=label, command=lambda v=version: on_button_click(v), width=300)
    buttons[version].pack(pady=5)

status_label = ctk.CTkLabel(app, text="Ready to launch!", font=("Segoe UI", 14, "italic"))
status_label.pack(pady=20)

update_ui_selection()
threading.Thread(target=listen_controller, daemon=True).start()
app.mainloop()
