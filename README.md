# QOL_Score
Using Notion API and pyscript to calculate QOL score

*NOTE: If you want to run run_this_everyday.sh in the Archive directory properly, you need to take out all the files in Archive directory and move it to the QOL_Score directory again.

How to Use

1. Get Notion, then
	- Copy below page into your Notion
		- https://www.notion.so/1924d9b143a980719cabc4f151bc30fb?v=1924d9b143a980dfb2ab000c90213282&pvs=4
2. Create a Notion Integration 
	- use this link https://www.notion.so/profile/integrations
3. Add the database to the integration
4. Go into terminal, run, ```git clone https://github.com/kjhsu1/QOL_Score.git```
5. Open run_this_everyday.sh, change path to the directory on your computer
	- ex. "Users/name/Downloads/QOL_Score"
6. Open QOL_input_extraction.py and UI.py and change NOTION_TOKEN and DATABASE_ID

*Note: New User Should download anaconda, then pip install all of the required modules using environment.yml

When Running Everday
1. On Mac, go to Applications to open the Automater app.
2. Automate running UI.py and have it on your desktop so you just need to click on it everyday
