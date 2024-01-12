# This is the legacy/1.0 branch, which is two years out of date! For the automatic overhaul, see the master branch.
 
 # TelstraCallToCSV
 ### Convert your Telstra call logs to CSV files!
 
 This Python script allows you to easily convert your Telstra call logs to CSV files so you can open them in a spreadsheet program like LibreOffice Calc.
 
 #### Why?
 A while ago, Telstra stopped providing downloads for CSV files of your call logs. Now, they are only accessible from the My Telstra interface, and it is not possible to download them. This script aims to fix this problem by allowing you to easily convert your call logs to CSV, just like you could before.
 #### How?
 You will need a browser which has sufficient developer tools (Firefox, Chromium/Chrome and Safari* all do). Here, instructions on obtaining the file are shown for Firefox, but the process does not differ much between browsers.
 
 Once you have cloned the repository:
 
 1. Go to your My Telstra homepage ([myservices.telstra.com](https://myservices.telstra.com.au)) and log in if needed.
 2. Right click, press *Inspect*, then *Network*, and type in the *Filter URLs* box "itemised".
 3. Scroll down on the My Telstra page to the plan you want to get the data for, and press *Manage [payment type]*.
 4. Scroll down and click on *Usage History*.
 5. Click on *Calls* across the top.
 6. Click on the icon below the bar with the *Calls* button which looks like a list.
 7. Using the arrow buttons, navigate to the month you want to save.
 8. In the *Inspect* sidebar you opened before, click on the last entry, click *Response* in the top bar, turn on the *Raw* option, select all the text (`Ctrl/Cmd+A`), and copy it (`Ctrl/Cmd+C`).
 9. Create a new file in the same folder you cloned the repository to called `data.json` and paste (`Ctrl/Cmd+V`) the data you copied there.
 10. Run `main.py` after `cd`ing to the place where you cloned the repository:
```bash
python3 main.py
```
 11. Look at `out.csv` in your favourite spreadsheet program, and hope it worked.
 
Note that this script does not support the Data and Messages logs, however this may be added in the future.
 
 **Safari requires you to enable developer tools in its Preferences first.*
