import discord
from discord import app_commands
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

CANAL_PERMITIDO = "luisani-ia"
CATEGORIA_PERMITIDA = "general"

intents = discord.Intents.default()
intents.message_content = True

class LuisaniBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

bot = LuisaniBot()

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📋 Nombre: {bot.user.name}')
    print(f'🆔 ID: {bot.user.id}')
    print('━' * 50)
    
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            print(f'✅ Comandos sincronizados en: {guild.name}')
        except Exception as e:
            print(f'⚠️  Error sincronizando en {guild.name}: {e}')
    
    await bot.change_presence(activity=discord.Game(name="Usa /ia [pregunta]"))
    print('━' * 50)
    print('✅ Bot listo para usar')

@bot.tree.command(name="ia", description="Hazle una pregunta a Luisani-ia")
@app_commands.describe(pregunta="Tu pregunta para la IA")
async def ia_command(interaction: discord.Interaction, pregunta: str):
    # ... [mantén todo tu código igual aquí]
    # Tu código actual está perfecto

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERROR: No se encontró DISCORD_TOKEN")
        exit(1)
    
    if not GROQ_API_KEY:
        print("❌ ERROR: No se encontró GROQ_API_KEY")
        exit(1)
    
    print("🚀 Iniciando bot Luisani-ia en Render...")
    bot.run(DISCORD_TOKEN)