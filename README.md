# QOL_Score
Using Notion API and pyscript to calculate QOL score

*NOTE: If you want to run run_this_everyday.sh in the Archive directory properly, you need to take out all the files in Archive directory and move it to the QOL_Score directory again.

How to Use

1. Get Notion, then
	- Copy below page into your Notion
		- https://intriguing-macaroni-6ea.notion.site/Data-Input-for-QOL-Score-3aad05e95cb148e4b659999a6d5202ec
2. Create a Notion Integration 
	- use this link https://www.notion.so/profile/integrations
3. Add the all databases on the page to the integration
4. Go into terminal, run, ```git clone https://github.com/kjhsu1/QOL_Score.git```
5. Open run_this_everyday.sh, change path to the directory on your computer
	- ex. "Users/name/Downloads/QOL_Score"
6. Open QOL_input_extraction.py with ```open QOL_input_extraction.py```
	- change NOTION_TOKEN, DATABASE_ID, DATABASE2_ID, DATABASE3_ID appropriately to your specific integration and database

When you run it everyday
- Fill out the Notion template daily ()
- Make sure to go into run_this_everyday.sh and change the entry number appropriately to the specific day
