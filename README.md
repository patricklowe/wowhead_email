# wowhead_email
Collect character data from Blizzar dAPI, then collects data from Wowhead, coompare available activities (from Wowhead) with required achievements (from character API), compile a HTML table of To-Do's and send email to yourself

## Email Login
For login use your own email and login password. This is setup for Gmail and will require adjustments for other hosts
	
	server.login("YOUR_EMAIL@gmail.com","YOUR_PASSWORD")
  
## Character API
For Blizzard API use your own client ID and Secret ID, setup using the Blizzard API.
		
		response = create_access_token('CLIENT_ID', 'SECRET_ID')
 
## Characters and Servers
For searching a character enter their name and server. Accents require special code. Use only lowercase. For exmaple "Míne" will be:
    
		character = 'm%C3%ADne'
  		server = 'YOUR_SERVER'
