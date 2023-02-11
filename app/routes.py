from flask import Flask, request, redirect, url_for, render_template, flash, session, jsonify
import os
from datetime import datetime
import datetime
import requests
import json
from app import app, db, discord
from app.models import *
from sqlalchemy import cast, or_
from flask_discord_interactions import DiscordInteractions, Member, Channel, Role, Permission, Message

@app.before_first_request
def register_commands():
    print("registering commands!")
    discord.update_commands(guild_id=os.environ.get("GUILD_ID"))

def getSnowflakeTimestamp(snowflake):
    DiscordEpoch = 1420070400000
    input = int(snowflake)
    UnixTSinMS = input / 4194304 + DiscordEpoch
    out = str(datetime.fromtimestamp(UnixTSinMS/1000.0))
    return out

# role configs. 
key_roles = [625108953126141964, 693117420365414500, 600483209242869771, 662345018727727113, 993823229221281802, 948030402075983962, 625174339020652564, 652983677852188672, 600483629772308501, 758886007792730142]
is_member = [625108953126141964, 693117420365414500, 600483209242869771, 662345018727727113, 993823229221281802, 948030402075983962, 625174339020652564, 652983677852188672, 600483629772308501]
is_staff = [625108953126141964, 693117420365414500, 600483209242869771, 662345018727727113]
is_admin = [625108953126141964, 693117420365414500, 600483209242869771]

# role demote/promote list | Veteran, Recruit, -_-
roles_whitelist = [625174339020652564,652983677852188672,600483629772308501]
approval_roles = [652983677852188672,600483629772308501]
promotion_roles = [625174339020652564,600483629772308501]
self_roles = [983129148761464834,983129194659725353,983129229698932786,654993971180994580,983128577207844874,688869645125681254,654993557496528909,983128723932983356,983128802995609640,654993343494881300,654993254315589663,654993609317285898,654993296363356173,654993672613527563,983128452037230683,654993191321206787,654993739260887050,654993501716742144,654994022334595072,670016391633567762,670016282120290307,670016335606054922,670016444293054514,762784599071129630,983125892408680489,983126153197912134,983125787010015312,983125598601875498,983125705179148309,652982868070367252,653101820151070750,719083825283596330,983430183056965672,984491045947580447,604317785400672312,983125473955545140,983126482488532992]
role_veteran = 625174339020652564
role_recruit = 652983677852188672


@app.route('/')
def index():
    return jsonify({"message": "Hello!"})

