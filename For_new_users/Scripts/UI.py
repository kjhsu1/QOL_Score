#!/usr/bin/env python3

import requests
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, font
from tkinter import scrolledtext
import tkinter.font as tkFont
from datetime import datetime, timedelta
import pytz
import os
import threading
import subprocess
import random
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import QOL_LIB # my homemade library 


# !!!!!! CHANGE THIS FOR OTHER USERS !!!!!!!
user = "Kenta"

# dict with all user info
# includes "User Analysis Requests" database
all_users = {
    "Kenta": {
        "NOTION_TOKEN": "YOUR_NOTION_TOKEN_HERE",
        "DATABASE_ID": "1924d9b143a980719cabc4f151bc30fb"
    },

    "Kazuma":{
        "NOTION_TOKEN": "YOUR_NOTION_TOKEN_HERE",
        "DATABASE_ID": "1954d9b143a981019212fbe32c21a6a1" 
    },

    "Eoin":{
        "NOTION_TOKEN": "YOUR_NOTION_TOKEN_HERE",
        "DATABASE_ID": "1f44d9b143a980559a2bffbe8e7ab9b5" 
    },

    "User_Analysis_Requests_Database":{
        "NOTION_TOKEN": "YOUR_NOTION_TOKEN_HERE",
        "DATABASE_ID": "1ad4d9b143a980e7806ece9c6a0eb626"
    }

}

# assuming you git clone directory in Downloads...
# first_part_of_path = "/Applications/QOL_Score/For_new_users_v2"

# directory that this file is in
base_dir = os.path.dirname(os.path.abspath(__file__))

