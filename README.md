# Aurora - A DayZ/Discord Bot Written In Python3
* # Features:
    * Server Information
        * Name
        * IP : Port
        * Running Status
        * DayZ Version
        * Connected Players
        * In-Game Time
        * Time Acceleration
        * Server FPS
        * 1st/3rd Person Status
        * Map
        * Hive
	* Permissions System
		* 3 Tiers
			* Staff
			* Moderators
			* Administrator
    * Activity Cycling
        * Server Player Count
        * Status (Online, Not Available, Idle)
        * User Configurable
        * Multiple Server Support
    * Command Cooldowns
        * Channel and User Cooldowns
        * User Configurable
    * Proper Error Handling
    * Basic Logging
    * Server Technical Details
        * DayZ Process CPU% Utilization
        * DayZ Process RAM% Utilization
        * Server Uptime
        * Total CPU% Utilization
        * Total MEM% Utilization
        * CPU Cores
        * Manager Application
        * Version
        * Running Node
    * Multiple Server Support
        * Configuration File (config.json)
        * Commands Display by 'ALL' or 'SERVERNAME'
    * BEC Broadcast
        * Broadcast to 'ALL' or 'SERVERNAME'
        * Limited to a Staff/Admin Role
    * Mods Listing for Server
        * Displays 'ALL' or 'SERVERNAME'
        * Links To Mod Workshop Page For Each Mod
    * Player List
        * Limited to Staff/Admin Role
        * Displays 'ALL' or 'SERVERNAME'
        * Supports 120 Players
        * Links Playername To CFTools Profile ID Page
        * Displays Player Count/Max Players
    * Leaderboard
        * Displays Top 20 in Kills or Played Time
        * Links Playername to CFTools Profile ID Page
    * Schedule
        * Displays Upcoming Server Event: Restart, etc.
    * Network
        * Displays IDName and Full Name for Every Server in config file.
    * Reload
        * Reload config.json while bot is running.
    * Report Function
        * Can Post to Staff/Admin Channel With Player Abuse Reports
    * Responding via PM
        * Bot Responds Either In-Channel or PM Depending on Source of Command

* Requirements:
    * [Discord.py 1.0.0a](https://github.com/Rapptz/discord.py/tree/rewrite) 
        * Discord Python Library
    * [AIOHTTP](https://aiohttp.readthedocs.io/en/stable)
        * Asynchronous HTTP connections
    * [ASyncIO](https://docs.python.org/3/library/asyncio.html)
        * Asynchronous Library

* Installation Instructions:
    * Install Python 3 (3.4+ Required)
        * https://www.python.org/downloads/

	* Install Git
		* https://git-scm.com/downloads
    
    * Create a Discord Bot
        * https://discordpy.readthedocs.io/en/rewrite/discord.html

    * Install discord-rewrite 1.0.0a using:
        ```python -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py```

        It will install required dependencies automatically.

    * Install other required libraries
        * ``` python -m pip install asyncio ```
        * ``` python -m pip install aiohttp ```
    
    * Edit config.example.json, add in your information:

```json
{
	"discord_token" : "DISCORD_BOT_TOKEN",
	"api_url" : "https://omegax.cftools.de/api/v1/",
	"report_channel" : "REPORTS_CHANNEL_ID",
	"staff_roles" : "STAFF_ROLE",
	"guild_id" : "DISCORD_SERVER_ID",
	"status_refresh": 60,
	"delayed_refresh": 3600,
	"activity_rotate": true,
	"activity_refresh": 10,
	"cooldown_channel": 600,
	"cooldown_user": 60,
	"permissions": {
		"staff": ["Staff", "Moderators", "Administrators"],
		"moderators": ["Moderators", "Administrators"],
		"admins": ["Administrators"]
	},
	"server" : [
		{
			"name" : "SERVER_NAME",
			"address" : "IP:PORT",
			"service_id" : "SERVICE_ID",
			"service_api_key" : "SERVICE_API_KEY",
			"server_url" : "WEBSITE_URL",
			"server_icon": "URL_FOR_ICON"
		}
	]        
}
```

    * Save as config.json
    
    * Run Bot:
		python aurora.py

