#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import hashlib
from bin.libs.database import execute

def find_commits_by_users_and_searchterm(users=[], searchterm=""):

    # Creating a string with +user%3A as delimiter
    userstring = "+user%3A".join(users)

    # URL formation
    url = f"https://github.com/search?o=desc&q={searchterm}+user%3A{userstring}&s=updated&type=Repositories"

    # Found commits will be stored here
    commits = []

    # Sending the request
    r = requests.get(url)

    # Status check : 200 = SUCCESS
    if r.status_code == 200:

        # Conversion of string to html parse
        soup = BeautifulSoup(r.content, 'html.parser')

        # We retrieve all items that are supposed to be commits
        repoListItems = soup.find_all(class_='repo-list-item')

        # We reverse the list to start from the oldest commit to the most recent
        repoListItems.reverse()

        # Analysis of each commit
        for item in repoListItems:

            # We verify that the element we have retrieved is indeed a commit
            href = item.find(class_='v-align-middle')['href']

            if href is not None:
                # Get Github ID and Repository by url
                userId = href.split('/')[1]
                repository = href.split('/')[2]

                # Commit date retrieval
                datetime = item.find('relative-time')['datetime']

                # Creating a fake but unique ID
                id = hashlib.md5(f"{userId}-{datetime}".encode('utf-8')).hexdigest()

                commits.append({
                    'USER_ID': userId, 
                    'ID': id, 
                    'REPOSITORY': repository,
                    'DATETIME': datetime
                })
              
    # Returns the list of commits
    return commits


def find_last_commit_by_repository(userId, repository):
    
    # URL formation
    api_url = f"https://api.github.com/repos/{userId}/{repository}/commits"

    # Sending the request
    r = requests.get(api_url)

    # Status check : 200 = SUCCESS
    if r.status_code == 200:
        
        data = {}
        
        # Reusing the variable to retrieve the json
        r = r.json()[0]
        
        # Retrieving the title
        data['title'] = r['commit']['message']
        data['title'] = data['title'].replace('\n', '')
        
        if r['author'] and r['author']['login']:
            
            data['author'] = r['author']['login']
        
        # Returning the title commit
        return data
    
    raise TypeError(f"API returned error code {r.status_code}")


def save_commit_to_database(commit):
    
    # Structuring of the request
    query = """
        INSERT INTO commits(ID, USER_ID, REPOSITORY, TITLE, DATETIME, XP)
        VALUES(%(id)s, %(user_id)s, %(repository)s, %(title)s, %(datetime)s, %(xp)s)
    """
    
    # Data to insert
    parameters = {
        'id': commit['ID'],
        'user_id': commit['USER_ID'],
        'repository': commit['REPOSITORY'],
        'title': commit['TITLE'],
        'datetime': commit['DATETIME'],
        'xp': commit['XP']
    }

    # Query Execution
    execute(query, parameters)

