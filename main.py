import discord
from discord import app_commands
import os
from openai import OpenAI

# Configuración
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Validar variables
if not DISCORD_TOKEN:
    print("❌ ERROR: DISCORD_TOKEN no encontrado")
    exit(1)

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY no encontrado")
    exit(1)

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
    print('📋 Sincronizando comandos...')
    
    try:
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            print(f'✅ Comandos en: {guild.name}')
    except Exception as e:
        print(f'⚠️ Error sincronizando: {e}')
    
    await bot.change_presence(activity=discord.Game(name="Usa /ia [pregunta]"))
    print('🚀 Bot listo en Render!')

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
        
        # Manejo seguro del avatar
        try:
            if interaction.user.avatar:
                embed.set_footer(
                    text=f"Pregunta de {interaction.user.display_name}", 
                    icon_url=interaction.user.avatar.url
                )
            else:
                embed.set_footer(text=f"Pregunta de {interaction.user.display_name}")
        except:
            embed.set_footer(text=f"Pregunta de {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description="Hubo un problema al procesar tu pregunta. Por favor, inténtalo de nuevo.",
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

# 🔥 ESTA LÍNEA DEBE ESTAR AL FINAL Y SIN INDENTACIÓN
if __name__ == "__main__":
    print("🚀 Iniciando Luisani-ia en Render...")
    bot.run(DISCORD_TOKEN)