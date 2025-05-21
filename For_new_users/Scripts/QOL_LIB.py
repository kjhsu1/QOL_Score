from datetime import datetime, timedelta

def calculate_qol_score(data):
    wake_time = data["wake_time"]
    sleep_time = data["sleep_time"]
    wake_time_dt = datetime.strptime(wake_time, "%Y-%m-%dT%H:%M:%S")
    sleep_time_dt = datetime.strptime(sleep_time, "%Y-%m-%dT%H:%M:%S")
    
    # if sleep crosses midnight
    if sleep_time_dt < wake_time_dt:
        sleep_time_dt += timedelta(days=1)

    minutes_awake = (sleep_time_dt - wake_time_dt).total_seconds() / 60
    exercise = data["exercise"]
    outside = data["outside"]
    talk = data["talk"]
    social_media = int(data["social_media"])
    time_focused = int(data["time_focused"])
    eff = time_focused / minutes_awake
    offday_special_day = data["offday_special_day"]

    score = 100

    # define ideals
    ideal_wake_time  = wake_time_dt.replace(hour=8,  minute=30, second=0, microsecond=0)
    ideal_sleep_time = sleep_time_dt.replace(hour=23, minute=59, second=0, microsecond=0)

    if eff < 0.6:
        # Healthy day penalties
        # Wake‐up penalty only if you woke later than 8:30
        wake_diff = (wake_time_dt - ideal_wake_time).total_seconds() / 60
        if wake_diff > 0:
            score -= min(wake_diff * 0.2, 15)

        # Sleep penalty (unchanged)
        sleep_minutes_off = abs((sleep_time_dt - ideal_sleep_time).total_seconds() / 60)
        score -= min(sleep_minutes_off * 0.2, 15)

        if exercise == "No":
            score -= 10
        if outside == "No":
            score -= 10
        if talk == "No":
            score -= 10
        if social_media > 45:
            score -= (social_media - 45) * 0.2
        if eff < 0.6:
            score -= ((0.6 - eff) / 0.1) * 10

    else:
        # Productive day penalties
        wake_diff = (wake_time_dt - ideal_wake_time).total_seconds() / 60
        if wake_diff > 0:
            score -= min(wake_diff * 0.2, 15)

        sleep_minutes_off = abs((sleep_time_dt - ideal_sleep_time).total_seconds() / 60)
        score -= min(sleep_minutes_off * 0.2, 15)
        if social_media > 45:
            score -= (social_media - 45) * 0.2
        if eff < 0.7:
            score -= ((0.7 - eff) / 0.1) * 15

    # never go below 0
    score = max(score, 0)

    # special days override
    if offday_special_day == "Yes":
        score = 100

    return score