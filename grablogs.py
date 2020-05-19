import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup
import cfscrape
import requests

def scrapeteams(division):
    """
    Scrapes urls for teams from RGL website, returns as an array of team names.
    Requires division name as input (Invite, Advanced, etc)
    This will have to be updated from season to season as the below ids change each season.
    """
    seasonid='72' #id for RGL season 3, changes each season
    leagueid='40' #id for Trad. Sixes, change if you want to do this for prolander or something
    divids={'invite':'404','advanced':'405','main':'406','intermediate':'407','amateur':'410','newcomer':'411'} #Ids for each division
    try:

        url='https://rgl.gg/Public/LeagueTable.aspx?g='+divids[division.lower()]+'&s='+seasonid+'&r='+leagueid #URL for each division
        scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
        # Or: scraper = cfscrape.CloudflareScraper()  # CloudflareScraper inherits from requests.Session
        html=scraper.get(url).content #Scrape html from RGL website
        teamnames=pd.read_html(html)[1]['Team Name'].values #grab team names from table in html
        soup = BeautifulSoup(html, 'html.parser') #Use beautifulsoup to grab links from table in html
        table = soup.findAll('table')[1] #find tables

        links = [] #make empty list of links
        for tr in table.findAll("tr"): #search through table to grab links
            trs = tr.findAll("td")
            for each in trs:
                try:
                    link = each.find('a')['href']
                    links.append(link) #append to list of links
                except:
                    pass
    except KeyError: #Tell people if they didn't put a correct division name in.
        print('Error, division name needs to be one of: Invite,Advanced,Main,Intermediate,Amateur,Newcomer')
        return
    return {teamnames[i]:'https://rgl.gg/Public/teamb'+links[i][4:] for i in range(len(teamnames))} #return the dictionary of team names

def scrapeplayers(teamdict):
    """
    Scrapes steamids for players on each team from RGL website, uses input from function above.
    """
    players_list=[] #Initialize empty players list
    for key in teamdict: #Loop through teams
        scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
        # Or: scraper = cfscrape.CloudflareScraper()  # CloudflareScraper inherits from requests.Session
        url=teamdict[key] #Get url for that team
        html=scraper.get(url).content #grab html from url
        player_ids=list(pd.read_html(html)[0].SteamId.astype(str).values) #get list of steamids
        players_list.append(player_ids) #append player ids to the list of team player ids
    teams_list=list(teamdict.keys())
    teamplayerids={teams_list[i]:players_list[i] for i in range(len(teams_list)) if len(players_list[i])>5} #dictionary with team names and playerids
    return(teamplayerids)

def get_player_logs(player_id,start_season_log):
    """
    Uses logs.tf api to grab logs. Requires a starting log (start_season_log) and a playerid as input
    """
    loglist=False
    while loglist==False: #try and grab the list of logs from logs.tf, can be edited to check for a longer number of logs if necessary.
        try:
            loglist=requests.get('http://logs.tf/api/v1/log?player='+str(player_id)+'&limit=1000')
        except: #wait 10 seconds and try again if this didn't work.
            time.sleep(10)
            print('Error getting logs list, trying again')

    #convert to json and extract log ids.
    loglist_json=loglist.json()
    logs=loglist_json['logs']
    logids=np.array([int(log['id']) for log in logs])
    return(logids[logids>start_season_log]) #return only logs newer than the initial id.

def get_log_ids(teamplayerids,start_season_log):
    """
    Grab unique logs that have at least 8 of every player in a division
    recorded as playing in the server.
    """
    logidarray=np.array([])
    for team in teamplayerids:
        for player_id in teamplayerids[team]:
            logidarray=np.append(logidarray,get_player_logs(player_id,start_season_log)) #grab logs for each player on each team.
    unique,counts=np.unique(logidarray,return_counts=True)
    logids_trimmed=unique.astype(int)[counts>=8] #grab logs that only have 8 or more players playing
    return(logids_trimmed)

def commid_to_usteamid(commid):
    """
    Converts steamids to the version used by logs.tf to search. Thanks to yosh for this.
    """
    steamid64ident = 76561197960265728
    usteamid = []
    usteamid.append('[U:1:')
    steamidacct = int(commid) - steamid64ident

    usteamid.append(str(steamidacct) + ']')

    return ''.join(usteamid)


