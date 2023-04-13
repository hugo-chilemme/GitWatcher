import requests

# Remplacez ces valeurs par votre nom d'utilisateur et votre mot de passe GitHub
username = "hugo.chilemme@gmail.com"
password = "votre_mot_de_passe"

# URL pour générer un token d'accès
url = "https://api.github.com/authorizations"

# Créez un objet auth avec vos informations d'identification
auth = (username, password)

# Données de la requête pour générer un token d'accès
data = {
    "scopes": [
        "repo",
        "user"
    ],
    "note": "Python script to get GitHub access token"
}

# Effectuez la requête POST pour générer le token d'accès
response = requests.post(url, auth=auth, json=data)

# Vérifiez que la requête a réussi
if response.status_code == 201:
    # Récupérez le token d'accès dans la réponse JSON
    token = response.json()["token"]
    print(f"Bearer token: {token}")
else:
    print("La requête a échoué.")
    print(response.json())
