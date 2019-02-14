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

import asyncio
import datetime
import math
import time
import traceback
import sys
import discord
from discord.ext import commands


class Server(object):
    def __init__(self, name=None, address=None, server_url=None, service_api_key=None, service_id=None, server_icon=None,
                 info=None, players=None, kills=None, playtime=None, whitelist=None):
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


async def display_status(ctx, server: object):
    try:
        info = server.info
        if info['fpp_only']:
            game_mode = '1st Person'
        else:
            game_mode = '3rd Person'
        embed = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                              url=server.server_url,
                              description=server.address,
                              timestamp=datetime.datetime.now().astimezone())
        embed.set_author(name='Server Details', url=server.server_url,
                         icon_url=server.server_icon)
        embed.set_footer(text="Report Generated", icon_url=server.server_icon)
        embed.add_field(name="Status", value=info['state'].capitalize())
        embed.add_field(name="DayZ Version", value=info['version'])
        embed.add_field(name="Connected Players",
                        value=str(info['current_players']) + '/' + str(info['max_players']))
        embed.add_field(name="In-Game Time", value=info['gametime'])
        embed.add_field(name="Time Acceleration", value=info['time_acceleration'])
        embed.add_field(name="Server FPS", value=info['health']['game']['fps'])
        embed.add_field(name="Game Mode", value=game_mode)
        embed.add_field(name="Map", value=info['map'])
        embed.add_field(name="Hive", value=info['hive'])
        await ctx.send(embed=embed)
    except KeyError as error:
        if error.args[0] == 'health':
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            embed1.add_field(name="Server Did Not Respond, May Be Down", value='\u200b')
            embed1.set_footer(text='Server Error', icon_url=server.server_icon)
            await ctx.send(embed=embed1)


async def display_tech(ctx, server: object):
    try:
        info = server.info
        if info['health']['system']['application'] == 'om':
            server_manager = 'Omega Manager'
        else:
            server_manager = 'CFOmegaSC'
        uptime_secs = time.time() - int(info['health']['system']['boot_time'])
        uptime = await convert_time(uptime_secs)
        embed = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                              url=server.server_url,
                              description=server.address,
                              timestamp=datetime.datetime.now().astimezone())
        embed.set_author(name='Server Technical Details', url=server.server_url,
                         icon_url=server.server_icon)
        embed.set_footer(text="Report Generated", icon_url=server.server_icon)
        embed.add_field(name="DayZ CPU Usage", value=str(info['health']['process']['cpu_usage']) + '%')
        embed.add_field(name="DayZ MEM Usage", value=str(info['health']['process']['memory_usage']) + 'MB')
        embed.add_field(name="Uptime", value=uptime)
        embed.add_field(name="Total CPU Usage", value=str(info['health']['system']['cpu_usage']) + '%')
        embed.add_field(name="Total MEM Usage", value=str(info['health']['system']['memory']['used']) + 'MB')
        embed.add_field(name="CPU Cores", value=info['health']['system']['cpu_count'])
        embed.add_field(name="Application", value=server_manager)
        embed.add_field(name="Version", value=info['health']['system']['version'])
        embed.add_field(name='Node', value=info['node'])
        await ctx.send(embed=embed)
    except KeyError as error:
        if error.args[0] == 'health':
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            embed1.add_field(name="Server Did Not Respond, May Be Down", value='\u200b')
            embed1.set_footer(text='Server Error', icon_url=server.server_icon)
            await ctx.send(embed=embed1)


async def convert_time(time):
    seconds = round(time)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    converted_time = "{:02d}h : {:02d}m : {:02d}s".format(hours, minutes, seconds)
    return converted_time


