import discord
from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix="!", help_command=None, intents=discord.Intents.all())
#Здесь можно поставить любой удобный для вас префик. Для меня например удобный (!) Изменять комнаду command_prefix="Нужный вам префикс"

@bot.event
async def on_ready():
    print("Bot was connected to the server")

    await bot.change_presence(status=discord.Status.online, activity=discord.Game("help")) # Изменяем статус боту


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    msg = message.content.lower()
    greeting_words = ["hello", "hi", "привет"]
    censored_words = ["дурак", "дура", "придурок"]

    if msg in greeting_words:
        await message.channel.send(f"{message.author.name}, Приветик!")

    # Filter censored words
    for bad_content in msg.split(" "):
        if bad_content in censored_words:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, Нельзя так!")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel() # Передайте ID канала
    role = discord.utils.get(member.guild.roles, id=) # Передайте ID роли

    await member.add_roles(role)


@bot.event
async def on_command_error(ctx, error):


    print(error)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author}, у вас недостаточно прав для выполнения данной команды!")
    elif isinstance(error, commands.UserInputError):
        await ctx.send(embed=discord.Embed(
            description=f"Правильное использование команды: `{ctx.prefix}{ctx.command.name}` ({ctx.command.brief})\nExample: {ctx.prefix}{ctx.command.usage}"
        ))


@bot.command(name="clear", brief="Очистить чат от сообщений, по умолчанию 15 сообщений", usage="clear <amount=10>")
async def clear(ctx, amount: int=15):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Was deleted {amount} messages...")



@bot.command(name="kick", brief="Выгнать пользователя с сервера", usage="kick <@user> <reason=None>")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.message.delete(delay=1) # Если желаете удалять сообщение после отправки с задержкой

    await member.send(f"You was kicked from server") # Отправить личное сообщение пользователю
    await ctx.send(f"Member {member.mention} was kicked from this server!")
    await member.kick(reason=reason)


@bot.command(name="ban", brief="Забанить пользователя на сервере", usage="ban <@user> <reason=None>")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.send(f"You was banned on server") # Отправить личное сообщение пользователю
    await ctx.send(f"Member {member.mention} was banned on this server")
    await member.ban(reason=reason)


@bot.command(name="unban", brief="Разбанить пользователя на сервере", usage="unban <user_id>")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)


@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="Help menu",
        description="Here you can find the necessary command"
    )
    commands_list = ["clear", "kick", "ban", "unban"]
    descriptions_for_commands = ["Clear chat", "Kick user", "Ban user", "Unban user"]

    for command_name, description_command in zip(commands_list, descriptions_for_commands):
        embed.add_field(
            name=command_name,
            value=description_command,
            inline=False # Будет выводиться в столбик, если True - в строчку
        )

    await ctx.send(embed=embed)

#У вас на сервере должна быть создана роль под названием mute
@bot.command(name="mute", brief="Запретить пользователю писать ", usage="mute <member>")
@commands.has_permissions(mute_members=True)
async def mute_user(ctx, member: discord.Member):
    mute_role = discord.utils.get(ctx.message.guild.roles, name="mute")

    await member.add_roles(mute_role)
    await ctx.send(f"{ctx.author} gave role mute to {member}")



@bot.command(name="join", brief="Подключение к голосовому каналу", usage="join")
async def join_to_channel(ctx):
    global voice
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f"Bot was connected to the voice channel")


@bot.command(name="leave", brief="Отключение от голосового канала", usage="leave")
async def leave_from_channel(ctx):
    global voice
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.disconnect()
        await ctx.send(f"Bot was connected to the voice channel")

#Здесь обязательно нужно в файл token.txt кинуть токен бота 
token = open ('token.txt', 'r').readline()

bot.run( token )
