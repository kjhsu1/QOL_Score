#!/usr/bin/env python3
# pipe QOL_input_extraction.py output into this program

import json
import sys
import os
from datetime import datetime
from tkinter import Tk, messagebox

# Read JSON data from stdin
input_json = sys.stdin.read()
data = json.loads(input_json)

# Extract data
wake_time = data["Wake Times"][0]
wake_time = wake_time[wake_time.find("T")+1:wake_time.find("T")+6]

sleep_time = data["Sleep Times"][0]
sleep_time = sleep_time[sleep_time.find("T")+1:sleep_time.find("T")+6]

exercise = data["Exercise Values"][0]
outside = data["Went Outside Values"][0]
talk = data["Talk to Someone Values"][0]
social_media = int(data["Min. on Social Media Values"][0])
eff = float(data["Efficiency"][0])

score = 100

# Healthy Day or Productive Day
if eff <= 0.6:  # healthy day
    # Calculate wake_time penalty
    wake_hour, wake_minute = map(int, wake_time.split(':'))
    wake_minutes_off = abs((wake_hour * 60 + wake_minute) - (8 * 60 + 30))
    score -= wake_minutes_off

    # Calculate sleep_time penalty
    sleep_hour, sleep_minute = map(int, sleep_time.split(':'))
    sleep_minutes_off = abs((sleep_hour * 60 + sleep_minute) - (23 * 60 + 59))
    score -= sleep_minutes_off

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
        score -= (social_media - 45)

    # Efficiency penalty
    score -= (1 - (0.6 - eff) / 0.6) * 100

    if score < 0:
        score = 0
else:
    # Calculate wake_time penalty
    wake_hour, wake_minute = map(int, wake_time.split(':'))
    wake_minutes_off = abs((wake_hour * 60 + wake_minute) - (8 * 60 + 30))
    score -= wake_minutes_off

    # Calculate sleep_time penalty
    sleep_hour, sleep_minute = map(int, sleep_time.split(':'))
    sleep_minutes_off = abs((sleep_hour * 60 + sleep_minute) - (23 * 60 + 59))
    score -= sleep_minutes_off

    # Social media penalty
    if social_media > 45:
        score -= (social_media - 45)

    # Efficiency penalty
    score -= (1 - (0.8 - eff) / 0.8) * 100

    if score < 0:
        score = 0

# Display pop-up with QOL score
root = Tk()
root.withdraw()
messagebox.showinfo("QOL Score", f"Your QOL Score is: {score}")

# Track streaks
streak_file = "streaks.json"

# Initialize streaks data
if not os.path.exists(streak_file):
    streaks = {"good_streak": 0, "bad_streak": 0, "last_score": None}
else:
    with open(streak_file, 'r') as file:
        streaks = json.load(file)

# Update streaks
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

# Save streaks data
with open(streak_file, 'w') as file:
    json.dump(streaks, file, indent=4)

# Display streaks
messagebox.showinfo("Streaks", f"Good Streak: {streaks['good_streak']}")




