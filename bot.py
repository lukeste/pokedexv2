import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

test_guild_id = 246877047488512000
marin_guild_id = 330217404669886465


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.command()
async def r(ctx):
    """role request"""
    if ctx.guild.id != test_guild_id and ctx.guild.id != marin_guild_id:
        return
    split_message = ctx.message.content[3:].split(',')
    if split_message:  # check if any roles were requested
        requested_roles = validate_roles(ctx.guild, split_message)
        if requested_roles:
            try:
                await ctx.author.add_roles(*requested_roles)
                success_msg = f'Successfully added {len(requested_roles)} role'
                if (len(requested_roles)) > 1:
                    success_msg += 's'
                await ctx.send(success_msg)
            except discord.Forbidden:
                await ctx.send('I don\'t have permission to add roles')
            except discord.HTTPException:
                await ctx.send('Something went wrong')
                print(f'HTTPException in r\nrequested_roles: {requested_roles}')


@bot.command()
async def remove(ctx):
    """role removal"""
    if ctx.guild.id != test_guild_id and ctx.guild.id != marin_guild_id:
        return
    role_list = ctx.message.content[8:].lower().split(',')
    remove_list = validate_roles(ctx.guild, role_list)
    if remove_list:
        try:
            await ctx.author.remove_roles(*remove_list)
            success_msg = f'Successfully removed {len(remove_list)} role'
            if len(remove_list) > 1:
                success_msg += 's'
            await ctx.send(success_msg)
        except discord.Forbidden:
            await ctx.send('I don\'t have permission to remove roles')
        except discord.HTTPException:
            await ctx.send('Something went wrong')
            print(f'HTTPException in remove\nremove_list: {remove_list}')


@bot.command()
async def addrole(ctx):
    if ctx.guild.id != test_guild_id and ctx.guild.id != marin_guild_id:
        return
    role = ctx.message.content[8:].strip()
    if role:
        # check if role doesn't exist
        if discord.utils.get(ctx.guild.roles, name=role) is None:
            await ctx.send('No existing role found. Creating role...')
            try:
                await ctx.guild.create_role(name=role,
                                            reason=f'Created by '
                                                   f'{ctx.author.name}')
                await ctx.send(f'Successfully created `{role}` role')
            except discord.Forbidden:
                await ctx.send('I don\'t have permission to create roles')
            except discord.HTTPException:
                await ctx.send('Something went wrong')
                print(f'HTTPException in addrole\nrole: {role}')
            except discord.InvalidArgument:
                await ctx.send('Something went wrong')
                print('InvalidArgument in addrole')

        # add role to role file
        with open('roles.txt', 'a+') as f:
            roles = f.read().splitlines()
            if role in roles:
                await ctx.send(f'Bot already knows `{role}` role')
            else:
                f.write(f'\n{role}')
                await ctx.send(f'Successfully added `{role}` to the bot')


def validate_roles(guild, roles):
    with open('roles.txt', 'r') as f:
        valid_roles = f.read().splitlines()
    roles_list = []
    for role in roles:
        role = role.lower().strip()
        if is_int(role):
            role = f'lvl{role}'
        elif role.startswith('level'):
            role = f'lvl{role[5:].strip()}'
        elif role.startswith('lvl '):
            role = f'lvl{role[4:]}'
        for valid_role in valid_roles:
            if role == valid_role.lower():
                role = discord.utils.get(guild.roles, name=valid_role)
                roles_list.append(role)
    return roles_list


def is_int(s: str):
    """helper function. checks if s is a number."""
    try:
        int(s)
        return True
    except ValueError:
        return False


with open('key.txt', 'r') as keyfile:
    key = keyfile.read()

bot.run(key)
