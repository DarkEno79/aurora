#  Copyright © 2018, 2019 James M. Ivey <james@binaryalkemist.net>
#  Portions Copyright © 2018 EvieePy (https://github.com/EvieePy) Licensed under the MIT License
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import tools
import asyncio
import json
import logging
import aiohttp
import datetime
import discord
from discord.ext import commands
import requests
import time
import requests_cache
requests_cache.install_cache('test_cache', backend='memory', expire_after=900, allowable_methods=('GET', 'POST'))


headers = {'contentType': 'application/x-www-form-urlencoded','User-Agent': 'CFTools ServiceAPI-Client'}

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='[%H:%M:%S]')
log = logging.getLogger()
log.setLevel(logging.INFO)

with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    token = config_data['discord_token']
    report_channel = config_data['report_channel']
    api_url = config_data['api_url']
    guild_id = config_data['guild_id']
    status_refresh = config_data['status_refresh']
    delayed_refresh = config_data['delayed_refresh']
    activity_rotate = config_data['activity_rotate']
    activity_refresh = config_data['activity_refresh']
    cooldown_channel = config_data['cooldown_channel']
    cooldown_user = config_data['cooldown_user']
    staff_role = tuple(config_data['permissions']['staff'])
    moderator_role = tuple(config_data['permissions']['moderators'])
    admin_role = tuple(config_data["permissions"]["admins"])

server_list = []

class Server(object):
    def __init__(self, name=None, address=None, server_url=None, service_api_key=None, service_id=None, server_icon=None, info=None, players=None, kills=None, playtime=None, whitelist=None):
        self.name = name
        self.address = address
        self.server_url = server_url
        self.service_api_key = service_api_key
        self.service_id = service_id
        self.server_icon = server_icon
        self.info = info
        self.players = players
        self.kills = kills
        self.playtime = playtime
        self.whitelist = whitelist


async def fetch_api(session, url, data):
    try:
        async with session.post(url, data=data, headers=headers) as response:
            api_data = await response.json()
            return api_data
    except Exception as error:
        log.info('API Fetch Failed: ' + str(error))


async def leaderboard_fetch_async():
    while True:
        tasks = []
        try:
            async with aiohttp.ClientSession() as session:
                for server in server_list:
                    tasks.append(fetch_api(session, "{}stats/{}".format(api_url, server.service_id),
                                           {'service_api_key': str(server.service_api_key), 'order': 'descending',
                                            'stat_type': 'kills'}))
                    tasks.append(fetch_api(session, "{}stats/{}".format(api_url, server.service_id),
                                           {'service_api_key': str(server.service_api_key), 'order': 'descending',
                                            'stat_type': 'playtime'}))
                results = await asyncio.gather(*tasks)
                sub_list = [results[n:n + 2] for n in range(0, len(results), 2)]
                index = 0
                for api_return in sub_list:
                    server = server_list[index]
                    server.kills = api_return[0]
                    server.playtime = api_return[1]
                    index += 1
            await session.close()
            log.info("Server(s) Leaderboard Updated")
        except Exception as error:
            log.info('API Fetch Failed:' + str(error))
        await asyncio.sleep(delayed_refresh)


async def status_fetch_async():
    while True:
        tasks = []
        try:
            async with aiohttp.ClientSession() as session:
                for server in server_list:
                    tasks.append(
                        fetch_api(session, "{}serverinfo/{}".format(api_url, server.service_id),
                                  {'service_api_key': str(server.service_api_key)}))
                    tasks.append(
                        fetch_api(session, "{}playerlist/{}".format(api_url, server.service_id),
                                  {'service_api_key': str(server.service_api_key)}))
                results = await asyncio.gather(*tasks)
                sub_list = [results[n:n + 2] for n in range(0, len(results), 2)]
                index = 0
                for api_return in sub_list:
                    server = server_list[index]
                    server.info = api_return[0]
                    server.players = api_return[1]
                    index += 1
            await session.close()
            log.info("Server(s) Status Updated")
            await asyncio.sleep(status_refresh)  # task runs every 60 seconds
        except Exception as error:
            log.info('API Fetch Failed:' + str(error))


async def whitelist_fetch_async():
    while True:
        tasks = []
        try:
            async with aiohttp.ClientSession() as session:
                for server in server_list:
                    tasks.append(fetch_api(session, "{}whitelist/list".format(api_url),
                                           {'service_id': str(server.service_id),
                                            'service_api_key': str(server.service_api_key)}))

                results = await asyncio.gather(*tasks)
                index = 0
                for result in results:
                    server = server_list[index]
                    server.whitelist = result
                    index += 1
                log.info("Server(s) Whitelist Updated")
                await asyncio.sleep(delayed_refresh)
            await session.close()
        except Exception as error:
            log.info('Fetch Error:' + str(error))


