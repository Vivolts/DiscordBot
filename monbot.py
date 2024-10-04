import os  # Importer le module os pour accéder aux variables d'environnement
import discord
from mcstatus import JavaServer
import asyncio

# Récupérer le token du bot depuis une variable d'environnement
TOKEN = os.environ.get('TOKEN')

# Remplace par l'IP et le port de ton serveur Minecraft.
MINECRAFT_SERVER_IP = "91.197.6.221:25579"

# Crée une instance du bot Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Variable pour suivre les joueurs précédemment connectés
previous_players = set()  # Utiliser un ensemble pour stocker les pseudos des joueurs

# Fonction pour vérifier le statut du serveur Minecraft
async def check_minecraft_server():
    global previous_players  # Indiquer que nous voulons utiliser la variable globale

    try:
        # Connexion au serveur Minecraft
        server = JavaServer.lookup(MINECRAFT_SERVER_IP)
        status = server.status()  # Obtenir le statut du serveur

        current_players = {player.name for player in status.players.sample} if status.players.sample else set()
        
        # Vérifier les nouveaux joueurs connectés
        new_players = current_players - previous_players
        # Vérifier les joueurs déconnectés
        disconnected_players = previous_players - current_players
        
        message = None
        
        if new_players:
            message = f"Nouveau(x) joueur(s) connecté(s) : {', '.join(new_players)}"
        
        if disconnected_players:
            message = f"Déconnexion de : {', '.join(disconnected_players)}"

        # Mettre à jour la liste des joueurs précédemment connectés
        previous_players = current_players
        
        return message

    except Exception as e:
        return f"Erreur lors de la connexion au serveur Minecraft : {str(e)}"

# Événement déclenché lorsque le bot est prêt et connecté à Discord
@client.event
async def on_ready():
    print(f'{client.user} est connecté à Discord!')

    channel = client.get_channel(1291720245417082986)  # Remplace par l'ID du canal Discord
    if channel is None:
        print("Erreur : Impossible de trouver le canal Discord avec l'ID spécifié.")
        return
    
    while True:
        status_message = await check_minecraft_server()
        if status_message:
            await channel.send(status_message)

        await asyncio.sleep(30)

# Lancer le bot
client.run(TOKEN)