async def display_mods(ctx, server):
    try:
        info = server.info
        mod_list = []
        output_mods = ''
        for mod in server.info['health']['game'].get('mods', []):
            mod_string = '[{}](https://steamcommunity.com/sharedfiles/filedetails/?id={})\n'.format(
                (str(mod['directory'])[1:22]).ljust(22, '\u200b'), (str(mod['file_id'])))
            mod_list.append(mod_string)
        count = 0
        if len(mod_list) == 0:
            output_mods = "\u200b"
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Server Mod Information', url=server.server_url,
                              icon_url=server.server_icon)
            embed1.set_footer(
                text='{} Mods'.format(len(mod_list)),
                icon_url=server.server_icon)
            embed1.add_field(name="Vanilla Server: No Mods Installed", value=output_mods)
            await ctx.send(embed=embed1)
            await asyncio.sleep(1)
        if len(mod_list) < 10 and len(mod_list) != 0:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            for mod in mod_list:
                output_mods += mod
                count += 1
                if count == 5:
                    embed1.add_field(name='\u200b', value=output_mods, inline=True)
                    output_mods = ''
                    count = 0
            embed1.add_field(name='\u200b', value=output_mods, inline=True)
            embed1.set_footer(
                text='{} Mods'.format(len(mod_list)),
                icon_url=server.server_icon)
            await ctx.send(embed=embed1)
            await asyncio.sleep(1)
        if 10 < len(mod_list) <= 20:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            for mod in mod_list:
                output_mods += mod
                count += 1
                if count == 5:
                    embed1.add_field(name='\u200b', value=output_mods, inline=True)
                    output_mods = ''
                    count = 0
            if len(output_mods) != 0:
                embed1.add_field(name='\u200b', value=output_mods, inline=True)
            embed1.set_footer(
                text='{} Mods'.format(len(mod_list)),
                icon_url=server.server_icon)
            await ctx.send(embed=embed1)
            await asyncio.sleep(1)
        if 20 > len(mod_list) >= 40:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address)
            embed1.set_author(name='Server Mod Information', url=server.server_url,
                              icon_url=server.server_icon)
            embed2 = discord.Embed(colour=discord.Colour(0x3D85C6),
                                   timestamp=datetime.datetime.now().astimezone())
            embed2.set_footer(
                text='{} Mods'.format(len(mod_list)),
                icon_url=server.server_icon)
            for mod in mod_list[:20]:
                output_mods += mod
                count += 1
                if count == 5:
                    embed1.add_field(name='\u200b', value=output_mods)
                    output_mods = ''
                    count = 0
            output_mods = ''
            count = 0
            for mod in mod_list[20:]:
                output_mods += mod
                count += 1
                if count == 10:
                    embed2.add_field(name='\u200b', value=output_mods)
                    output_mods = ''
                    count = 0
            if len(output_mods) != 0:
                embed2.add_field(name='\u200b', value=output_mods)
            embed1.add_field(name='\u200b', value='\u200b')
            embed2.add_field(name='\u200b', value='\u200b')
            await ctx.send(embed=embed1)
            await ctx.send(embed=embed2)
    except KeyError as error:
        if error.args[0] == 'health':
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            embed1.add_field(name="Server Did Not Respond, May Be Down", value='\u200b')
            embed1.set_footer(text='Server Error', icon_url=server.server_icon)
            await ctx.send(embed=embed1)


async def display_players(ctx, server):
    try:
        info = server.info
        player_listing = ' '
        count = 1
        player_list = []
        for player in server.players.get('players', []):
            player_string = '[{}](https://omegax.cftools.de/user/{})\n'.format(
                player['info']['name'][:22].ljust(22, '\u200b'), player['cftools_id'])
            player_list.append(player_string)
            count += 1
        count = 0
        if len(player_list) is 0:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Players Online', url=server.server_url,
                              icon_url=server.server_icon)
            embed1.set_footer(text='{}/{} Players Online'.format(info['current_players'], info['max_players']),
                              icon_url=server.server_icon)
            embed1.add_field(name="No Players Online", value='\u200b')
            await ctx.send(embed=embed1)
            await asyncio.sleep(1)
        if len(player_list) < 10 and len(player_list) != 0:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Players Online', url=server.server_url,
                              icon_url=server.server_icon)
            embed1.set_footer(text='{}/{} Players Online'.format(info['current_players'], info['max_players']),
                              icon_url=server.server_icon)
            for player in player_list:
                player_listing += str(player)
            embed1.add_field(name="Players", value=player_listing, inline=True)
            await ctx.send(embed=embed1)
            await asyncio.sleep(1)
        if 10 < len(player_list) <= 60:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Players Online', url=server.server_url,
                              icon_url=server.server_icon)
            embed1.set_footer(text='{}/{} Players Online'.format(info['current_players'], info['max_players']),
                              icon_url=server.server_icon)
            for player in player_list:
                player_listing += player
                count += 1
                if count == 10:
                    embed1.add_field(name='\u200b', value=player_listing, inline=True)
                    player_listing = ''
                    count = 0
            embed1.add_field(name='\u200b', value=player_listing, inline=True)
            embed1.set_footer(text='{}/{} Players Online'.format(info['current_players'], info['max_players']),
                              icon_url=server.server_icon)
            await ctx.send(embed=embed1)
            await asyncio.sleep(1)
        if len(player_list) > 60:
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address)
            embed1.set_author(name='Players Online', url=server.server_url,
                              icon_url=server.server_icon)
            embed2 = discord.Embed(colour=discord.Colour(0x3D85C6), timestamp=datetime.datetime.now().astimezone())
            embed2.set_footer(text='{}/{} Players Online'.format(info['current_players'], info['max_players']),
                              icon_url=server.server_icon)
            for player in player_list[:60]:
                player_listing += str(player)
                count += 1
                if count == 10:
                    embed1.add_field(name='\u200b', value=player_listing)
                    player_listing = ''
                    count = 0
            player_listing = ''
            count = 0
            for player in player_list[60:]:
                player_listing += str(player)
                count += 1
                if count == 10:
                    embed2.add_field(name='\u200b', value=player_listing)
                    player_listing = ''
                    count = 0
            if len(player_listing) != 0:
                embed2.add_field(name='\u200b', value=player_listing)
            embed1.add_field(name='\u200b', value='\u200b')
            embed2.add_field(name='\u200b', value='\u200b')
            embed2.set_footer(text='{}/{} Players Online'.format(info['current_players'], info['max_players']),
                              icon_url=server.server_icon)
            await ctx.send(embed=embed1)
            await ctx.send(embed=embed2)
    except KeyError as error:
        if error.args[0] == 'health':
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            embed1.add_field(name="Server Did Not Respond, May Be Down", value='\u200b')
            embed1.set_footer(text='Server Error', icon_url=server.server_icon)
            await ctx.send(embed=embed1)