async def initialize_servers():
    server_list.clear()
    for server in config_data.get('server', []):
        update = Server()
        update.name = server['name']
        update.address = server['address']
        update.server_url = server['server_url']
        update.service_api_key = server['service_api_key']
        update.service_id = server['service_id']
        update.server_icon = server['server_icon']
        server_list.append(update)
        bot.loop.create_task(status_fetch_async())
        bot.loop.create_task(whitelist_fetch_async())
        bot.loop.create_task(leaderboard_fetch_async())



bot = commands.Bot(command_prefix='!', description='Aurora - The DayZ Discord Bot')
bot.add_cog(tools.CommandErrorHandler(bot))


@bot.event
async def on_ready():
    await initialize_servers()
    activity = discord.Game(name="!help for help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot_info = await bot.application_info()
    log.info("Aurora Discord Bot\nName: {}\nID: {}\nDescription: {}\nOwner: {}\nPublic: {}".format(bot_info.name,bot_info.id,bot_info.description,bot_info.owner,bot_info.bot_public))
    log.info("Bot Connected")
    await asyncio.sleep(10)
    bot.loop.create_task(rotate_activity())


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
@commands.has_any_role(*admin_role)
async def reload(ctx):
    """[ADMIN] Reloads Configuration File"""
    log.info("Configuration Reload Requested")
    await ctx.send("Configuration Reload Requested")
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
        token = config_data['discord_token']
        report_channel = config_data['report_channel']
        api_url = config_data['api_url']
        guild_id = config_data['guild_id']
        status_refresh = config_data['status_refresh']
        delayed_refresh = config_data['delayed_refresh']
        activity_rotate = config_data['activity_rotate']
        activity_refresh = config_data['activity_refresh']
        cooldown_channel = config_data['cooldown_channel']
        cooldown_user = config_data['cooldown_user']
        staff_role = tuple(config_data['permissions']['staff'])
        moderator_role = tuple(config_data['permissions']['moderators'])
        admin_role = tuple(config_data["permissions"]["admins"])
    try:
        await initialize_servers()
    except Exception as error:
        log.exception('Initialization Error:' + str(error))
    await ctx.send('Configuration Reload Complete')


async def rotate_activity():
    rotate_position = 0
    while activity_rotate is True:
        try:
            server = server_list[rotate_position]
            info = server.info
            if info['state'] == 'running':
                player_activity = '{}: {}/{} Online'.format(server.name, info['current_players'], info['max_players'])
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.online, activity=activity)
            elif info['state'] == 'starting':
                player_activity = '{}: Server Restarting'.format(server.name)
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.idle, activity=activity)
            elif info['state'] == 'idle':
                player_activity = '{}: Server Offline'.format(server.name)
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.do_not_disturb, activity=activity)
            if rotate_position == (int(len(server_list)) - 1):
                rotate_position = 0
                await asyncio.sleep(activity_refresh)
                player_activity = '!help for help'
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.online, activity=activity)
            else:
                rotate_position += 1
        except Exception as error:
            log.error('Error: ' + str(error))
            pass
        await asyncio.sleep(activity_refresh)


@bot.command()
@commands.cooldown(1, cooldown_user, commands.BucketType.user)
async def status(ctx, name: str):
    """Displays Server Status Information"""
    if name == 'all':
        for server in server_list:
            await tools.display_status(ctx, server)
            await asyncio.sleep(1)
    if name != 'all':
            found = False
            for server in server_list:
                if server.name == name:
                    found = True
                    await tools.display_status(ctx, server)
            if found == False:
                await ctx.send('Error: Server Not Found')


