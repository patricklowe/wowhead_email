import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create a new Access Token
def create_access_token(client_id, client_secret, region = 'eu'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    return response.json()

def get_character(character,server,token):
    search = "https://eu.api.blizzard.com/profile/wow/character/"+ server +"/"+ character +"/achievements?namespace=profile-eu&locale=en_GB&access_token="+token
    response = requests.get(search)
    return response.json()["achievements"]

def get_achievement_criteria(achievement_id):
    search = "https://eu.api.blizzard.com/data/wow/achievement/" + achievement_id + "?namespace=static-eu&locale=en_GB&access_token="+token
    response = requests.get(search)
    return response.json()["criteria"]


response = create_access_token('CLIENT_ID', 'SECRET_ID')
token = response['access_token']

character = 'YOUR_CHARACTER'
server = 'YOUR_SERVER'

character_achievements = get_character(character,server,token)
character_achievements = pd.DataFrame( character_achievements )
character_achievements = character_achievements.drop(['id'], axis=1)
char_achievements = pd.concat([character_achievements.drop(['achievement'], axis=1), character_achievements['achievement'].apply(pd.Series)], axis=1)
char_achievements = char_achievements.rename(columns={"id": "achievement_id",})
char_achievements = pd.concat([char_achievements.drop(['criteria'], axis=1), char_achievements['criteria'].apply(pd.Series)], axis=1)
char_achievements = char_achievements.rename(columns={"id": "criteria1_id",})
char_achievements = char_achievements.drop(['key','amount',0], axis=1)

# Check for Active Battle Pets on Wowhead, and filter needed achievements
url1 = "https://www.wowhead.com/"
url2 = "https://www.wowhead.com/world-quests/legion/eu"
url3 = "https://www.wowhead.com/world-quests/bfa/eu"
url4 = "https://www.wowhead.com/world-quests/sl/eu"
driver = webdriver.Chrome('C:/Users/YOUR_USER/Desktop/Untitled Folder/chromedriver')  

# Standard News
driver.get(url1)
html1 = driver.page_source
soup1 = BeautifulSoup(html1, "html.parser") 

# Legion WQ
driver.get(url2)
html2 = driver.page_source 
soup2 = BeautifulSoup(html2, "html.parser") 

#BFA WQ
driver.get(url3)
html3 = driver.page_source 
soup3 = BeautifulSoup(html3, "html.parser") 

# SL WQ
driver.get(url4)
html4 = driver.page_source 
soup4 = BeautifulSoup(html4, "html.parser")

driver.close()

wq_df = pd.DataFrame(columns=['Quest','Reward','Ends'])

# List Legion Quests
for thing in soup2.find_all('tr', class_="listview-row"):
     wq_df.loc[len(wq_df.index)] = [thing.find_all('td')[0].get_text(), thing.find_all('td')[1].get_text(),thing.find_all('td')[3].get_text()]

# List BFA Quests
for thing in soup3.find_all('tr', class_="listview-row"):
     wq_df.loc[len(wq_df.index)] = [thing.find_all('td')[0].get_text(), thing.find_all('td')[1].get_text(),thing.find_all('td')[3].get_text()]
        
# List SL Quests
for thing in soup4.find_all('tr', class_="listview-row"):
     wq_df.loc[len(wq_df.index)] = [thing.find_all('td')[0].get_text(), thing.find_all('td')[1].get_text(),thing.find_all('td')[3].get_text()]
        
# Get EU News
EU_News = soup1.find('div', class_="tiw-region",  attrs={"data-region":"EU"})


# In[44]:


# Battle Pets
#        SHADOWLANDS PETS NOT YET IN API
achievements = ['9686','9688','9690','9692','9694','9687','9689','9691','9693','9695','12089','12091','12092','12093','12094','12095','12096','12097','12098','12099']
# Filter for Battle Pet Achievements
battle_pets_df = char_achievements[ char_achievements['achievement_id'].isin(achievements)]
# Drop NULL, and unneccessary criteria columns
battle_pets_df = battle_pets_df.dropna(axis=1).reset_index().drop(['index','criteria1_id','is_completed'],axis=1)
# Expand downwards Child Criteria Column
battle_pets_df = battle_pets_df.explode('child_criteria').reset_index(drop=True)
# Expand across Child Criteria Column
battle_pets_df = pd.concat([battle_pets_df.drop(['child_criteria'], axis=1), battle_pets_df['child_criteria'].apply(pd.Series)], axis=1).drop(['amount'],axis=1)
# Filter for incompelte criteria
battle_pets_df = battle_pets_df[ battle_pets_df['is_completed']==False].reset_index(drop=True)
# Criteria Search Results
crit_df = pd.DataFrame(columns=['id', 'description'])
# Combine criteria text, based on ID
for criteria in achievements:
    for crit in get_achievement_criteria(criteria)['child_criteria']:
        crit_df.loc[len(crit_df.index)] = [crit['id'],crit['description']]
# Merge criteria text with incomplete battle pet achievements, based on matching ID's
battle_pets_df = pd.merge(battle_pets_df, crit_df, on="id")
# Dictionary of Trainer and their World Quest
trainers_quest = {'description' : ['Nightwatcher Merayl', 'Bodhi Sunwayver','Amalia','Sir Galveston','Grixis Tinypop','Odrogg','Robert Craig','Trapper Jarrun','Aulier','Master Tamer Flummox','Varenne','Xorvasc','Bredda Tenderhide','Durian Strongfruit','Gnasher','Bucky','Snozz','Gloamwing','Shadeflicker','Corrupted Blood of Argus',"Mar'cuus",'Watcher','Bloat','Earseeker','Pilfer','Minixis','One-of-Many','Deathscreech'],
'Quest': ["Training with the Nightwatchers","Fight Night: Bodhi Sunwayver","Fight Night: Amalia","Fight Night: Sir Galveston","Tiny Poacher, Tiny Animals","Snail Fight!","My Beasts's Bidding","Jarrun's Ladder","The Master of Pets","Flummoxed","Chopped","Dealing with Satyrs","Training with Bredda","Training with Durian","Gnasher","Bucky","Snozz","Gloamwing","Shadeflicker","Corrupted Blood of Argus","Mar'cuus","Watcher","Bloat","Earseeker","Pilfer","Minixis","One-of-Many","Deathscreech"]}
# Convert to DF
trainers_quest_df = pd.DataFrame.from_dict(trainers_quest)
# Merge Quest name into battle pets dataframe
battle_pets_df = pd.merge(battle_pets_df, trainers_quest_df, on="description")
find = battle_pets_df['Quest'].unique()
wq_df[ wq_df['Quest'].isin(find) ]['Quest']
available1 = pd.merge(battle_pets_df, wq_df, on="Quest")


# In[8]:


# Torghast
achievements = ['14809','14810']
torghast_df = char_achievements[ char_achievements['achievement_id'].isin(achievements)]
torghast_df = torghast_df.dropna(axis=1).reset_index().drop(['index','criteria1_id','is_completed'],axis=1)
torghast_df = torghast_df.explode('child_criteria').reset_index(drop=True)
torghast_df = pd.concat([torghast_df.drop(['child_criteria'], axis=1), torghast_df['child_criteria'].apply(pd.Series)], axis=1).drop(['amount'],axis=1)
torghast_df = torghast_df[ torghast_df['is_completed']==False].reset_index(drop=True)
crit_df = pd.DataFrame(columns=['id', 'description'])

for criteria in achievements:
    for crit in get_achievement_criteria(criteria)['child_criteria']:
        crit_df.loc[len(crit_df.index)] = [crit['id'],crit['description']]

torghast_df = pd.merge(torghast_df, crit_df, on="id")
wings = []
for wing in EU_News.find_all('div', {"id" : lambda L: L and L.startswith('EU-group-torghast-wings-line-')}):
    wings.append(wing.get_text() )
available2 = torghast_df[ torghast_df['description'].isin(wings) ]


# Ampitheatre
achievements = ['14353']
ampitheatre_df = char_achievements[ char_achievements['achievement_id'].isin(achievements)]
ampitheatre_df = ampitheatre_df.dropna(axis=1).reset_index().drop(['index','criteria1_id','is_completed'],axis=1)
ampitheatre_df = ampitheatre_df.explode('child_criteria').reset_index(drop=True)
ampitheatre_df = pd.concat([ampitheatre_df.drop(['child_criteria'], axis=1), ampitheatre_df['child_criteria'].apply(pd.Series)], axis=1).drop(['amount'],axis=1)
ampitheatre_df = ampitheatre_df[ ampitheatre_df['is_completed']==False].reset_index(drop=True)
crit_df = pd.DataFrame(columns=['id', 'description'])

for criteria in achievements:
    for crit in get_achievement_criteria(criteria)['child_criteria']:
        crit_df.loc[len(crit_df.index)] = [crit['id'],crit['description']]

ampitheatre_df = pd.merge(ampitheatre_df, crit_df, on="id")
ampi_quest = {'description' : ['Xavius','Gul\'dan','Kil\'jaeden','Argus, The Unmaker','Jaina','Azshara','N\'Zoth'],
'Quest': ['Niya, As Xavius',"Senthii, As Gul'dan","Glimmerdust, As Kil'jaeden","Mi'kai, As Argus","Glimmerdust, As Jaina","Astra, As Azshara","Dreamweaver, As N'Zoth"]}
ampi_quest_df = pd.DataFrame.from_dict(ampi_quest)
ampitheatre_df = pd.merge(ampitheatre_df, ampi_quest_df, on="description")
available3 = ampitheatre_df[ ampitheatre_df['description'] == EU_News.find('div', id="EU-group-star-lake-amphitheater-line-0").a.get_text()]

# Mechagon Visitor
available4 = ''
try:
        visitor = EU_News.find('div', id="EU-group-mechagon-visitors-line-0").get_text()
        if visitor == 'Archivist Bitbyte':
            available4 = visitor
        elif visitor == 'Steelsage Mao':
            available4 = visitor
        elif visitor == 'Steelsage Gao <Madam Goya Operative>':
            available4 = visitor
except AttributeError:
    available4 = 'Mechagon ERROR'

url = "https://www.wowhead.com/"
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\YOUR_USER\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome('C:/Users/YOUR_PATH/hromedriver',options=options)  
driver.get(url)
driver.find_element_by_xpath('//*[@id="tiw-switcher-region"]/a[2]').click()
driver.find_element_by_xpath('//*[@id="tiw-switcher-expansion"]/a[3]').click()

html = driver.page_source
souper = BeautifulSoup(html, "html.parser")
driver.close()

assaults_df = pd.DataFrame(columns=['Assault', 'Description','Duration'])

for region in souper.find_all('div', attrs={"data-region":"EU"}):
    for element in region.find('div',attrs={"data-tiw-section":"warfront-9734"}):
        if element.find('a'):
            assault = element.find('a').text
        if element.find('span', class_="slider-labels-title"):
            title = element.find('span', class_="slider-labels-title").text
        if element.find('span', class_="slider-labels-values"):
            value = element.find('span', class_="slider-labels-values").text
    assaults_df = assaults_df.append({'Assault':assault,'Description':title,'Duration':value}, ignore_index=True)
    for element in region.find('div',attrs={"data-tiw-section":"warfront-10288"}):
        if element.find('a'):
            assault = element.find('a').text
        if element.find('span', class_="slider-labels-title"):
            title = element.find('span', class_="slider-labels-title").text
        if element.find('span', class_="slider-labels-values"):
            value = element.find('span', class_="slider-labels-values").text
    assaults_df = assaults_df.append({'Assault':assault,'Description':title,'Duration':value}, ignore_index=True)
    for element in region.find('div',attrs={"data-tiw-section":"assaults-nzoth-assaults-major"}):
        if element.find('a'):
            assault = element.find('a').text + " - Major"
        if element.find('span', class_="slider-labels-title"):
            title = element.find('span', class_="slider-labels-title").text
        if element.find('span', class_="slider-labels-values"):
            value = element.find('span', class_="slider-labels-values").text
    assaults_df = assaults_df.append({'Assault':assault,'Description':title,'Duration':value}, ignore_index=True)
    for element in region.find('div',attrs={"data-tiw-section":"assaults-nzoth-assaults-minor"}):
        if element.find('a'):
            assault = element.find('a').text + " - Minor"
        if element.find('span', class_="slider-labels-title"):
            title = element.find('span', class_="slider-labels-title").text
        if element.find('span', class_="slider-labels-values"):
            value = element.find('span', class_="slider-labels-values").text
    assaults_df = assaults_df.append({'Assault':assault,'Description':title,'Duration':value}, ignore_index=True)

# World Bosses
bosses_df = pd.DataFrame(columns=['Boss', 'Expansion'])
for boss in EU_News.find_all('div',attrs={"id" : lambda L: L and L.startswith("EU-group-epiceliteworldsl-line-")}):
    bosses_df = bosses_df.append({'Boss':boss.text,'Expansion':'Shadowlands'}, ignore_index=True)
for boss in EU_News.find_all('div',attrs={"id" : lambda L: L and L.startswith("EU-group-epiceliteworldbfa-line-")}):
    bosses_df = bosses_df.append({'Boss':boss.text,'Expansion':'BfA'}, ignore_index=True)
for boss in EU_News.find_all('div',attrs={"id" : lambda L: L and L.startswith("EU-group-epiceliteworld-line-")}):
    bosses_df = bosses_df.append({'Boss':boss.text,'Expansion':'Legion'}, ignore_index=True)


# Emissary Toys Needed
emissaries = {'Reputation' : ['Nightfallen','Highmountain','Dreamweaver','Army of the Light','Armies of Legionfall'],
'Rewards': ['Llothien Prowler',"Highmountain Elderhorn",'Wild Dreamrunner','Avenging Felcrusher, Blessed Felcrusher, Glorious Felcrusher','Orphaned Felbat'],
'Active':[False,False,False,False,False],
'Ends':[0,0,0,0,0]}
emissaries_df = pd.DataFrame.from_dict(emissaries)
for emm in EU_News.find_all('div',attrs={"id" : lambda L: L and L.startswith("EU-group-emissary6")}):
    text = str(emm.find('img', alt=True)['alt'].replace(' Icon',''))
    try:
        ends = str(emm.find('div', class_="tiw-line-ending").get_text())
    except AttributeError:
        pass
    for rep in emissaries_df['Reputation']:
        if rep == text:
            emissaries_df.loc[emissaries_df['Reputation'] == rep,'Active'] = True
            emissaries_df.loc[emissaries_df['Reputation'] == rep,'Ends'] = ends
    
available5 = emissaries_df[ emissaries_df['Active']==True]


# World Quest Achievements
achievements = ['13054','13285','13026','14233','14737','14671','14741','14765','14766']
quest_ach_df = char_achievements[ char_achievements['achievement_id'].isin(achievements)]
quest_ach_df = quest_ach_df.dropna(axis=1).reset_index().drop(['index','criteria1_id','is_completed'],axis=1)
quest_ach_df = quest_ach_df.explode('child_criteria').reset_index(drop=True)
quest_ach_df = pd.concat([quest_ach_df.drop(['child_criteria'], axis=1), quest_ach_df['child_criteria'].apply(pd.Series)], axis=1).drop(['amount'],axis=1)
quest_ach_df = quest_ach_df[ quest_ach_df['is_completed']==False].reset_index(drop=True)
crit_df = pd.DataFrame(columns=['id', 'description'])
for criteria in achievements:
    try:
        for crit in get_achievement_criteria(criteria)['child_criteria']:
            crit_df.loc[len(crit_df.index)] = [crit['id'],crit['description']]
    except KeyError:
        pass

quest_ach_df = pd.merge(quest_ach_df, crit_df, on="id")
ach_quest = {'name' : ['Sabertron Assemble', 'Upright Citizens','7th Legion Spycatcher','Tea Tales','What Bastion Remembered',
                       "Something's Not Quite Right....",'Aerial Ace','Ramparts Racer','Parasoling'],
'Quest': ["Sabertron","Not Too Sober Citizens Brigade","Don't Stalk Me, Troll",'Tea Tales: Lost Sybille','Thing Remembered',
         'Tough Crowd','Flight School: FlappingFrenzy',"It's Race Day in the Ramparts!",'Parasol Peril']}
ach_quest_df = pd.DataFrame.from_dict(ach_quest)
quest_ach_df = pd.merge(quest_ach_df, ach_quest_df, on="name")
find = quest_ach_df['Quest'].unique()
wq_df[ wq_df['Quest'].isin(find) ]['Quest']
available6 = pd.merge(quest_ach_df, wq_df, on="Quest")

available1 = available1.groupby('description').agg(lambda x: ','.join(x.unique())).reset_index()
available2 = available2.groupby('description').agg(lambda x: ','.join(x.unique())).reset_index()
available3 = available3.groupby('description').agg(lambda x: ','.join(x.unique())).reset_index()
available6 = available6.groupby('description').agg(lambda x: ','.join(x.unique())).reset_index()
to_do_df = pd.DataFrame(columns=['Achievement', 'description', 'Ends'])
for i, row in available1.iterrows():
    to_do_df.loc[len(to_do_df.index)] = [ row['name'], row['description'], row['Ends']]
for i, row in available2.iterrows():
    to_do_df.loc[len(to_do_df.index)] = [ row['name'], row['description'], 'Weekly Reset']
for i, row in available3.iterrows():
    to_do_df.loc[len(to_do_df.index)] = [ row['name'], row['description'], row['Quest']]
if len(available4) > 0:
    to_do_df.loc[len(to_do_df.index)] = [ 'Junkyard Architect', available4, 'Daily Reset']
for i, row in available5.iterrows():
    to_do_df.loc[len(to_do_df.index)] = [ row['Reputation'], row['Rewards'], row['Ends']]
for i, row in available6.iterrows():
    to_do_df.loc[len(to_do_df.index)] = [ row['name'], row['Quest'], row['Ends']]
for i, row in bosses_df.iterrows():
    to_do_df.loc[len(to_do_df.index)] = [ row['Boss'], row['Expansion'], 'Weekly Reset']


me = 'YOUR_EMAIL'
you  = 'TO_EMAIL'

msg = MIMEMultipart('alternative')
msg['Subject'] = "Link"
msg['From'] = me
msg['To'] = you

text = "Morning! Here is what you can do:"
html = to_do_df.to_html()

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)

server = smtplib.SMTP("smtp.gmail.com:587")
server.starttls()
server.login("YOURS@gmail.com","YOUR_PASSWORD")
server.sendmail(me, you, msg.as_string())
server.quit()
