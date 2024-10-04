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

# Fonction pour vérifier le statut du serveur Minecraft
async def check_minecraft_server():
    try:
        # Connexion au serveur Minecraft
        server = JavaServer.lookup(MINECRAFT_SERVER_IP)
        status = server.status()  # Obtenir le statut du serveur

        if status.players.online > 0:
            # Obtenir les pseudos des joueurs connectés
            if status.players.sample:
                players_list = ', '.join([player.name for player in status.players.sample])
                message = f"Il y a {status.players.online} joueur(s) en ligne : {players_list}"
            else:
                message = f"Il y a {status.players.online} joueur(s) en ligne, mais impossible d'obtenir les pseudos."
        else:
            # Si personne n'est connecté, on ne renvoie rien
            message = None

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
        if status_message and len(status_message.strip()) > 0:
            await channel.send(status_message)

        await asyncio.sleep(30)

# Lancer le bot
client.run(TOKEN)
