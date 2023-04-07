#!/usr/bin/python3
from bin.modules.setInterval import setInterval
from bin.libs.github import get_commits, get_last_commit_repository, save_commit
from bin.libs.database import get_table

# Create a dictionary of oldest commits
oldest_commits = {commit[0]: commit for commit in get_table('commits')}

# Create a list of Github usernames from the 'users' table
github_list = [user[3] for user in get_table('users') if user[3]]


def process():
    """ main function """
    # Retrieving the last 20 newsfeed commits
    commits = get_commits(github_list)
    for commit in commits:
        
        # check if you don't already have it
        if oldest_commits.get(commit['ID']) is None:
            
            # Title recovery
            commit['TITLE'] = get_last_commit_repository(commit['USER_ID'], commit['REPOSITORY'])
            
            # We have it on the "blacklist" of the next recoveries
            oldest_commits[commit['ID']] = commit
            
            # Database Saving
            save_commit(commit)
            
            # Announce in console
            print(f"New commit of {commit['USER_ID']}: {commit['TITLE']}")
            
setInterval(process, 15000)    