async def display_kills(ctx, limit: int, server: object):
    try:
        upper_limit = limit
        info = server.info
        kills = server.kills
        kills_list = []
        count_kills = []
        count_deaths = []
        count = 0
        kills_list.clear()
        count_deaths.clear()
        count_kills.clear()
        top_kd_ratio = 0
        top_kd_string = ""
        top_killer = ""
        for user in kills.get('users', []):
            if int(user['deaths']) != 0:
                kd_ratio = round(int(user['kills']) / int(user['deaths']), 2)
            else:
                kd_ratio = round(int(user['kills']) + .00, 3)
            if top_kd_ratio < kd_ratio:
                top_kd_ratio = kd_ratio
                top_kd_string = '[{}](https://omegax.cftools.de/user/{}) with {}!'.format(
                    user['latest_name'], user['cftools_id'], kd_ratio)
            if user['rank'] == 1:
                top_killer = '[{}](https://omegax.cftools.de/user/{}) with {} kills!'.format(
                    user['latest_name'], user['cftools_id'], user['kills'])
            kill_name = '{} [{}](https://omegax.cftools.de/user/{})'.format(str(user['rank']).rjust(2, '0'),
                                                                            user['latest_name'][:15].ljust(
                                                                                15, ' '),
                                                                            user['cftools_id']) + '\n'
            kills = '{}'.format(str(user['kills'])) + '\n'
            deaths = '{}'.format(str(user['deaths'])) + '\n'
            count_kills.append(kills)
            count_deaths.append(deaths)
            kills_list.append(kill_name)
            count += 1
        if top_kd_string == "":
            top_killer = ''
            top_kd_string = ''
        embed_kills = discord.Embed(title=info['servername'][:57], colour=discord.Colour(0x3D85C6),
                                    url=server.server_url,
                                    description='\nTop Killer: {}\nTop K/D: {}'.format(top_killer,
                                                                                       top_kd_string),
                                    timestamp=datetime.datetime.now().astimezone())
        embed_kills.set_author(name='Server Leaderboard', url=server.server_url,
                               icon_url=server.server_icon)
        embed_kills.set_footer(text="Report Generated",
                               icon_url=server.server_icon)
        lower = 0
        upper = 10
        player_string = ""
        kills_string = ""
        deaths_string = ""
        if upper_limit < upper:
            upper = upper_limit
        if len(kills_list) < upper_limit:
            upper_limit = len(kills_list)
        tier = 1
        parsed = 0
        while upper <= upper_limit:
            for player in kills_list[lower:upper]:
                player_string += player
            for kills in count_kills[lower:upper]:
                kills_string += kills
            for deaths in count_deaths[lower:upper]:
                deaths_string += deaths
            embed_kills.add_field(name='Tier {}'.format(tier), value=(player_string.ljust(20, '\u200b')),
                                  inline=True)
            embed_kills.add_field(name='Kills'.format(tier),
                                  value='{}'.format(kills_string.rjust(4, '\u200b')), inline=True)
            embed_kills.add_field(name='Deaths'.format(tier),
                                  value='{}'.format(deaths_string.rjust(4, '\u200b')), inline=True)
            player_string = ""
            kills_string = ""
            deaths_string = ""
            lower += 10
            upper += 10
            tier += 1
            parsed += 10
        if parsed < upper_limit:
            for player in kills_list[parsed:upper_limit]:
                player_string += player
            for kills in count_kills[parsed:upper_limit]:
                kills_string += kills
            for deaths in count_deaths[parsed:upper_limit]:
                deaths_string += deaths
            embed_kills.add_field(name='Tier {}'.format(tier), value=(player_string.ljust(20, '\u200b')),
                                  inline=True)
            embed_kills.add_field(name='Kills'.format(tier),
                                  value='{}'.format(kills_string.rjust(4, '\u200b')), inline=True)
            embed_kills.add_field(name='Deaths'.format(tier),
                                  value='{}'.format(deaths_string.rjust(4, '\u200b')), inline=True)
        await ctx.send(embed=embed_kills)
    except KeyError as error:
        if error.args[0] == 'health':
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            embed1.add_field(name="Server Did Not Respond, May Be Down", value='\u200b')
            embed1.set_footer(text='Server Error', icon_url=server.server_icon)
            await ctx.send(embed=embed1)

