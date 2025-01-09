# QOL_Score
Using Notion API and pyscript to calculate QOL score

How to Use

1. Get Notion, then
	- Copy below 3 pages into your Notion
		- https://intriguing-macaroni-6ea.notion.site/Wake-and-Sleep-Times-bf14cc193e8849558710f634677e8dd6
		- https://intriguing-macaroni-6ea.notion.site/QOL-Score-3aad05e95cb148e4b659999a6d5202ec?pvs=4
		- https://intriguing-macaroni-6ea.notion.site/4-1-Efficiency-Tracking-e584cbb8d6214b8e9dd4ae4d879d83b1?pvs=4
2. Create a Notion Integration 
	- use this link https://www.notion.so/profile/integrations
3. Add the 3 databases to the integration
4. Download all files, put this in same folder/directory
5. Open run_this_everyday.sh, change path to the directory on your computer
6. Open QOL_input_extraction.py, change NOTION_TOKEN, DATABASE_ID, DATABASE2_ID, DATABASE3_ID appropriately


When you run it everyday
- Make sure to go into run_this_everyday.sh and change the entry number appropriately
- Don't run multiple times a day, it'll mess up the streak counter
