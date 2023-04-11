#!/usr/bin/python3
from threading import Thread
from bin.modules.setTimeout import setTimeout
from bin.libs.github import find_commits_by_users_and_searchterm, find_last_commit_by_repository, save_commit_to_database
from bin.libs.database import get_table
from bin.labs.analyzer import get_xp_from_title
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Create a dictionary of oldest commits
db_commits = get_table('commits', "ORDER BY ORDER_ID DESC")
oldest_commits = {commit['ID']: commit for commit in db_commits}

# Create a list of Github usernames from the 'users' table
users = get_table('users')
github_list = [user['Github'] for user in users if user.get('Github')]
need_display = []

def process():
    """ main function """
    
    # Retrieving the last 20 newsfeed commits with the research topic "holberton-"
    commits = find_commits_by_users_and_searchterm(github_list, "holberton-")
    
    for commit in commits:
        
        # variable initialization to avoid repetitions
        id = commit.get('ID')
        userId = commit.get('USER_ID')
        repository = commit.get('REPOSITORY')
        
        # check if you don't already have it
        if oldest_commits.get(id) is None:
            
                
            # Information about the commit retrieve
            CommitInfo = find_last_commit_by_repository(userId, repository)
            
            # Title recovery
            title = CommitInfo['title']
            
            # we score the title of the commit
            experience = get_xp_from_title(title)
            
            # Add information in the commit
            commit['USER_ID'] = userId
            commit['TITLE'] = title
            commit['XP'] = experience
            
            # The system may have detected that the author is not the creator of the repo
            if CommitInfo.get('author') is not None :
                
                author = CommitInfo.get('author')
                
                # If the author is a Toulouse holbie
                if author in github_list:
                    
                    # We change the author of the commit
                    commit['USER_ID'] = author
                
            
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
    
@app.route('/api/v2/commits')
def home():
    cf_connecting_ip = request.headers.get('Cf-Connecting-Ip')
        
    commit = {}
    if len(need_display) > 0:
        commit = need_display[0]
        target = None
        for user in users:
            if user.get('Github') == commit.get('USER_ID'):
                target = user
                break
        
        commit['USER'] = {
            "Pseudo": target['Pseudo'],
            "Avatar": target['Avatar'],
            "Session": target['Session'],
        }
        
        if cf_connecting_ip == "80.125.5.170":
            need_display.pop(0)
            print('deleted')
            
    return commit


@app.route('/api/v2/version')
def version():
    return {
        "manifest": True,
        "version": "v0.0.18-beta",
    }

@app.route('/api/v2/address')
def address():
    cf_connecting_ip = request.headers.get('Cf-Connecting-Ip')
    return cf_connecting_ip


def start_flask():
    app.run(port=9999)

if __name__ == "__main__":
    process_thread = Thread(target=process)
    process_thread.start()
    start_flask()
    