async def display_played(ctx, limit, server):
    try:
        upper_limit = limit
        info = server.info
        playtime = server.playtime
        time_list = []
        name_list = []
        count = 0
        name_list.clear()
        time_list.clear()
        top_played = ""
        for user in playtime.get('users', []):
            if user['rank'] == 1:
                top_played = '[{}](https://omegax.cftools.de/user/{}) with {}!'.format(
                    user['latest_name'], user['cftools_id'], await convert_time(user['playtime']))
            played_name = '{} [{}](https://omegax.cftools.de/user/{})'.format(
                str(user['rank']).rjust(2, '0'), user['latest_name'][:15].ljust(15, ' '),
                user['cftools_id']) + '\n'
            played_time = '{}'.format(str(await convert_time(user['playtime']))) + '\n'
            time_list.append(played_time)
            name_list.append(played_name)
            count += 1
        embed_played = discord.Embed(title=info['servername'][:57], colour=discord.Colour(0x3D85C6),
                                     url=server.server_url,
                                     description='\nMost Played: {}'.format(top_played),
                                     timestamp=datetime.datetime.now().astimezone())
        embed_played.set_author(name='Server Leaderboard', url=server.server_url,
                                icon_url=server.server_icon)
        embed_played.set_footer(text="Report Generated",
                                icon_url=server.server_icon)
        lower = 0
        upper = 10
        played_name = ""
        played_time = ""
        if upper_limit < upper:
            upper = upper_limit
        if len(name_list) < upper_limit:
            upper_limit = len(name_list)
        tier = 1
        parsed = 0
        while upper <= upper_limit:
            for player in name_list[lower:upper]:
                played_name += player
            for time in time_list[lower:upper]:
                played_time += time
            embed_played.add_field(name='Tier {}'.format(tier), value=(played_name.ljust(20, '\u200b')),
                                   inline=True)
            embed_played.add_field(name='Played For'.format(tier),
                                   value='{}'.format(played_time.rjust(4, '\u200b')), inline=True)
            embed_played.add_field(name='\u200b', value='\u200b', inline=True)
            played_name = ""
            played_time = ""
            lower += 10
            upper += 10
            tier += 1
            parsed += 10
        if parsed < upper_limit:
            for player in name_list[parsed:upper_limit]:
                played_name += player
            for time in time_list[parsed:upper_limit]:
                played_time += time
            embed_played.add_field(name='Tier {}'.format(tier), value=(played_name.ljust(20, '\u200b')),
                                   inline=True)
            embed_played.add_field(name='Played For'.format(tier),
                                   value='{}'.format(played_time.rjust(4, '\u200b')), inline=True)
            embed_played.add_field(name='\u200b', value='\u200b', inline=True)
        await ctx.send(embed=embed_played)
    except KeyError as error:
        if error.args[0] == 'health':
            embed1 = discord.Embed(title=info['servername'], colour=discord.Colour(0x3D85C6),
                                   url=server.server_url,
                                   description=server.address,
                                   timestamp=datetime.datetime.now().astimezone())
            embed1.set_author(name='Mod Information', url=server.server_icon,
                              icon_url=server.server_icon)
            embed1.add_field(name="Server Did Not Respond, May Be Down", value='\u200b')
            embed1.set_footer(text='Server Error', icon_url=server.server_icon)
            await ctx.send(embed=embed1)

# CommandErrorHandler
# Copyright © 2018 EvieePy (https://github.com/EvieePy) Licensed under the MIT License
# Copyright © 2018, 2019 James M. Ivey <james@binaryalkemist.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, including without
# limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

class CommandErrorHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        # if command has local error handler, return
        if hasattr(ctx.command, 'on_error'):
            return

        # get the original exception
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send('This command has been disabled.')
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('This command is missing an argument.')
            return

        if isinstance(error, commands.UserInputError):
            await ctx.send("Invalid input.")
            await self.send_command_help(ctx)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
            return

        if isinstance(error, KeyError):
            await ctx.send("Key Error: " + str(error) + " Not Found")
            return

        # ignore all other exception types, but print them to stderr
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

