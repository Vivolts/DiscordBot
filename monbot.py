
import os  # Importer le module os pour accéder aux variables d'environnement
import discord
from mcstatus import JavaServer
import asyncio
import datetime


TOKEN = os.environ.get('TOKEN')
# Remplace par l'IP et le port de ton serveur Minecraft.
MINECRAFT_SERVER_IP = "91.197.6.221:25579"

# ID de ton utilisateur pour que le bot t'envoie des messages privés
USER_ID = 123456789012345678  # Remplace par ton propre ID utilisateur Discord

# Crée une instance du bot Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Variables pour suivre l'état précédent des joueurs connectés et leur heure de connexion
previous_players = set()
player_connect_times = {}

# Fonction pour vérifier le statut du serveur Minecraft
async def check_minecraft_server():
    global previous_players, player_connect_times  # Utiliser les variables globales pour suivre l'état précédent et les temps de connexion
    try:
        # Connexion au serveur Minecraft
        server = JavaServer.lookup(MINECRAFT_SERVER_IP)
        status = server.status()  # Obtenir le statut du serveur
        
        current_players = set()  # Créer un ensemble pour les joueurs actuellement connectés

        if status.players.online > 0:
            # Obtenir les pseudos des joueurs connectés
            if status.players.sample:
                current_players = set(player.name for player in status.players.sample)
                print(f"Joueurs connectés : {', '.join(current_players)}")  # Afficher les joueurs connectés
            else:
                current_players = set()  # Aucune information sur les pseudos
        else:
            current_players = set()  # Aucun joueur connecté

        # Comparer l'état actuel avec l'état précédent
        if current_players != previous_players:
            # Identifier les joueurs qui se sont connectés et déconnectés
            new_players = current_players - previous_players
            disconnected_players = previous_players - current_players

            # Gérer les nouveaux joueurs connectés
            for player in new_players:
                player_connect_times[player] = datetime.datetime.now()  # Enregistrer l'heure de connexion du joueur
                await send_player_status(f"Un joueur s'est connecté : {player}")

            # Gérer les joueurs déconnectés
            for player in disconnected_players:
                if player in player_connect_times:
                    connect_time = player_connect_times[player]
                    disconnect_time = datetime.datetime.now()
                    play_duration = disconnect_time - connect_time
                    # Formater la durée pour l'afficher proprement (heures, minutes, secondes)
                    formatted_duration = str(play_duration).split('.')[0]  # On enlève les microsecondes
                    await send_player_status(f"Un joueur s'est déconnecté : {player} (Temps de jeu : {formatted_duration})")
                    del player_connect_times[player]  # Supprimer l'heure de connexion, le joueur est déconnecté

        # Mettre à jour l'état précédent
        previous_players = current_players

    except Exception as e:
        print(f"Erreur lors de la connexion au serveur Minecraft : {str(e)}")

# Fonction pour envoyer un message sur Discord (canal et message privé)
async def send_player_status(message):
    # Envoyer le message dans un canal spécifique
    channel = client.get_channel(1291720245417082986)  # ID du canal Discord
    if channel is None:
        print("Erreur : Impossible de trouver le canal Discord avec l'ID spécifié.")
    else:
        await channel.send(message)

    # Envoyer un message privé à l'utilisateur spécifié
    user = await client.fetch_user(USER_ID)  # Récupérer l'utilisateur par son ID
    if user is None:
        print("Erreur : Impossible de trouver l'utilisateur avec l'ID spécifié.")
    else:
        await user.send(message)

# Événement déclenché lorsque le bot est prêt et connecté à Discord
@client.event
async def on_ready():
    print(f'{client.user} est connecté à Discord!')
    
    # Envoyer un message de bienvenue ou d'état initial
    await send_player_status("Bot en ligne et vérifie le statut des joueurs.")

    while True:
        await check_minecraft_server()
        await asyncio.sleep(30)  # Attendre 30 secondes avant la prochaine vérification

# Lancer le bot
client.run(TOKEN)
