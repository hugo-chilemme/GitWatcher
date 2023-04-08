#!/usr/bin/python3
from bin.modules.setTimeout import setTimeout
from bin.libs.github import find_commits_by_users_and_searchterm, find_last_commit_by_repository, save_commit_to_database
from bin.libs.database import get_table
from bin.labs.analyzer import get_xp_from_title

# Create a dictionary of oldest commits
db_commits = get_table('commits', "ORDER BY ORDER_ID DESC")
oldest_commits = {commit['ID']: commit for commit in db_commits}
# Create a list of Github usernames from the 'users' table
github_list = [user['Github'] for user in get_table('users') if user.get('Github')]


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
            
            try:
                
                # Title recovery
                title = find_last_commit_by_repository(userId, repository)
                experience = get_xp_from_title(title)
                
                # Add in commit data
                commit['TITLE'] = title
                commit['XP'] = experience
                
                # We have it on the "blacklist" of the next recoveries
                oldest_commits[id] = commit
                
                # Database Saving
                save_commit_to_database(commit)
                
                # Announce in console
                print(f"New commit of {userId} ({experience}): {commit.get('TITLE')}")
                
            except TypeError:
                
                # The request was surely a rate limit, we stop the other requests
                break
          
    
    # We restart the process indefinitely every 15 seconds
    setTimeout(process, 15000)
 
    
if __name__ == "__main__":
    process()
    
