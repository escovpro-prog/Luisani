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
    if not interaction.guild:
        embed = discord.Embed(
            title="⚠️ No Disponible en DM",
            description="Este comando solo funciona en servidores de Discord, no en mensajes directos.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not hasattr(interaction.channel, 'name') or not hasattr(interaction.channel, 'category'):
        embed = discord.Embed(
            title="⚠️ Canal No Soportado",
            description="Este comando solo funciona en canales de texto normales.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    canal_nombre = interaction.channel.name.lower()
    categoria_nombre = interaction.channel.category.name.lower() if interaction.channel.category else ""
    
    if canal_nombre != CANAL_PERMITIDO or categoria_nombre != CATEGORIA_PERMITIDA:
        embed = discord.Embed(
            title="⚠️ Canal Incorrecto",
            description=f"Este comando solo funciona en el canal **#{CANAL_PERMITIDO}** dentro de la categoría **{CATEGORIA_PERMITIDA.title()}**.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres Luisani-ia, un asistente útil que siempre responde en español de forma clara y amigable."},
                {"role": "user", "content": pregunta}
            ],
            stream=False
        )
        
        respuesta_texto = respuesta.choices[0].message.content
        
        if len(respuesta_texto) > 4000:
            respuesta_texto = respuesta_texto[:3997] + "..."
        
        embed = discord.Embed(
            title="💡 Respuesta de Luisani-ia",
            description=respuesta_texto,
            color=discord.Color.green()
        )
        embed.set_footer(
            text=f"Pregunta de {interaction.user.display_name}", 
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Hubo un problema al procesar tu pregunta. Por favor, inténtalo de nuevo.",
            color=discord.Color.red()
        )
        try:
            await interaction.followup.send(embed=error_embed)
        except:
            pass
        print(f"Error al procesar pregunta: {e}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError):
        embed = discord.Embed(
            title="❌ Error",
            description="Ocurrió un error al ejecutar el comando. Por favor, inténtalo de nuevo.",
            color=discord.Color.red()
        )
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            pass
    print(f"Error en comando: {error}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERROR: No se encontró DISCORD_TOKEN en las variables de entorno")
        exit(1)
    
    if not GROQ_API_KEY:
        print("❌ ERROR: No se encontró GROQ_API_KEY en las variables de entorno")
        exit(1)
    
    print("🚀 Iniciando bot Luisani-ia en Railway...")
    print("⚡ Usando Groq API - Sin servidor Flask")
    bot.run(DISCORD_TOKEN)