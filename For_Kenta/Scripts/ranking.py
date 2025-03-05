import requests
import json
import tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, font
import tkinter.font as tkFont
from PIL import Image, ImageTk

# dict with all user info
all_users = {
    "Kenta": {
        "NOTION_TOKEN": "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",
        "DATABASE_ID": "1924d9b143a980719cabc4f151bc30fb"
    },

    "Kazuma":{
        "NOTION_TOKEN": "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",
        "DATABASE_ID": "1954d9b143a981019212fbe32c21a6a1" 
    },

    "User_Analysis_Requests_Database":{
        "NOTION_TOKEN": "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",
        "DATABASE_ID": "1ad4d9b143a980e7806ece9c6a0eb626"
    }

}

# just to see structure of database json
def display_structure(DATABASE_ID, user):
	url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
	payload = {
		"page_size": 1
	}
	headers = {
	    "Authorization": "Bearer " + all_users[user]["NOTION_TOKEN"],
	    "Content-Type": "application/json",
	    "Notion-Version": "2022-06-28",
		}
	response = requests.post(url, headers=headers, json=payload)
	data = response.json()
	results = data.get("results", [])
	
	for page in results:
		prop = page.get("properties", [])
		prop_as_json = json.dumps(prop, indent=4)
		print(prop_as_json)

# retrieve all users latest QOL score
def retrieve_all_users_QOL(all_users):
	all_users_qol_score = {}
	for key in all_users:
		DATABASE_ID = all_users[key]["DATABASE_ID"]
		
		url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
		
		payload = {
			"page_size": 1,
			"sorts": [{"property": 	"Name", "direction": "descending"}]
		}

		headers = {
	    "Authorization": "Bearer " + all_users[key]["NOTION_TOKEN"],
	    "Content-Type": "application/json",
	    "Notion-Version": "2022-06-28",
		}

		response = requests.post(url, headers=headers, json=payload)
		data = response.json()
		results = data.get("results", [])

		# sort page by descending "Name" property-> get QOL score of entry
		for page in results:
			properties = page.get("properties", [])
			qol_score = properties["QOL Score"]["number"]
			all_users_qol_score[key] = qol_score

	return all_users_qol_score

# take all user qol
# display top 3 in tkinter
def get_top_three(all_users_qol_score):
	rank = [(None, 0)] * 3
	for key in all_users_qol_score:
		qol = all_users_qol_score[key]
		if qol > rank[2][1]:
			if qol > rank[1][1]:
				if qol > rank[0][1]:
					rank.insert(0, (key, qol))
					rank.pop(3)
					continue
				rank.insert(1, (key, qol))
				rank.pop(3)
				continue
			rank.insert[2, (key, qol)]
			rank.pop(3)
	return rank

def display_it(rank):
	root = tk.Tk()
	root.title("Top 3 Rankings")
	root.geometry("800x600")  # Set the window size to 800x600 pixels

	# Load background
	background_image = Image.open("/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/medalist.jpeg")
	background_photo = ImageTk.PhotoImage(background_image)
	background_label = tk.Label(root, image=background_photo)
	background_label.place(relwidth=1, relheight=1)

	# Set retro font
	font_path = "/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Text_Files/Press_Start_2P/PressStart2P-Regular.ttf"
	root.option_add("*Font", tkFont.Font(family="Press Start 2P", size=25))
	retro_font = tkFont.Font(family="Press Start 2P", size=25)

	# Title label
	title_label = tk.Label(root, text="LATEST TOP 3", font=retro_font, bg="white", fg="black")
	title_label.place(relx=0.5, rely=0.1, anchor="center")

	# Function to create a ranking label
	def create_ranking_label(position, name, score):
		position_label = tk.Label(root, text=f"{position}.", font=retro_font, bg="white", fg="black")
		position_label.place(relx=0.1, rely=0.2 + position * 0.1, anchor="center")

		name_label = tk.Label(root, text=name, font=retro_font, bg="white", fg="black")
		name_label.place(relx=0.3, rely=0.2 + position * 0.1, anchor="center")

		score_label = tk.Label(root, text=f"Score: {score}", font=retro_font, bg="white", fg="black")
		score_label.place(relx=0.7, rely=0.2 + position * 0.1, anchor="center")

	# Create labels for each rank
	for i, (name, score) in enumerate(rank):
		create_ranking_label(i + 1, name, score)

	# Add pixel game-themed images (if provided)
	images = ["/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/gold_medal.jpg", "/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/silver_medal.jpg", "/Users/kentahsu/Code/Personal/QOL_Score/For_Kenta/Images/bronze_medal.jpg"]
	for i, image_path in enumerate(images):
		try:
			print(f"Loading image: {image_path}")
			image = Image.open(image_path)
			image = image.resize((60, 60), Image.LANCZOS)
			photo = ImageTk.PhotoImage(image)
			image_label = tk.Label(root, image=photo, bg="lightgray")
			image_label.image = photo  # Keep a reference to avoid garbage collection
			image_label.place(relx=0.1, rely=0.19 + (i + 1) * 0.1, anchor="center")
			print(f"Successfully loaded image: {image_path}")
		except Exception as e:
			print(f"Error loading image {image_path}: {e}")

	root.mainloop()

def main():
	all_users_qol_score = retrieve_all_users_QOL(all_users)
	rank = get_top_three(all_users_qol_score)
	display_it(rank)


if __name__ == '__main__':
	main()


#display_structure(all_users["User_Analysis_Requests_Database"]["DATABASE_ID"], "User_Analysis_Requests_Database")


