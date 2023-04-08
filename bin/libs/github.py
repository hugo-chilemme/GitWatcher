#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import hashlib
from bin.libs.database import execute

def get_commits(users=[], searchterm=""):

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
    return commits


def get_last_commit_repository(userId, repository):
    
    # URL formation
    repo_url = f"https://github.com/{userId}/{repository}/commits"

    # Sending the request
    r = requests.get(repo_url)

    # Status check : 200 = SUCCESS
    if r.status_code == 200:
        
        # Conversion of string to html parse
        soup = BeautifulSoup(r.content, 'html.parser')

        # Retrieving the latest commits from the repository
        commits = soup.find_all(class_='js-navigation-open')
        
        # Retrieving the title of the first commits
        title = commits[4].contents[0]
        
        # Returning the title commit
        return title


def save_commit(commit):   
    execute("INSERT INTO commits(ID, USER_ID, REPOSITORY, TITLE, DATETIME) VALUES(%s, %s, %s, %s, %s)", 
        (commit['ID'], commit['USER_ID'], commit['REPOSITORY'], commit['TITLE'], commit['DATETIME'], ))
