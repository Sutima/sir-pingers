import requests
import yaml
import time
import datetime
import calendar
import string
curtime = time.time()

class Printer(object):
    def __init__(self, eve):
        self.eve = eve
    def transform(self, notification):
        text = self.get_notification_text(notification)
        timestamp = self.timestamp_to_date(notification['timestamp'])

        return '[%s] %s' % (timestamp, text)
    def get_notification_text(self, notification):
        types = {
            'AllWarDeclaredMsg': self.corporation_war_declared,
            'WarDeclared': self.corporation_war_declared,
            'StructureUnderAttack': self.citadel_attacked,
            'StructureFuelAlert': self.citadel_low_fuel,
            'StructureLostShields': self.citadel_lost_shields,
            'StructureLostArmor': self.citadel_lost_armor,
            'AllWarInvalidatedMsg': self.corporation_war_invalidated,
            'WarRetractedByConcord': self.corporation_war_invalidated,

        }
        if notification['type'] in types:
            text = yaml.load(notification['text'])
            text['notification_timestamp'] = notification['timestamp']
            return types[notification['type']](text)

        return 'Unknown notification type for printing'
    def corporation_war_declared(self, notification):
        tstamp = notification['notification_timestamp']
        time_msg = self.war_start(tstamp)
        # May contain corporation or alliance IDs
        try:
            against_corp = self.get_corporation(notification['againstID'])
        except:
            against_corp = self.get_alliance(notification['againstID'])
        try:
            declared_by_corp = self.get_corporation(notification['declaredByID'])
        except:
            declared_by_corp = self.get_alliance(notification['declaredByID'])

        return 'War has been declared to %s by %s. %s' % (against_corp, declared_by_corp, time_msg)
    def corporation_war_invalidated(self, notification):
        tstamp = notification['notification_timestamp']
        time_msg = self.war_over(tstamp)
        # May contain corporation or alliance IDs
        try:
            against_corp = self.get_corporation(notification['againstID'])
        except:
            against_corp = self.get_alliance(notification['againstID'])
        try:
            declared_by_corp = self.get_corporation(notification['declaredByID'])
        except:
            declared_by_corp = self.get_alliance(notification['declaredByID'])

        return 'War has been invalidated to %s by %s. %s' % (against_corp, declared_by_corp, time_msg)

    def citadel_low_fuel(self, notification):
        citadel_type = self.get_item(notification['structureShowInfoData'][1])
        system = self.get_system(notification['solarsystemID'])
        citadel_name = self.get_structure_name(notification['structureID'])

        return "Citadel (%s, \"%s\") low fuel alert in %s" % (
            citadel_type,
            citadel_name,
            system)


    def citadel_lost_shields(self, notification):
        citadel_type = self.get_item(notification['structureShowInfoData'][1])
        system = self.get_system(notification['solarsystemID'])
        citadel_name = self.get_structure_name(notification['structureID'])
        timestamp = self.eve_duration_to_date(notification['notification_timestamp'], notification['timeLeft'])

        return "Citadel (%s, \"%s\") lost shields in %s (comes out of reinforce on \"%s\")" % (
            citadel_type,
            citadel_name,
            system,
            timestamp)

    def citadel_lost_armor(self, notification):
        citadel_type = self.get_item(notification['structureShowInfoData'][1])
        system = self.get_system(notification['solarsystemID'])
        citadel_name = self.get_structure_name(notification['structureID'])
        timestamp = self.eve_duration_to_date(notification['notification_timestamp'], notification['timeLeft'])

        return "Citadel (%s, \"%s\") lost armor in %s (comes out of reinforce on \"%s\")" % (
            citadel_type,
            citadel_name,
            system,
            timestamp)

    def citadel_attacked(self, notification):
        citadel_type = self.get_item(notification['structureShowInfoData'][1])
        system = self.get_system(notification['solarsystemID'])
        citadel_name = self.get_structure_name(notification['structureID'])
        zk = self.get_zk(notification['charID'])


        return "Citadel (%s, \"%s\") attacked (%.1f%% shield, %.1f%% armor, %.1f%% hull) in %s, by %s  %s." % (
            citadel_type,
            citadel_name,
            notification['shieldPercentage'],
            notification['armorPercentage'],
            notification['hullPercentage'],
            system,
            zk,
            notification['corpName'])


    def evetimeto(timestamp):
        return time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")


    def citname(self, id):
        id=str(id)
        if id in cache:
            return (cache.get(id))
        else:
            return ("Could not find name")
    def get_structure_name(self, structure_id):
        structure = self.eve.get_structure(structure_id)
        if 'name' in structure:
            return structure['name']
        else:
            return "Unknown name"

    def war_start(self, timestamp):
        timeh=datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime('%s')
        timesec=int(timeh)+86400
        timeprint=time.localtime(int(timeh)+86400)
        nowh=time.strftime('%Y-%m-%d %H:%M:%S', timeprint)
        link="http://time.nakamura-labs.com/#"
        msg= "The war will start %s Eve time, to convert to your local time head here %s%s IF you want more info on wardecs and how they affect you, read these links <https://support.eveonline.com/hc/en-us/articles/115004152745-Wars> <https://wiki.eveuniversity.org/Wartime_Operations_in_EVE_University>  " % (nowh, link,timesec)
        return msg

    def war_over(self, timestamp):
        timeh=datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime('%s')
        timesec=int(timeh)+86400
        timeprint=time.localtime(int(timeh)+86400)
        nowh=time.strftime('%Y-%m-%d %H:%M:%S', timeprint)
        link="http://time.nakamura-labs.com/#"
        msg= "The war will end %s Eve time, to convert to your local time head here %s%s Remeber to stay safe.. " % (nowh, link,timesec)
        return msg

    def evetotimestamp(timestamp):
        return calendar.timegm(evetimeto(timestamp))

    def timestamp_to_date(self, timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')

    def eve_timestamp_to_date(self, microseconds):
        """
        Convert microsoft epoch to unix epoch
        Based on: http://www.wiki.eve-id.net/APIv2_Char_NotificationTexts_XML
        """

        seconds = microseconds / 10000000 - 11644473600
        return datetime.datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

    def eve_duration_to_date(self, timestamp, microseconds):
        """
        Convert microsoft epoch to unix epoch
        Based on: http://www.wiki.eve-id.net/APIv2_Char_NotificationTexts_XML
        """

        seconds = microseconds / 10000000
        timedelta = datetime.datetime.strptime(
            timestamp, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(seconds=seconds)
        return timedelta.strftime('%Y-%m-%d %H:%M:%S')
    def get_zk(self,id):
        try:
            h = self.get_corporation(id)
            ch="/corporation/"
        except:
            ""
        try:
            h = self.get_alliance(id)
            ch="/alliance/"

        except:
            ""
        try:
            h = self.get_character(id)
            ch="/character/"
        except:
            ""
        return "https://zkillboard.com"+ch+str(id)

    def get_item(self, item_id):
        item = self.eve.get_item(item_id)
        return item['name']


    def get_system(self, system_id):
        system = self.eve.get_system(system_id)
        return system['name']

    def get_character(self, charID):
        char = self.eve.get_character(charID)
        return char['name']

    def get_corporation(self, corpID):
        corp = self.eve.get_corporation(corpID)
        return corp['name']

    def get_alliance(self, allianceID):
        alliance = self.eve.get_alliance(allianceID)
        return alliance['name']
