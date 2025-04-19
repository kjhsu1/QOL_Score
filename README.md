# QOL_Score
Using Notion API, Python, Shell to calculate QOL score

How to Use

1. Go into terminal, run, ```git clone https://github.com/kjhsu1/QOL_Score.git```
	- Make sure to go into ```cd /Applications``` to git clone
2. Open All_in_one_QOL_input_extraction.py, All_in_one_QOL_score_compute.py, and UI.py and change variable, ```user``` to your name.
	- ex. ```user = "Kenta"```

*Note: New User Should download anaconda, then pip install all of the required modules using environment.yml
- After downloading conda...
1. Run ```conda env create -f QOL_score/For_new_users/environment.yml```
	- make sure you run above in the /Applications directory
2. Then run ```conda activate QOL_env```
	- QOL_env is the name of the env defined in the environment.yml file. 

When Running Everday
1. On Mac, go to Applications to open the Automater app.
2. Create new "application"->go to search bar and type "Run Shell Script"
	- the script should be
	```
	/Applications/QOL_Score/For_new_users/run_ui.sh
	```
3. Save the application to desktop, you should now see it.
	- if you double click, the app should run. 


*NOTE: If you want to run run_this_everyday.sh in the Archive directory properly, you need to take out all the files in Archive directory and move it to the QOL_Score directory again.