def generate_round_data(logid,usteamids):
    """
    Checks a log to see if there are 4 players on each team. Gives the winner of and duration of each round.
    Can easily be modified to just return the logid but it's more efficient to only access the logs once.
    """

    log=requests.get('http://logs.tf/json/'+str(logid)) #use requests to grab the log
    log=log.json() #turn into json
    playerids=np.array([*log['players']]) #players info from log
    player_team=np.array([log['players'][player]['team'] for player in log['players']]) #get the teams for each player
    red_playerids=playerids[player_team=='Red'] #get the red player ids
    blu_playerids=playerids[player_team=='Blue'] #get the blue player ids


    blu_team=False #sets blue and red team to False (easy to check if log was actually a scrim or match)
    red_team=False

    #Sets the team names to be the team names if >=4 players on each team are correct.
    for team in usteamids:
        if len(np.intersect1d(usteamids[team],blu_playerids))>=4:
            blu_team=team
        elif len(np.intersect1d(usteamids[team],red_playerids))>=4:
            red_team=team

    #getting map names and round durations (useful information for statistical model, you might not want this)
    mapname=log['info']['map'].split('_')[1].lower() #what is the name of the map (ignoring prefix and suffix)
    winner=np.array([rounds['winner'] for rounds in log['rounds']]) #who won the round?
    blu_score=np.array([1 if win=='Blue' else 0 for win in winner]).astype(int) #binary, 1 for Blue winning, 0 for red winning
    duration=np.array([rounds['length'] for rounds in log['rounds']]) #Duration of each round

    #check to see if the map went to timelimit. If so, ignore last round. This is so the round durations arent affected by truncated rounds.
    if (np.sum(blu_score)==log['teams']['Blue']['score'])&(np.sum(1-blu_score)==log['teams']['Red']['score']):
        pass
    else:
        winner=winner[:-1]
        duration=duration[:-1]
        blu_score=blu_score[:-1]
    #return an array of [logid,map name,blue team name, red team name, blu_score, round duration] for each round
    return(np.array([np.full(len(winner),logid),np.full(len(winner),mapname),np.full(len(winner),blu_team),np.full(len(winner),red_team),blu_score,duration]).T)

def check_if_scrims(logids,usteamids):
    """
    Checks whether logs in our list of possible scrim logs have players on the correct teams.
    For any log with >=8 players from a given division, checks to see if there are >=4 on the same team.
    """
    points_table=np.empty(shape=(0,6)) #create an empty table for points
    for i in range(len(logids)): #loop through logids
        try:
            points_log=generate_round_data(logids[i],usteamids) #generate data
            if (points_log[0][3]=='False')|(points_log[0][2]=='False'): #if either of these are False then this is NOT a scrim or match.
                pass
            elif points_log[0][1] in ['process','gullywash','snakewater','metalworks','sunshine','product','clearcut','villa']: #check to see if it's one of the RGL sanctioned maps
                points_table=np.append(points_table,points_log,axis=0)
        except:
            pass
        print('Working through log '+str(i+1)+' of '+str(len(logids)),end='\r')
    return(points_table)

def main():
    print('Enter Division (Invite,Advanced,Main,Intermediate,Amateur,Newcomer)')
    division=input()
    print('Scraping Player IDs from RGL.gg')
    teamdict=scrapeteams(division)
    teamplayerids=scrapeplayers(teamdict)
    print('Enter a log id for the start of when you want to grab team logs.')
    print('RGL Season 2 Ended on April 8th. The first logid of April 9th was 2518452')
    start_season_log=int(input())
    print('Grabbing List of Logs with 8 or more players from logs.tf')
    print('This may take a few minutes')
    logids_trimmed=get_log_ids(teamplayerids,start_season_log)
    usteamids={key:[commid_to_usteamid(steamid) for steamid in teamplayerids[key]] for key in teamplayerids.keys()}
    print('Checking whether each log is a scrim. This may take a few minutes')
    points_table=check_if_scrims(logids_trimmed,usteamids)
    points_table=points_table[points_table[:,5].astype(float)>0]
    points_data=pd.DataFrame(points_table,columns=['log_id','map','blu_team','red_team','blu_win','round_duration'])
    print('Please enter a filename to save data to')
    filename=input()
    points_data.to_csv(filename+'.csv',index=False)
    print('Done, file saved to '+filename+'.csv')
main()
quit()
