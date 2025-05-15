from datetime import datetime, timedelta


'''
    TAKE IN DICTIONARY WITH FORMAT
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
        "offday_special_day": offday_special_day_var.get(),
        #"qol_score": 0, # CHANGE THIS
        #"streak": 0 # CHANGE THIS

    }
'''

def calculate_qol_score(data):
    wake_time = data["wake_time"]
    sleep_time = data["sleep_time"]
    wake_time_dt = datetime.strptime(wake_time, "%Y-%m-%dT%H:%M:%S")
    sleep_time_dt = datetime.strptime(sleep_time, "%Y-%m-%dT%H:%M:%S")
    minutes_awake = (sleep_time_dt - wake_time_dt).total_seconds() / 60


    exercise = data["exercise"]
    outside = data["outside"]
    talk = data["talk"]
    social_media = int(data["social_media"])
    time_focused = int(data["time_focused"])
    eff = time_focused / minutes_awake
    offday_special_day = data["offday_special_day"]

    score = 100
    
    if sleep_time_dt < wake_time_dt:
            sleep_time_dt += timedelta(days=1)

    # Ideal wake and sleep times
    ideal_wake_time = wake_time_dt.replace(hour=8, minute=30, second=0, microsecond=0)
    ideal_sleep_time = sleep_time_dt.replace(hour=23, minute=59, second=0, microsecond=0)

    # Healthy Day or Productive Day
    if eff < 0.6:  # healthy day
        print("healthy day")

        # Calculate wake_time penalty
        wake_minutes_off = abs((wake_time_dt - ideal_wake_time).total_seconds() / 60)
        score -= min(wake_minutes_off * 0.2, 15)

        # Calculate sleep_time penalty
        sleep_minutes_off = abs((sleep_time_dt - ideal_sleep_time).total_seconds() / 60)
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
        wake_minutes_off = abs((wake_time_dt - ideal_wake_time).total_seconds() / 60)
        # print(wake_minutes_off)
        score -= min(wake_minutes_off * 0.2, 15)
        # print(score)

        # Calculate sleep_time penalty
        sleep_minutes_off = abs((sleep_time_dt - ideal_sleep_time).total_seconds() / 60)
        score -= min(sleep_minutes_off * 0.2, 15)
        # print(score)

        # Social media penalty
        if social_media > 45:
            score -= (social_media - 45) * 0.2

        # Efficiency penalty
        if eff < 0.70:
            eff_diff = 0.7 - eff
            score -= (eff_diff / 0.1) * 15

        if score < 0:
            score = 0
    
    # if offday or special day, then that day's score is 100
    if offday_special_day == "Yes":
        score = 100

    return score