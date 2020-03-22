import yaml
import schedule
import time
from sso import SSO
from esi import ESI
from status import Printer
from discordhooker import Hooker
from cacheout import Cache
from apiqueue import ApiQueue
from bot import DiscordNotifier
import tokens as tokens
cache = Cache(ttl=4600)


notification_options = {'whitelist': [
    'StructureUnderAttack',
    'StructureFuelAlert',
    'StructureLostShields',
    'StructureLostArmor',
    'AllWarDeclaredMsg',
    'WarDeclared',
    'AllWarInvalidatedMsg',
    'WarRetractedByConcord',

]}
discord = {
    'personal': {
        'token': tokens.discord_token,
        'channel_id': tokens.discord_id
    }
}
sso_app = {
    'client_id': tokens.sso_id,
    'secret_key': tokens.sso_key
}

eve_apis = {
    'Frosty': {
        'character_name': tokens.char1_name,
        'character_id': tokens.char1_id,
        'refresh_token': tokens.char1_token
    },
    'Dev': {
        'character_name': tokens.char2_name,
        'character_id': tokens.char2_id,
        'refresh_token': tokens.char2_token
    },
}


def asso():
    return SSO(
        sso_app['client_id'],
        sso_app['secret_key'],
        eve_apis['Dev']['refresh_token'],
        eve_apis['Dev']['character_id']
    )


def api_to_sso(api):
    return SSO(
        sso_app['client_id'],
        sso_app['secret_key'],
        api['refresh_token'],
        api['character_id']
    )


aq = ApiQueue(list(map(api_to_sso, eve_apis.values())))


def noti(notifications):
    if notification_options['whitelist']:
        notifications = [notification for notification in notifications if notification['type']
                         in notification_options['whitelist']]
    return notifications


def getfrosty(data):
    stru = ['StructureUnderAttack',
            'StructureLostShields', 'StructureLostArmor']
    k = ''
    for i in range(0, len(data)):
        if data[i]['type'] in stru and data[i]['notification_id'] not in cache:
            k = k + (Printer(ESI(asso())).transform(data[i]))
            d = str(data[i]['notification_id'])
            cache.set(data[i]['notification_id'], k)
            k = k + '\n'
    if k != '':
        DiscordNotifier(tokens.channel_1).notify("@here " + k)
        DiscordNotifier(tokens.channel_2).notify("@here " + k)
        print(time.strftime(" %d:%m:%y %H:%M:%S", time.gmtime()) +"Structure notification id: " + d)
    else:
        print(time.strftime(" %d:%m:%y %H:%M:%S", time.gmtime())+" Structure no hit")
        return ""


def getleadership(data):
    stru = ['StructureFuelAlert']
    k = ''
    for i in range(0, len(data)):
        if data[i]['type'] in stru and data[i]['notification_id'] not in cache:
            k = k + (Printer(ESI(asso())).transform(data[i]))
            d = str(data[i]['notification_id'])
            cache.set(data[i]['notification_id'], k)
            k = k + '\n'
    if k != '':
        DiscordNotifier(tokens.channel_1).notify("@here " + k)
        print(time.strftime(" %d:%m:%y %H:%M:%S", time.gmtime()) +"Fuel notification id: " + d)
    else:
        print(time.strftime(" %d:%m:%y %H:%M:%S", time.gmtime())+" Fuel no hit")
        return ""


def getwar(data):
    stru = ['AllWarDeclaredMsg', 'AllWarInvalidatedMsg',
            'WarDeclared', 'WarRetractedByConcord']
    k = ''
    for i in range(0, len(data)):
        if data[i]['type'] in stru and data[i]['notification_id'] not in cache:
            k = k + (Printer(ESI(asso())).transform(data[i]))
            d = str(data[i]['notification_id'])
            cache.set(data[i]['notification_id'], k)
            k = k + '\n'
    if k != '':
        DiscordNotifier(tokens.channel_4).notify("@here " + k)
        DiscordNotifier(tokens.channel_3).notify("War notification" + k)
        print(time.strftime(" %d:%m:%y %H:%M:%S", time.gmtime()) +"War notification id: " + d)
    else:
        print(time.strftime(" %d:%m:%y %H:%M:%S", time.gmtime())+" war no hit")
        return ""


def pingping(data):
    getwar(data)
    getfrosty(data)
    getleadership(data)


def silly():
    pingping(noti(ESI(aq.get()).get_new_notifications()))


schedule.every(5).minutes.do(silly)
silly()
while True:
    schedule.run_pending()
    time.sleep(1)