@app.route('/sync', methods=['GET'])
def sync():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth == os.environ.get('CURL_PASS'):    
        # request roles from discord
        url = 'https://discordapp.com/api/guilds/{}/roles'.format(os.environ.get('GUILD_ID'))
        x = requests.get(url, headers={'Authorization': 'Bot {}'.format(os.environ.get('BOT_TOKEN'))}) 
        from_discord = json.loads(x.content)
        #keep only necessary fields 
        filtered_data = [{k: v for k, v in d.items() if k in {'id', 'name', 'color', 'position'}} for d in from_discord]
        #clear all previous roles
        db.session.query(User).update({User.key_role: None}, synchronize_session=False)
        db.session.query(roles_ref).delete()
        db.session.delete(Role)
        #bulk insert roles
        db.session.bulk_insert_mappings(Role, filtered_data)
        db.session.commit()
        #request member list from discord
        url = 'https://discordapp.com/api/guilds/{}/members?limit=1000'.format(os.environ.get('GUILD_ID'))
        x = requests.get(url, headers={'Authorization': 'Bot {}'.format(os.environ.get('BOT_TOKEN'))}) 
        from_discord = json.loads(x.content)
        #iterate the list
        for x in from_discord:
            x['id'] = int(x['user']['id'])
            # convert x['roles'] to int list
            x['roles'] = [int(val) for val in x['roles'][0:]]
            x['joined'] = datetime.fromisoformat(x['joined_at'])
            x['created'] = datetime.fromisoformat(getSnowflakeTimestamp(x['user']['id']))
            x['is_member'] = True
            #set nick or username
            if x['nick'] is None: 
                x['name'] = x['user']['username']
            else: 
                x['name'] = x['nick']
            # set avatar or guild avatar
            if x['avatar'] is None:
                x['avatar'] = x['user']['avatar']
            else:
                x['avatar'] = x['avatar']
            # check if the user is guest (no role, but in discord)
            if any(i in is_member for i in x['roles']):
                x['is_approved'] = True
            else: 
                x['is_approved'] = False
            # get highest role
            if any(i in key_roles for i in x['roles']):
                x['key_role'] = next(item for item in key_roles if item in x['roles'])
            else: 
                x['key_role'] = None
            #check if member is part of staff
            if any(i in is_staff for i in x['roles']):
                x['is_staff'] = True
            else: 
                x['is_staff'] = False
            #check if member is part of admin
            if any(i in is_admin for i in x['roles']):
                x['is_admin'] = True
            else: 
                x['is_admin'] = False
            #list roles
            x['discord_roles'] = []
            for y in x['roles']:
                x['discord_roles'].append(int(y))
            
            #remove unwanted fields
            del x['deaf']
            del x['mute']
            del x['flags']
            del x['nick']
            del x['user']
            del x['pending']
            del x['is_pending']
            del x['joined_at']
            del x['communication_disabled_until']
            del x['premium_since']
            del x['roles']

        # delete some columns to ensure previous members updated
        db.session.query(User).update({'avatar': None, 'key_role': None, 'is_approved': None, 'is_staff': None, 'is_admin': None, 'is_member': None})

        # bulk update members
        entries_to_update = []
        entries_to_insert = []

        # create new dict based on list from discord
        new_dict = {}
        for item in from_discord:
            new_dict[item['id']] = item

        # create a new dict for many2many role table
        roles_dict = {}
        for item in from_discord:
            roles_dict[item['id']] = item
    
        # get all entries to be updated
        for each in db.session.query(User).filter(getattr(User, 'id').in_(new_dict.keys())).all():
            # pop users needs an update
            entry = new_dict.pop(int(getattr(each, 'id')))
            # finalize list and save
            entries_to_update.append(entry)

        # get all entries to be inserted. ps: updated users popped from the new_dict dict
        for entry in new_dict.values():      
            # finalize list and save
            entries_to_insert.append(entry)
            #add roles for the new users
            
        # update db
        db.session.bulk_insert_mappings(User, entries_to_insert)
        db.session.bulk_update_mappings(User, entries_to_update)
        
        # delete many2many role relations
        # db.session.query(roles_ref).delete()

        # create many2many role relation based on roles_dict dic
        for each in db.session.query(User).filter(getattr(User, 'id').in_(roles_dict.keys())).all():
            # get freshly added and updated user list from roles_dict
            entry = roles_dict.get(int(getattr(each, 'id')))
            roles = Role.query.filter(Role.id.in_(entry['discord_roles'])).all()
            each.discord_roles.extend(roles)
        
        #save everything
        db.session.commit()
        print(datetime.now(), ' - ', 'Database updated')
        return jsonify({"message": "OK: Authorized"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


@discord.command()
def info(ctx, user: str = None):
    print(f'{ctx.author} used {user}')
    if ctx.channel_id == '1020065348445274283':
        q = user
        if q is not None:
            results = (User.query
            .outerjoin(User.characters)
            .filter(or_(Character.name.ilike(f'%{q}%'), User.name.ilike(f'%{q}%'), cast(User.id, db.String).ilike(f'%{q}%')))
            .all())
            if results is not None:
            # if results is greater than 1
                if len(results) > 1:
                    return Message(
                    embed={
                        "title": ctx.author.display_name,
                        "description": "Avatar Info",
                        "fields": [
                            {"name": "Member Since", "value": ctx.author.joined_at},
                            {
                                "name": "Username",
                                "value": (
                                    f"**{ctx.author.username}**" f"#{ctx.author.discriminator}"
                                ),
                            },
                            {"name": "User ID", "value": ctx.author.id},
                            {"name": "Channel ID", "value": ctx.channel_id},
                            {"name": "Guild ID", "value": ctx.guild_id},
                        ],
                        "image": {"url": ctx.author.avatar_url},
                    }
                )
            # multiple results
                else:
                    return results
            # no result found
            else:
                return Message(
                    content="No results found. Try /info anal",
                    ephemeral=True,
                )
        return Message(
                    content='Query not provided.',
                    ephemeral=True,
                )
    else:
        return Message(
            content="You are not allowed to use this command here.",
            ephemeral=True,
        )
    

discord.set_route("/interactions")


