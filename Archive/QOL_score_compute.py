#!/usr/bin/env python3

import json
import sys
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

# Function to calculate QOL score
def calculate_qol_score(data):
    wake_time = data["Wake Times"][0]
    sleep_time = data["Sleep Times"][0]

    exercise = data["Exercise Values"][0]
    outside = data["Went Outside Values"][0]
    talk = data["Talk to Someone Values"][0]
    social_media = int(data["Min. on Social Media Values"][0])
    eff = float(data["Efficiency"])

    score = 100

    # Extract time from datetime string
    wake_time_dt = datetime.strptime(wake_time, "%Y-%m-%dT%H:%M:%S.%f%z")
    
    # Check if sleep_time is empty and handle it
    if sleep_time:
        sleep_time_dt = datetime.strptime(sleep_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        # Adjust for next day sleep times
        if sleep_time_dt < wake_time_dt:
            sleep_time_dt += timedelta(days=1)
    else:
        sleep_time_dt = wake_time_dt + timedelta(hours=8)  # Default to 8 hours after wake time

    # Healthy Day or Productive Day
    if eff <= 0.6:  # healthy day
        print("healthy day")

        # Calculate wake_time penalty
        wake_minutes_off = abs((wake_time_dt - datetime.strptime("08:30", "%H:%M").replace(tzinfo=wake_time_dt.tzinfo)).total_seconds() / 60)
        score -= min(wake_minutes_off * 0.2, 15)

        # Calculate sleep_time penalty
        sleep_minutes_off = abs((sleep_time_dt - datetime.strptime("23:59", "%H:%M").replace(tzinfo=sleep_time_dt.tzinfo)).total_seconds() / 60)
        score -= min(sleep_minutes_off * 0.2, 15)

        # Exercise penalty
        if exercise == "No":
            score -= 10

        # Outside penalty
        if outside == "No":
            score -= 10

        # Talk penalty
        if talk == "No":
            score -= 10

        # Social media penalty
        if social_media > 45:
            score -= (social_media - 45) * 0.2

        # Efficiency penalty
        if eff < 0.6:
            eff_diff = 0.6 - eff
            score -= (eff_diff / 0.1) * 10

        if score < 0:
            score = 0
    else:
        print("productive day")

        # Calculate wake_time penalty
        wake_minutes_off = abs((wake_time_dt - datetime.strptime("08:30", "%H:%M").replace(tzinfo=wake_time_dt.tzinfo)).total_seconds() / 60)
        score -= min(wake_minutes_off * 0.2, 15)

        # Calculate sleep_time penalty
        sleep_minutes_off = abs((sleep_time_dt - datetime.strptime("23:59", "%H:%M").replace(tzinfo=sleep_time_dt.tzinfo)).total_seconds() / 60)
        score -= min(sleep_minutes_off * 0.2, 15)

        # Social media penalty
        if social_media > 45:
            score -= (social_media - 45) * 0.2

        # Efficiency penalty
        if eff < 0.8:
            eff_diff = 0.8 - eff
            score -= (eff_diff / 0.1) * 15

        if score < 0:
            score = 0

    return score

# Function to display QOL score and streak with a background image and custom font
def display_qol_score(score, good_streak, bad_streak):
    root = tk.Tk()
    root.title("QOL Score")

    # Set window size to be larger
    root.geometry("800x600")

    # Set background image (ensure the correct path to your background image)
    background_image_path = "/Users/kentahsu/Code/Personal/QOL_Score/boyyaky.jpg"
    
    if not os.path.exists(background_image_path):
        print(f"Background image not found: {background_image_path}")
        return
    
    background_image = Image.open(background_image_path)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Custom font (ensure the font file is in the same directory or provide the full path)
    custom_font = ("Comic Sans MS", 24, "bold")

    # QOL Score Label
    qol_score_label = tk.Label(root, text=f"QOL Score: {score}", font=custom_font, bg="white", fg="black")
    qol_score_label.pack(pady=20)

    # Good Streak Label
    good_streak_label = tk.Label(root, text=f"Good Streak: {good_streak}", font=custom_font, bg="white", fg="black")
    good_streak_label.pack(pady=10)

    # Bad Streak Label
    bad_streak_label = tk.Label(root, text=f"Bad Streak: {bad_streak}", font=custom_font, bg="white", fg="black")
    bad_streak_label.pack(pady=10)

    # Messages based on streaks
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
        
        message_label = tk.Label(root, text=message_text, font=("Comic Sans MS", 24, "bold"), bg="white", fg="red")
        message_label.pack(pady=20)
        
    else:
        message_text = random.choice(good_streak_messages)
        
        message_label = tk.Label(root, text=message_text, font=("Comic Sans MS", 24, "bold"), bg="white", fg="black")
        message_label.pack(pady=20)

    root.mainloop()

# Main function to read JSON data and calculate/display QOL score and streaks
def main():
    input_json = sys.stdin.read()
    
    if not input_json.strip():
        print("No input data provided.")
        return
    
    data = json.loads(input_json)

    score = calculate_qol_score(data)

    # Track streaks
    streak_file = "streaks.json"

    # Initialize streaks data
    if not os.path.exists(streak_file):
        streaks = {"good_streak": 0, "bad_streak": 0, "last_score": None, "last_update": ""}
    else:
        with open(streak_file, 'r') as file:
            streaks = json.load(file)

    today_date_str = datetime.now().strftime("%Y-%m-%d")

    # Ensure 'last_update' key exists in streaks dictionary to avoid KeyError
    if 'last_update' not in streaks:
        streaks['last_update'] = ""

    # Check if the streaks were updated today
    if streaks["last_update"] != today_date_str:
        # Update streaks only if they were not updated today
        if score >= 80:
            if streaks["last_score"] is not None and streaks["last_score"] >= 80:
                streaks["good_streak"] += 1
            else:
                streaks["good_streak"] = 1
            streaks["bad_streak"] = 0
        else:
            if streaks["last_score"] is not None and streaks["last_score"] < 80:
                streaks["bad_streak"] += 1
            else:
                streaks["bad_streak"] = 1
            streaks["good_streak"] = 0

        streaks["last_score"] = score
        streaks["last_update"] = today_date_str

        # Save streaks data only if updated today
        with open(streak_file, 'w') as file:
            json.dump(streaks, file, indent=4)

    display_qol_score(score, streaks['good_streak'], streaks['bad_streak'])

if __name__ == "__main__":
    main()






