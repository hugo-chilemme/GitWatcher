#!/usr/bin/python3
from threading import Thread
from bin.modules.setTimeout import setTimeout
from bin.libs.github import find_commits_by_users_and_searchterm,find_pullrequests_by_users_and_searchterm,  find_last_commit_by_repository, save_commit_to_database
from bin.libs.database import get_table, execute
from bin.labs.analyzer import get_xp_from_title
from flask import Flask, request
from datetime import datetime

import requests
import time

app = Flask(__name__)

# Create a dictionary of oldest commits
db_commits = get_table('commits', "ORDER BY ORDER_ID DESC")
oldest_commits = {commit['ID']: commit for commit in db_commits}

# Create a list of Github usernames from the 'users' table
users_table = get_table('users WHERE inactive = 0 AND Github IS NOT NULL')
github_list = [user['Github'] for user in users_table if user.get('Github')]
users = {user['Github']: user for user in users_table}

need_display = []
for commit in oldest_commits:
    need_display.append(commit)

typemode = "Repositories"

def process():
    global typemode
    """ main function """
    
    commits = []
    if typemode == "Repositories":
        commits = find_commits_by_users_and_searchterm(github_list, "holberton-")
        typemode = "Issues"
    else:
        commits = find_pullrequests_by_users_and_searchterm(github_list, "holberton-")
        typemode = "Repositories"
    
    for commit in commits:
        
        # variable initialization to avoid repetitions
        id = commit.get('ID')
        userId = commit.get('USER_ID')
        repository = commit.get('REPOSITORY')
        
        # check if you don't already have it
        if oldest_commits.get(id) is None:
            
                
            # Information about the commit retrieve
            if commit.get('TITLE') is None:
                
                CommitInfo = find_last_commit_by_repository(userId, repository)
            
                commit['TITLE'] = CommitInfo['title']
                
                if CommitInfo.get('author') is not None :
                
                    author = CommitInfo.get('author')
                    
                    # If the author is a Toulouse holbie
                    if author in github_list:
                        
                        # We change the author of the commit
                        commit['USER_ID'] = author
                
            # we score the title of the commit
            experience = get_xp_from_title(commit.get('TITLE'))
            
            # Add information in the commit
            commit['USER_ID'] = userId
            commit['XP'] = experience
            
            commit['XP_BEFORE'] = users[userId]['XP']
            commit['DISPLAYED'] = 0
            # The system may have detected that the author is not the creator of the repo
                
            
            # We have it on the "blacklist" of the next recoveries
            oldest_commits[id] = commit
            
            # Send to screen display list
            need_display.append(commit)
            
            # Database Saving
            save_commit_to_database(commit)
            
            
            # Announce in console
            print(f"New commit of {userId} ({experience}): {commit.get('TITLE')}")
                
          
    # We restart the process indefinitely every 15 seconds
    setTimeout(process, 15000)
    

def get_ranks():
    def sort_by_xp(user):
        return user[1]["XP"]
    
    def is_eligible(user):
        if user[1]['XP'] != 0:
            return True
        return False
    
    active_users = dict(filter(is_eligible, users.items()))
    sorted_users = dict(sorted(active_users.items(), key=sort_by_xp, reverse=True))
    return sorted_users

def get_rank(user):
    ranks = get_ranks()
    position = 0
    
    for rank in ranks.values():
        position += 1
        if rank.get('Github') == user.get('Github'):
            return position
 
 
@app.route('/api/v2/commits')
def home():
    
    limit = request.args.get('limit')
    limit_i = 0
    
    commits = need_display[:10]
    callback = []
    
    for k, commit in oldest_commits.items():
        
        if commit.get('DISPLAYED') == 0:
            
            if limit is None or limit_i < int(limit):
                user = users[commit.get('USER_ID')]
                
                commit['USER'] = {
                    'Session': user.get('Session'),
                    'Pseudo': user.get('Pseudo'),
                    'Avatar': user.get('Avatar'),
                }
                                    
                rank = get_rank(user)
                commit['USER']['Rank'] = rank
                callback.append(commit)
                limit_i += 1
            
    return callback


@app.route('/api/v2/commits/<commit_id>')
def commits_by_id(commit_id):
    if oldest_commits.get(commit_id) is not None:
        
        commit = oldest_commits.get(commit_id)
        user = users[commit.get('USER_ID')]
            
        commit['USER'] = {
            'Session': user.get('Session'),
            'Pseudo': user.get('Pseudo'),
            'Avatar': user.get('Avatar'),
        }
            
        return commit
    
    
@app.route('/api/v2/commits/<commit_id>/setDisplayed')
def commits_setDisplayed(commit_id):
    cf_connecting_ip = request.headers.get('Cf-Connecting-Ip')
    
    if oldest_commits.get(commit_id) is not None: 
    # and cf_connecting_ip == "80.125.5.170":
        oldest_commits[commit_id]['DISPLAYED'] = 1
        userId = oldest_commits[commit_id]['USER_ID']
        
        users[userId]['XP'] += oldest_commits[commit_id]['XP']
        execute("UPDATE users SET XP = {} WHERE Github = '{}'".format(users[userId]['XP'], userId))
        execute('UPDATE commits SET DISPLAYED = 1 WHERE ID = %(id)s', { 'id': commit_id })
            
    return { "ok": True}


@app.route('/api/v2/scoreboard')
def scoreboard():
    json = []
    
    def sort_by_xp(user):
        return user[1]["XP"]
    
    for user in users.values():
        if user.get('Github') and user.get('XP') != 0:
            json.append({
                "Rank": get_rank(user),
                "Experience": user.get('XP'),
                "Pseudo": user.get('Pseudo'),
                "Avatar": user.get('Avatar'),
                "Session": user.get('Session'),
                "Login": user.get('Github'),
            })
    json = sorted(json, key=lambda u: u['Rank'], reverse=True)
    return json

@app.route('/api/v2/version')
def version():
    return {
        "manifest": True,
        "version": "v0.2.91-beta",
    }


@app.route('/api/v2/address')
def address():
    cf_connecting_ip = request.headers.get('Cf-Connecting-Ip')
    return cf_connecting_ip


# Initialiser le dictionnaire pour stocker temporairement la température
temperature_cache = {
    "temperature": None,
    "timestamp": 0
}

@app.route('/api/v2/weather')
def weather():
    # latitude et longitude pour Toulouse, France
    latitude = '43.6045'
    longitude = '1.4440'
    # URL pour l'API de météo ouverte
    url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true'

    # Vérifier si la température est en cache et si elle a été mise à jour il y a moins d'une minute
    current_time = time.time()
    if temperature_cache['temperature'] is not None and (current_time - temperature_cache['timestamp']) < 60:
        temperature = temperature_cache['temperature']
    else:
        # Envoyer la requête à l'API
        response = requests.get(url)
        # Extraire la température à partir de la réponse JSON
        temperature = response.json()['current_weather']['temperature']
        # Mettre à jour la température dans le cache
        temperature_cache['temperature'] = temperature
        temperature_cache['timestamp'] = current_time

    # Retourner la température sous forme de dictionnaire JSON
    return {
        "temperature": temperature
    }

    

def start_flask():
    app.run(port=9999)

if __name__ == "__main__":
    process_thread = Thread(target=process)
    process_thread.start()
    start_flask()
    
