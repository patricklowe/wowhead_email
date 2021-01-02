# wowhead_email
Collect character data from API, compare with dailies on Wowhead, compile and send email to yourself
For login use your own email and login password.
	
	server.login("YOURS@gmail.com","YOUR_PASSWORD")
  
For Blizzard API use your own client ID and Secret ID:
		
		response = create_access_token('CLIENT_ID', 'SECRET_ID')
  
For searching a character enter their name and server. Accents require special code. Use only lowercase. For exmaple "Míne" will be:
    
		character = 'm%C3%ADne'
    server = 'YOUR_SERVER'