@bot.command()
@commands.has_any_role(*staff_role)
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def tech(ctx, name: str):
    """[STAFF] Displays Server Technical Details"""
    if name == 'all':
        for server in server_list:
            await tools.display_tech(ctx, server)
            await asyncio.sleep(1)
    if name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                await tools.display_tech(ctx, server)
        if found == False:
            await ctx.send('Server: ' + name + ' not found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def mods(ctx, name: str):
    """Server Mods List\n\nCommand Syntax: !mods <all> or <name>"""
    if name == 'all':
        for server in server_list:
            await tools.display_mods(ctx, server)
            await asyncio.sleep(1)
    if name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                await tools.display_mods(ctx, server)
        if found == False:
            await ctx.send('Server: ' + name + ' not found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def schedule(ctx, name: str):
    """Next Scheduled Event\n\nCommand Syntax: !schedule <all> or <shortname>"""
    if name in 'all':
        for server in server_list:
            info = server.info
            output = '```{}'.format(info['servername']).center(60, ' ') + '\n'
            output += 'Next server task is {} at {}```'.format(info['next_scheduled_task']['task']['action'],
                                                               info['next_scheduled_task']['task']['time'])
            await ctx.send(output)
    else:
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                info = server.info
                output = '```{}'.format(info['servername']).center(60, ' ') + '\n'
                output += 'Next server task is {} at {}```'.format(info['next_scheduled_task']['task'] \
                                                                       ['action'],
                                                                   info['next_scheduled_task']['task']['time'])
                await ctx.send(output)
        if not found:
            await ctx.send('Error: Server Not Found')


@bot.command()
@commands.has_any_role(*staff_role)
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def players(ctx, name: str):
    """[STAFF] Online Players List\n\nCommand Syntax: !players <all> or <shortname>"""
    if name == 'all':
        for server in server_list:
            await tools.display_players(ctx, server)
            await asyncio.sleep(1)
    elif name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                await tools.display_players(ctx, server)
        if found == False:
            await ctx.send('Error: Server Not Found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def list(ctx):
    """List Servers in Network\n\nCommand Syntax: !list"""
    embed = discord.Embed(colour=discord.Colour(0x3D85C6),
                          timestamp=datetime.datetime.now().astimezone())
    server_short = ''
    server_long = ''
    icon_url = ''
    for server in server_list:
        icon_url = server.server_icon
        name = server.name
        info = server.info
        server_short += name + '\n'
        server_long += str(info['servername'])[:40] + '\n'
    embed.set_author(name='Network List', icon_url=icon_url)
    embed.set_footer(text="Report Generated", icon_url=icon_url)
    embed.add_field(name="Name", value=server_short, inline=True)
    embed.add_field(name="Server", value=server_long, inline=True)
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, cooldown_user, commands.BucketType.user)
async def report(ctx, player: str, category: str, details: str, location: str, time: str):
    """Report Player to Admins\n\nSend via PM to Aurora\nCommand Syntax: !report \'<player>\' \'<type of incident>\' \'<details>\' \'<location>\' \'<time>\'"""
    output = '```'
    output += 'Player Abuse Report'.center(60, ' ') + '\n'
    output += 'Reporter: {}'.format(ctx.author).center(60, ' ') + '\n'
    output += 'Player: ' + player + '\n'
    output += 'Abuse: ' + category + '\n'
    output += 'Details: ' + details + '\n'
    output += 'Location: ' + location + '\n'
    output += 'Time: ' + time + '\n'
    output += '```'
    channel_id = int(report_channel)
    channel = bot.get_channel(channel_id)
    await channel.send(output)
    await ctx.author.send("Report has been submitted.")


@bot.command()
@commands.has_any_role(*admin_role)
async def broadcast(ctx, name: str, message: str):
    """ [ADMIN] Server Broadcast \n\nCommand Syntax: !broadcast <all> or <shortname> '<message>'"""
    if name == 'all':
        for server in server_list:
            service_api_key = server.service_api_key
            service_id = server.service_id
            data = {
                'service_api_key': '{}'.format(service_api_key),
                'message': '{}'.format(message)
            }
            url = "{}servermessage/{}".format(api_url, service_id)
            try:
                async with aiohttp.ClientSession() as session:
                    await fetch_api(session, url=url, data=data)
                    await ctx.send('Message Broadcast to Entire Network!')
                await session.close()
            except Exception as error:
                log.info('Broadcast Error:' + str(error))

    if name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                info = server.info
                found = True
                service_api_key = server.service_api_key
                service_id = server.service_id
                data = {
                    'service_api_key': '{}'.format(service_api_key),
                    'message': '{}'.format(message)
                }
                url = "{}servermessage/{}".format(api_url, service_id)
                try:
                    async with aiohttp.ClientSession() as session:
                        await fetch_api(session, url=url, data=data)
                        output = 'Message Broadcast to Server: ' + info['servername']
                        await ctx.send(output)
                    await session.close()
                except Exception as error:
                    log.exception('Broadcast Error: ' + str(error))
        if found == False:
            await ctx.send('Error: Server Not Found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def kills(ctx, name: str, limit: int):
    """ Kills Leaderboard \n\nCommand Syntax: !kills [all][server] [limit]"""
    if limit <= 50:
        if name == 'all':
            for server in server_list:
                await tools.display_kills(ctx, limit, server)
                await asyncio.sleep(1)
        if name != 'all':
            found = False
            for server in server_list:
                if server.name == name:
                    found = True
                    await tools.display_kills(ctx, limit, server)
            if found == False:
                await ctx.send('Server: ' + name + ' not found')
    if limit > 50:
        await ctx.send("Specified Limit Too High: 50 Max")


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def played(ctx, name: str, limit: int):
    """ Played Time Leaderboard \n\nCommand Syntax: !played [all][server] [limit]"""
    if limit <= 50:
        if name == 'all':
            for server in server_list:
                await tools.display_played(ctx, limit, server)
                await asyncio.sleep(1)
        if name != 'all':
            found = False
            for server in server_list:
                if server.name == name:
                    found = True
                    await tools.display_played(ctx, limit, server)
            if found == False:
                await ctx.send('Server: ' + name + ' not found')
    if limit > 50:
        await ctx.send("Specified Limit Too High: 50 Max")

@bot.command()
@commands.has_any_role(*moderator_role)
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def wl(ctx, name: str):
    """ [MODERATOR] Whitelist View\n\nSyntax: !wl <all> or <server>"""
    if name == 'all':
        for server in server_list:
            output = ""
            info = server.info
            embed = discord.Embed(title=info['servername'][:57], colour=discord.Colour(0x3D85C6),
                                  url=server.server_url,
                                  description=server.address,
                                  timestamp=datetime.datetime.now().astimezone())
            embed.set_author(name='Server Whitelist', url=server.server_url,
                             icon_url=server.server_icon)
            embed.set_footer(text="Report Generated",
                             icon_url=server.server_icon)

            count = 0
            for user in server.whitelist['data']:
                count += 1
                wl_player = await get_player(user['cftools_id'], server.service_id, server.service_api_key)
                print(wl_player)
                wl_sponsor = await get_player(user['issued_by'], server.service_id, server.service_api_key)
                print(wl_sponsor)
                output += '{}. [{}](https://omegax.cftools.de/user/{}) issued at {} by {}'.format(str(count).rjust(2), wl_player['data']['aliases'][0], user['cftools_id'], time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(user['issued_at'])), '[{}](https://omegax.cftools.de/user/{})'.format(wl_sponsor['data']['aliases'][0], user['issued_by']) + '\n')
            if len(output) == 0:
                embed.add_field(name='No Whitelist Entries', value='\u200b')
            else:
                embed.add_field(name='Whitelist Entries', value=output)
            await ctx.send(embed=embed)
            await asyncio.sleep(1)
    elif name != 'all':
        output = ""
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                info = server.info
                embed = discord.Embed(title=info['servername'][:57], colour=discord.Colour(0x3D85C6),
                                             url=server.server_url,
                                             description=server.address,
                                             timestamp=datetime.datetime.now().astimezone())
                embed.set_author(name='Server Whitelist', url=server.server_url,
                                        icon_url=server.server_icon)
                embed.set_footer(text="Report Generated",
                                        icon_url=server.server_icon)
                count = 0
                for user in server.whitelist['data']:
                    count += 1
                    wl_player = await get_player(user['cftools_id'], server.service_id, server.service_api_key)
                    wl_sponsor = await get_player(user['issued_by'], server.service_id, server.service_api_key)
                    output += '{}. [{}](https://omegax.cftools.de/user/{}) issued at {} by {}'.format(str(count).rjust(2), wl_player['data']['aliases'][0], user['cftools_id'], time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(user['issued_at'])),'[{}](https://omegax.cftools.de/user/{})'.format(wl_sponsor['data']['aliases'][0], user['issued_by']) + '\n')
                if len(output) != 0:
                    embed.add_field(name='Whitelist Entries', value=output)
                    await ctx.send(embed=embed)
                elif len(output) == 0:
                    embed.add_field(name='No Whitelist Entries', value='\u200b')
                    await ctx.send(embed=embed)
        if found == False:
            await ctx.send('Error: Server Not Found')


async def get_player(cftools_id: str, service_id: str, service_api_key: str):
    data = {
        'service_api_key': '{}'.format(service_api_key),
        'identity_type': 'cftools_id',
        'identity': '{}'.format(cftools_id)
    }
    r = requests.post('https://omegax.cftools.de/api/v1/playerinfo/{}'.format(service_id), headers=headers, data=data)
    print(r.from_cache)
    player_info = r.json()
    return player_info



bot.run(token)
