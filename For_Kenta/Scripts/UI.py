#!/usr/bin/env python3

import requests
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, font
import tkinter.font as tkFont
from datetime import datetime, timedelta
import pytz
import os
import threading
import subprocess
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import QOL_LIB # my homemade library 


# For Kenta's Database
NOTION_TOKEN = "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"
DATABASE_ID = "1924d9b143a980719cabc4f151bc30fb"

'''
# For Kazuma's Database
NOTION_TOKEN = "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"
DATABASE_ID = "1954d9b143a981019212fbe32c21a6a1" 
'''

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_highest_entry_number():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    data = response.json()
    results = data.get("results", [])
    
    max_entry_number = 0
    for page in results:
        properties = page.get("properties", {})
        name_property = properties.get("Name", {}).get("title", [])
        if name_property:
            entry_number = int(name_property[0].get("plain_text", 0))
            if entry_number > max_entry_number:
                max_entry_number = entry_number
    return max_entry_number

def to_pst_isoformat(date_str):
    local_time = datetime.fromisoformat(date_str)
    pst = pytz.timezone('America/Los_Angeles')
    local_time = pst.localize(local_time)
    return local_time.isoformat()

def update_notion_database(data):
    url = f"https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data["entry_number"]}}]},
            "Wake Time": {"date": {"start": to_pst_isoformat(data["wake_time"]).replace('-08:00', ''), "time_zone": "America/Los_Angeles"}},
            "Sleep Time": {"date": {"start": to_pst_isoformat(data["sleep_time"]).replace('-08:00', ''), "time_zone": "America/Los_Angeles"}},
            "Exercise?": {"select": {"name": data["exercise"]}},
            "Went Outside?": {"select": {"name": data["outside"]}},
            "Talk to Someone?": {"select": {"name": data["talk"]}},
            "Min. on Social Media": {"number": int(data["social_media"])},
            "Date": {"date": {"start": data["todays_date"] + "T00:00:00.000", "time_zone": "America/Los_Angeles"}},
            "Time Focused": {"number": int(data["time_focused"])},
            "Offday/Special Day?": {"select": {"name": data["offday_special_day"]}},
            "QOL Score": {"number": int(data["qol_score"])}, # NEW ADDITION
            "Streak": {"number": int(data["streak"])} # NEW ADDITION
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200

