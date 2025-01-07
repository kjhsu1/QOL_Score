import requests

NOTION_TOKEN = "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"
DATABASE_ID = "1144d9b143a9800180f9d91c8934c2cb"  # Data Input for QOL Calculation
DATABASE_2_ID = "0f0518e910de4ca8bf0bf67ddebeefe1"  # Awake Minutes

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# entry number of interest
entry_number = "145"

# Query the database
def get_pages(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    return results

# Extract values from the Awake Minutes database
# entry_number = value of "Name" property" of interest
    # ex. "145" (a.k.a entry # 145)
    # data_type is string
def extract_awake_minutes_values(pages, entry_number):
    wake_times = []
    sleep_times = []
    for page in pages:
        properties = page["properties"]
        name_property = properties["Name"]["title"]
        if name_property and name_property[0]["plain_text"] == entry_number:
            wake_time_property = properties["Wake TIme"]["date"]
            sleep_time_property = properties["Sleep TIme"]["date"]
            if wake_time_property:
                wake_time = wake_time_property["start"]
                wake_times.append(wake_time)
            if sleep_time_property:
                sleep_time = sleep_time_property["start"]
                sleep_times.append(sleep_time)
    return wake_times, sleep_times

# Extract values from the Data Input for QOL Calculation database
def extract_qol_values(pages, entry_number):
    exercise_values = []
    went_outside_values = []
    for page in pages:
        properties = page["properties"]
        name_property = properties["Name"]["title"]
        if name_property and name_property[0]["plain_text"] == entry_number:
            exercise_property = properties["Exercise?"]["select"]
            went_outside_property = properties["Went Outside?"]["select"]
            if exercise_property:
                exercise_values.append(exercise_property["name"])
            if went_outside_property:
                went_outside_values.append(went_outside_property["name"])
    return exercise_values, went_outside_values

# Get pages from both databases
awake_minutes_pages = get_pages(DATABASE_2_ID)
qol_pages = get_pages(DATABASE_ID)

# Extract values
wake_times, sleep_times = extract_awake_minutes_values(awake_minutes_pages, entry_number)
exercise_values, went_outside_values = extract_qol_values(qol_pages, entry_number)

print("Wake Times:", wake_times)
print("Sleep Times:", sleep_times)
print("Exercise Values:", exercise_values)
print("Went Outside Values:", went_outside_values)