DATABASE_ID = all_users[user]["DATABASE_ID"]
NOTION_TOKEN = all_users[user]["NOTION_TOKEN"]
# Analysis Request Database
AR_DATABASE_ID = all_users["User_Analysis_Requests_Database"]["DATABASE_ID"]
AR_NOTION_TOKEN = all_users["User_Analysis_Requests_Database"]["NOTION_TOKEN"]

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# header for Analysis Requests Database
ar_headers = {
    "Authorization": "Bearer " + AR_NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_highest_entry_number():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    max_entry_number = 0
    has_more = True
    start_cursor = None
    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
        except Exception as e:
            raise RuntimeError(f"Unable to reach Notion while loading entry numbers: {e}")

        if response.status_code != 200:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise RuntimeError(f"Notion rejected the entry lookup ({response.status_code}): {detail}")

        data = response.json()
        results = data.get("results", [])
        for page in results:
            properties = page.get("properties", {})
            name_property = properties.get("Name", {}).get("title", [])
            if name_property:
                entry_number = int(name_property[0].get("plain_text", 0))
                if entry_number > max_entry_number:
                    max_entry_number = entry_number
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")
    return max_entry_number

def to_pst_isoformat(date_str):
    local_time = datetime.fromisoformat(date_str)
    pst = pytz.timezone('America/Los_Angeles')
    local_time = pst.localize(local_time)
    return local_time.isoformat()

def update_notion_database(data):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": str(data["entry_number"])}}]},
            "Wake Time": {"date": {"start": to_pst_isoformat(data["wake_time"])}},
            "Sleep Time": {"date": {"start": to_pst_isoformat(data["sleep_time"])}},
            "Exercise?": {"select": {"name": data["exercise"]}},
            "Went Outside?": {"select": {"name": data["outside"]}},
            "Talk to Someone?": {"select": {"name": data["talk"]}},
            "Min. on Social Media": {"number": int(data["social_media"])},
            "Date": {"date": {"start": to_pst_isoformat(data["todays_date"] + "T00:00:00")}},
            "Time Focused": {"number": int(data["time_focused"])},
            "Offday/Special Day?": {"select": {"name": data["offday_special_day"]}},
            "QOL Score": {"number": float(data["qol_score"])},
            "Streak": {"number": int(data["streak"])},
            "Diary": {"rich_text": [{"text": {"content": str(data["diary"])}}]}
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
    except Exception as e:
        return False, f"Request failed: {e}"

    if response.status_code in (200, 201):
        return True, None

    # surface Notion’s real error message
    try:
        return False, f"{response.status_code}: {response.json()}"
    except Exception:
        return False, f"{response.status_code}: {response.text}"


def build_default_datetime_strings(now=None):
    if now is None:
        now = datetime.now()

    today = now.strftime("%Y-%m-%d")
    return {
        "wake_time": f"{today}T08:00:00",
        "sleep_time": f"{today}T23:00:00",
        "todays_date": today,
    }


def display_qol_score(data):
    score = data["qol_score"]
    streak = int(data["streak"])
    good_streak = streak if streak > 0 else 0
    bad_streak = abs(streak) if streak < 0 else 0

    score_window = tk.Toplevel(root)
    score_window.title("QOL Score")
    score_window.geometry("800x600")

    background_image_path = f"{base_dir}/../Images/boyyaky.jpg"
    if not os.path.exists(background_image_path):
        messagebox.showerror("Error", f"Background image not found: {background_image_path}")
        score_window.destroy()
        return

    background_image = Image.open(background_image_path)
    background_photo = ImageTk.PhotoImage(background_image)
    score_window.background_photo = background_photo

    background_label = tk.Label(score_window, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    custom_font = ("Comic Sans MS", 24, "bold")

    qol_score_label = tk.Label(score_window, text=f"QOL Score: {score}", font=custom_font, bg="white", fg="black")
    qol_score_label.pack(pady=20)

    good_streak_label = tk.Label(score_window, text=f"Good Streak: {good_streak}", font=custom_font, bg="white", fg="black")
    good_streak_label.pack(pady=10)

    bad_streak_label = tk.Label(score_window, text=f"Bad Streak: {bad_streak}", font=custom_font, bg="white", fg="black")
    bad_streak_label.pack(pady=10)

    good_streak_messages = [
        "You just a chill guy like that. Keep at it my friend.",
        "君の未来は明るい",
        "そなたは美しい"
    ]

    bad_streak_messages = [
        "ggs my friend, on to the next",
        "my guy, tomorrow's gonna be a better day.",
        "オワコンやんけ"
    ]

    if bad_streak > good_streak:
        message_text = random.choice(bad_streak_messages)
        message_label = tk.Label(score_window, text=message_text, font=custom_font, bg="white", fg="red")
    else:
        message_text = random.choice(good_streak_messages)
        message_label = tk.Label(score_window, text=message_text, font=custom_font, bg="white", fg="black")

    message_label.pack(pady=20)

def resize_image(image_path, width, height):
    image = Image.open(image_path)
    resized_image = image.resize((width, height), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
    return ImageTk.PhotoImage(resized_image)

def fetch_past_entries(limit=14):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "page_size": limit,
        "sorts": [{"property": "Date", "direction": "descending"}]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    if response.status_code != 200:
        try:
            messagebox.showerror("Notion Error", f"{response.status_code}: {response.json()}")
        except Exception:
            messagebox.showerror("Notion Error", f"{response.status_code}: {response.text}")
        return []

    
    entries = []
    for page in results:
        properties = page.get("properties", {})
        date_property = properties.get("Date", {}).get("date", {}).get("start", "")
        score_property = properties.get("QOL Score", {}).get("number", 0)
        if date_property and score_property:
            entries.append((date_property, score_property))
        if date_property and score_property == 0: # account for actual days with QOL_score=0
            entries.append((date_property, score_property))
    return entries[::-1]  # Reverse to get chronological order

def plot_qol_score():
    entries = fetch_past_entries(limit=14)
    print(entries)
    if not entries:
        messagebox.showwarning("No Data", "No QOL data available to plot.")
        return
    
    dates, scores = zip(*entries)
    formatted_dates = [datetime.fromisoformat(date).strftime('%Y-%m-%d') for date in dates]
    
    plt.figure(figsize=(10, 5))
    plt.plot(formatted_dates, scores, marker='o', linestyle='-', color='b')
    plt.xlabel('Date')
    plt.ylabel('QOL Score')
    plt.title('QOL Score vs. Time (Last 14 days)')
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# return "Streak" prop. value in database given entry number
def fetch_streak_by_name(entry_name):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Name",
            "title": {
                "equals": entry_name
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"Notion rejected the streak lookup ({response.status_code}): {detail}")
    data = response.json()
    results = data.get("results", [])
    
    if results:
        properties = results[0].get("properties", {})
        streak_property = properties.get("Streak", {}).get("number", None)
        return streak_property
    return None

# gets all user input data into a single dictionary
# also adds QOL score and streak value as well
# returns that dictionary
def get_values_from_user():
    # basic input fetch
    entry_number_raw = entry_number_entry.get().strip()

    # validate entry number
    try:
        entry_num = int(entry_number_raw)
    except ValueError:
        raise ValueError("Entry Number must be an integer.")

    # validate required numeric fields early (so you get a popup instead of silent failure)
    social_raw = social_media_entry.get().strip()
    focused_raw = time_focused_entry.get().strip()
    if social_raw == "" or focused_raw == "":
        raise ValueError("Please fill out 'Min. on Social Media' and 'Time Focused' (numbers).")

    try:
        int(social_raw)
        int(focused_raw)
    except ValueError:
        raise ValueError("'Min. on Social Media' and 'Time Focused' must be integers.")

    data = {
        "entry_number": str(entry_num),
        "wake_time": wake_time_entry.get().strip(),
        "sleep_time": sleep_time_entry.get().strip(),
        "exercise": exercise_var.get(),
        "outside": outside_var.get(),
        "talk": talk_var.get(),
        "social_media": social_raw,
        "todays_date": todays_date_entry.get().strip(),
        "time_focused": focused_raw,
        "offday_special_day": offday_special_day_var.get(),
        "diary": diary_entry.get().strip()
    }

    # compute qol (can still raise if datetime formats are wrong)
    qol_score = QOL_LIB.calculate_qol_score(data)
    data["qol_score"] = round(qol_score, 1)

    # safe streak calc (handle empty DB / missing previous entry)
    prev_name = str(entry_num - 1)
    prev_streak_val = fetch_streak_by_name(prev_name)
    previous_streak = int(prev_streak_val) if prev_streak_val is not None else 0

    if data["qol_score"] >= 65:
        data["streak"] = 1 if previous_streak <= 0 else previous_streak + 1
    else:
        data["streak"] = (previous_streak - 1) if previous_streak <= 0 else -1

    return data


def update_and_display_everything():
    try:
        data = get_values_from_user()
        ok, err = update_notion_database(data)
        if ok:
            messagebox.showinfo("Success", "Data updated successfully!")
            display_qol_score(data)  # (your function ignores the arg anyway)
        else:
            messagebox.showerror("Notion Error", err or "Failed to update Notion database.")
    except Exception as e:
        messagebox.showerror("Submit Failed", str(e))


def run_ranking_as_subprocess():
    def run_ranking():
        username = os.getenv('USER')
        try:
            subprocess.run(["python3", f"{base_dir}/ranking.py"], text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed: {e.stderr}")
            messagebox.showerror("Error", f"Subprocess failed: {e.stderr}")
    thread = threading.Thread(target=run_ranking)
    thread.start()

# update the analysis request database
def update_analysis_request_database():
    # Get the current date
    current_date = datetime.now()
    # Format the date as YYYY-MM-DD
    formatted_date = current_date.strftime("%Y-%m-%d")

    url = f"https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": AR_DATABASE_ID},
        "properties": {
            "Username": {"title": [{"text": {"content": user}}]},
            "Request Date": {"date":{"start": formatted_date}}
        }
    }

    response = requests.post(url, json=payload, headers=ar_headers)
    #print(response.status_code)
    #print(response.json())  # This will print the response content
    return response.status_code == 200

# analysis request = AR
def ar():
    if update_analysis_request_database():
            messagebox.showinfo("Success", "Analysis request sent successfully!")
    else:
            messagebox.showerror("Error", "Failed to send analysis request.")

# tkinter display the analysis results
def display_analysis_results(root, analysis_property):
    # Create a new top-level window instead of Tk()
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Analysis Results")
    analysis_window.geometry("900x700")  # Keep window size large

    # Load and set the background image
    background_image = Image.open(f"{base_dir}/../Images/medalist.jpeg")
    background_photo = ImageTk.PhotoImage(background_image)

    # Keep a reference in root to avoid garbage collection
    analysis_window.background_photo = background_photo  

    background_label = tk.Label(analysis_window, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Load retro font
    font_path = f"{base_dir}/../Text_Files/Press_Start_2P/PressStart2P-Regular.ttf"
    
    # Adjusted fonts for better proportions
    title_font = tkFont.Font(family="Press Start 2P", size=18)  # Title is big but not overwhelming
    text_font = tkFont.Font(family="Press Start 2P", size=15)   # Text is readable without stretching

    # Title label (Bigger & Centered)
    title_label = tk.Label(analysis_window, text="Analysis Results", font=title_font, bg="white", fg="black")
    title_label.place(relx=0.5, rely=0.07, anchor="center")

    # Scrollable text box (Shrunk width further)
    text_area = scrolledtext.ScrolledText(
        analysis_window, wrap=tk.WORD, font=text_font, 
        bg="black", fg="lime", width=50, height=30  # Further reduced width + balanced height
    )
    text_area.insert(tk.INSERT, analysis_property)  # Insert analysis report
    text_area.config(state=tk.DISABLED)  # Make it read-only
    text_area.place(relx=0.5, rely=0.55, anchor="center")  # Keep it centered

# check for new Analysis
# THIS FUNCTION IS WORK IN PROGRESS
def check_for_analysis():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
    "sorts": [
            {
            "property": "Name",
            "direction": "descending"
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    results = data.get("results", [])
    properties = results[0].get("properties", [])
    analysis_property = properties.get("Analysis", []).get("rich_text", [])[0].get("text").get("content")

    display_analysis_results(root, analysis_property)

# MAIN TKINTER THREAD
root = tk.Tk()
root.title("Daily QOL Data Input")

# Set the initial window size (width x height)
root.geometry("1200x1200")  # Adjust the size as needed

# Make the window resizable
root.resizable(True, True)

# Load pixel art background
background_image = tk.PhotoImage(file=f"{base_dir}/../Images/pixel_smile_background.png")  # Replace with your image path
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Set retro font
font_path = f"{base_dir}/../Text_Files/Press_Start_2P/PressStart2P-Regular.ttf"  # Path to your .ttf file
retro_font = tkFont.Font(family="Press Start 2P", size=15)  # Load the font using Tkinter
highest_entry_number = get_highest_entry_number()
default_datetimes = build_default_datetime_strings()

# Configure grid to be resizable
for i in range(10):
    root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(i, weight=1)

tk.Label(root, text="Entry Number (Previous: {})".format(highest_entry_number), font=retro_font, bg="black", fg="white").grid(row=0, column=0, sticky="nsew")
entry_number_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
entry_number_entry.insert(0, str(highest_entry_number + 1))
entry_number_entry.grid(row=0, column=1, sticky="nsew")

tk.Label(root, text="Wake Time (YYYY-MM-DDTHH:MM:SS)", font=retro_font, bg="black", fg="white").grid(row=1, column=0, sticky="nsew")
wake_time_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
wake_time_entry.insert(0, default_datetimes["wake_time"])
wake_time_entry.grid(row=1, column=1, sticky="nsew")

tk.Label(root, text="Sleep Time (YYYY-MM-DDTHH:MM:SS)", font=retro_font, bg="black", fg="white").grid(row=2, column=0, sticky="nsew")
sleep_time_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
sleep_time_entry.insert(0, default_datetimes["sleep_time"])
sleep_time_entry.grid(row=2, column=1, sticky="nsew")

exercise_var = tk.StringVar(value="No")
tk.Label(root, text="Exercise?", font=retro_font, bg="black", fg="white").grid(row=3, column=0, sticky="nsew")
exercise_menu = tk.OptionMenu(root, exercise_var, "Yes", "No")
exercise_menu.config(font=retro_font, bg="black", fg="white")
exercise_menu.grid(row=3, column=1, sticky="nsew")

outside_var = tk.StringVar(value="No")
tk.Label(root, text="Went Outside?", font=retro_font, bg="black", fg="white").grid(row=4, column=0, sticky="nsew")
outside_menu = tk.OptionMenu(root, outside_var, "Yes", "No")
outside_menu.config(font=retro_font, bg="black", fg="white")
outside_menu.grid(row=4, column=1, sticky="nsew")

talk_var = tk.StringVar(value="No")
tk.Label(root, text="Talk to Someone?", font=retro_font, bg="black", fg="white").grid(row=5, column=0, sticky="nsew")
talk_menu = tk.OptionMenu(root, talk_var, "Yes", "No")
talk_menu.config(font=retro_font, bg="black", fg="white")
talk_menu.grid(row=5, column=1, sticky="nsew")

tk.Label(root, text="Min. on Social Media", font=retro_font, bg="black", fg="white").grid(row=6, column=0, sticky="nsew")
social_media_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
social_media_entry.grid(row=6, column=1, sticky="nsew")

tk.Label(root, text="Today's Date (YYYY-MM-DD)", font=retro_font, bg="black", fg="white").grid(row=7, column=0, sticky="nsew")
todays_date_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
todays_date_entry.insert(0, default_datetimes["todays_date"])
todays_date_entry.grid(row=7, column=1, sticky="nsew")

tk.Label(root, text="Time Focused (minutes)", font=retro_font, bg="black", fg="white").grid(row=8, column=0, sticky="nsew")
time_focused_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
time_focused_entry.grid(row=8, column=1, sticky="nsew")

offday_special_day_var = tk.StringVar(value="No")
tk.Label(root, text="Offday/Special Day?", font=retro_font, bg="black", fg="white").grid(row=9, column=0, sticky="nsew")
offday_menu = tk.OptionMenu(root, offday_special_day_var, "Yes", "No")
offday_menu.config(font=retro_font, bg="black", fg="white")
offday_menu.grid(row=9, column=1, sticky="nsew")

# Diary
tk.Label(root, text="Diary (Separate Events by ',')", font=retro_font, bg="black", fg="white").grid(row=10, column=0, sticky="nsew")
diary_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
diary_entry.insert(0, "What Happened Today?")
diary_entry.grid(row=10, column=1, sticky="nsew")

# Resize the submit button image
submit_button_image = resize_image(f"{base_dir}/../Images/boyyaky_button.png", 100, 100)
submit_button = tk.Button(root, image=submit_button_image, command=update_and_display_everything, borderwidth=0)
submit_button.grid(row=11, column=0, columnspan=2, sticky="nsew")

# Configure plot button with ttk
style = ttk.Style()
style.configure("TButton", font=retro_font, background="yellow", foreground="blue")

# Keep references to the images to prevent garbage collection
plot_button_image = resize_image(f"{base_dir}/../Images/kabu_chart_man_happy.jpg", 130, 100)
ranking_button_image = resize_image(f"{base_dir}/../Images/jyaian.jpg", 100, 100)
request_button_image = resize_image(f"{base_dir}/../Images/yugioh.jpg", 150, 100)
check_analysis_image = resize_image(f"{base_dir}/../Images/mail.jpg", 100, 100)

plot_button = tk.Button(root, image=plot_button_image, command=plot_qol_score, borderwidth=0)
plot_button.grid(row=12, column=0, sticky="nsew")

ranking_button = tk.Button(root, image=ranking_button_image, command=run_ranking_as_subprocess, borderwidth=0)
ranking_button.grid(row=13, column=0, sticky="nsew")

# request analysis button
request_analysis_button = tk.Button(root, image=request_button_image, command=ar, borderwidth=0)
request_analysis_button.grid(row=12, column=1, sticky="nsew")

# check for analysis button
check_analysis = tk.Button(root, image=check_analysis_image, command=check_for_analysis, borderwidth=0)
check_analysis.grid(row=13, column=1, sticky="nsew")

root.update_idletasks()  # Force update the UI

root.mainloop()