def display_qol_score(data):
    def run_subprocess():
        username = os.getenv('USER')
        try:
            result = subprocess.run(["python3", f"/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Scripts/All_in_one_QOL_input_extraction_kenta_version.py", entry_number_entry.get()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            subprocess.run(["python3", f"/Users/{username}/Code/Personal/QOL_Score/For_Kenta/Scripts/All_in_one_QOL_score_compute_kenta_version.py"], input=result.stdout, text=True, check=True)

        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed: {e.stderr}")
            messagebox.showerror("Error", f"Subprocess failed: {e.stderr}")

    thread = threading.Thread(target=run_subprocess)
    thread.start()

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
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    results = data.get("results", [])
    
    entries = []
    for page in results:
        properties = page.get("properties", {})
        date_property = properties.get("Date", {}).get("date", {}).get("start", "")
        score_property = properties.get("QOL Score", {}).get("number", 0)
        if date_property and score_property:
            entries.append((date_property, score_property))
    return entries[::-1]  # Reverse to get chronological order

def plot_qol_score():
    entries = fetch_past_entries(limit=14)
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

def create_plot_button():
    plot_button = tk.Button(root, text="Push for Graph", command=plot_qol_score, font=retro_font, bg="black", fg="white")
    plot_button.grid(row=11, column=0, columnspan=2, sticky="nsew")
    root.update_idletasks()  # Force update the UI'

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
    response = requests.post(url, headers=headers, json=payload)
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
    data = {
        "entry_number": entry_number_entry.get(),
        "wake_time": wake_time_entry.get(),
        "sleep_time": sleep_time_entry.get(),
        "exercise": exercise_var.get(),
        "outside": outside_var.get(),
        "talk": talk_var.get(),
        "social_media": social_media_entry.get(),
        "todays_date": todays_date_entry.get(),
        "time_focused": time_focused_entry.get(),
        "offday_special_day": offday_special_day_var.get()
    }
    # add qol
    qol_score = QOL_LIB.calculate_qol_score(data)
    data["qol_score"] = round(qol_score, 1)
    
    # add streak
    current_streak = 0
    previous_streak = int(fetch_streak_by_name(str(int(data["entry_number"])-1)))
    if data["qol_score"] >= 65:
        if previous_streak <= 0:
            current_streak = 1
        if previous_streak > 0:
            current_streak = previous_streak + 1
    if data["qol_score"] < 65:
        if previous_streak <= 0:
            current_streak = previous_streak - 1
        if previous_streak > 0:
            current_streak = -1

    data["streak"] = current_streak

    return data


# revised update_and_display_everything function
def update_and_display_everything():
    data = get_values_from_user()
    
    # Check for None values instead of using all()
    if all(value is not None for value in data.values()):
        if update_notion_database(data):
            messagebox.showinfo("Success", "Data updated successfully!")
            display_qol_score(data["entry_number"])
        else:
            messagebox.showerror("Error", "Failed to update Notion database.")
    else:
        messagebox.showwarning("Incomplete Data", "Please fill out all fields.")



def run_ranking_as_subprocess():
    # Your function implementation here
    pass

root = tk.Tk()
root.title("Daily QOL Data Input")

# Set the initial window size (width x height)
root.geometry("1200x1200")  # Adjust the size as needed

# Make the window resizable
root.resizable(True, True)

# Load pixel art background
background_image = tk.PhotoImage(file="/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/pixel_smile_background.png")  # Replace with your image path
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Set retro font
font_path = "/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Text_Files/Press_Start_2P/PressStart2P-Regular.ttf"  # Path to your .ttf file
retro_font = tkFont.Font(family="Press Start 2P", size=15)  # Load the font using Tkinter
highest_entry_number = get_highest_entry_number()

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
wake_time_entry.insert(0, "2025-02-06T08:00:00")
wake_time_entry.grid(row=1, column=1, sticky="nsew")

tk.Label(root, text="Sleep Time (YYYY-MM-DDTHH:MM:SS)", font=retro_font, bg="black", fg="white").grid(row=2, column=0, sticky="nsew")
sleep_time_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
sleep_time_entry.insert(0, "2025-02-06T23:00:00")
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
todays_date_entry.insert(0, "2025-02-06")
todays_date_entry.grid(row=7, column=1, sticky="nsew")

tk.Label(root, text="Time Focused (minutes)", font=retro_font, bg="black", fg="white").grid(row=8, column=0, sticky="nsew")
time_focused_entry = tk.Entry(root, font=retro_font, bg="black", fg="white")
time_focused_entry.grid(row=8, column=1, sticky="nsew")

offday_special_day_var = tk.StringVar(value="No")
tk.Label(root, text="Offday/Special Day?", font=retro_font, bg="black", fg="white").grid(row=9, column=0, sticky="nsew")
offday_menu = tk.OptionMenu(root, offday_special_day_var, "Yes", "No")
offday_menu.config(font=retro_font, bg="black", fg="white")
offday_menu.grid(row=9, column=1, sticky="nsew")

# Resize the submit button image
submit_button_image = resize_image("/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/boyyaky_button.png", 100, 100)
submit_button = tk.Button(root, image=submit_button_image, command=update_and_display_everything, borderwidth=0)
submit_button.grid(row=10, column=0, columnspan=2, sticky="nsew")

# Configure plot button with ttk
style = ttk.Style()
style.configure("TButton", font=retro_font, background="yellow", foreground="blue")

plot_button = ttk.Button(root, text="Push for Graph", command=plot_qol_score, style="TButton")
plot_button.grid(row=11, column=0, columnspan=2)

# Load the new button image
ranking_button_image = resize_image("/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/jyaian.jpg", 100, 100)
ranking_button = tk.Button(root, image=ranking_button_image, command=run_ranking_as_subprocess, borderwidth=0)
ranking_button.grid(row=12, column=0, columnspan=2, sticky="nsew")

root.update_idletasks()  # Force update the UI

# Call this function after the main loop starts
root.after(100, create_plot_button)

root.mainloop()