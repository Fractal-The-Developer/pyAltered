from urllib import request, parse
import json
import sqlite3
import sys, getopt

short_options = "hscm"
long_options = ["scrape=","cube=","auth=","locale="]

AlteredAPI = {
    'endpoint': "https://api.altered.gg",
    'headers': {'User-Agent': 'pyAltered/0.0.1', 'Connection': 'keep-alive', 'Accept': '*/*'},
    'parameters': '',
    'httpRequest': '',
    'response': '',
    'bearerToken': '',
    'locale': 'en-us',
    'collection_flag': False,
    'scrape_flag': False,
    'card_sets': ("COREKS","CORE","ALIZE"),
    'factions': ("AX","BR","YZ","OR","MU","LY"),
    'rarities': ("COMMON","RARE","UNIQUE"),
    'card_types': ("TOKEN_MANA","HERO","CHARACTER","TOKEN","PERMANENT","SPELL","LANDMARK_PERMANENT","EXPEDITION_PERMANENT"),
    'card_subtypes': ("ADVENTURER", "ANIMAL", "APPRENTICE", "ARTIST", "BOON", "BUREAUCRAT", "CITIZEN", "COMPANION", "CONJURATION", "DEITY", "DISRUPTION", "DRAGON", "DRUID", "ELEMENTAL", "ENGINEER", "FAIRY","GEAR","LANDMARK","LEVIATHAN","MAGE","MANEUVER","MESSENGER","NOBLE","PLANT","ROBOT","SCHOLAR","SOLDIER","SONG","SPIRIT","TITAN","TRAINER"),
    'keywords': ("RESUPPLY","SEASONED","BOOSTED","BRASSBUG","SABOTAGE","BOODA","ORDIS_RECRUIT","GIGANTIC","TOUGH_1","TOUGH_2","TOUGH_X","DEFENDER","ETERNAL","AFTER_YOU","MAW","ANCHORED","FLEETING","ASLEEP")
}

dbName = "pyAltered.db"
   
def main(argv):
    card_value_min = 0
    card_value_max = 10
    
    prepare_database()
    
    try:
        opts, args = getopt.getopt(argv,short_options,long_options)
    except getopt.GetoptError as err:
        print (str(err))
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('usage: pyAltered.py [-h]')
            print('       pyAltered.py --authtoken     [Bearer Token]')
            print('       pyAltered.py --scrape        run in API scrape mode')
            print('       pyAltered.py --collection    flag to scrape only cards you own')
            print('       pyAltered.py --locale        [IETF language tag] e.g. en-US')            
            print('')
            print('Options and arguments:')
            print('-h               : print this help message and exit')
            sys.exit(2)
        elif opt in ("-l", "--locale"):
            AlteredAPI['locale'] = arg
        elif opt in ("-c", "--cube"):
            sys.exit(2)
        elif opt in ("-s", "--scrape"):
            AlteredAPI['scrape_flag'] = True
    
    if AlteredAPI['scrape_flag'] == True:
        for card_set in AlteredAPI['card_sets']:
            web_request_send(f"{AlteredAPI['endpoint']}/cards?&cardSet[]={card_set}&locale={AlteredAPI['locale']}")
            build_card_list()            
    print("Complete!")


def prepare_database():
    with sqlite3.connect(dbName) as dbFile:
        db = dbFile.cursor()
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS cards (
                    api_id TEXT PRIMARY KEY NOT NULL,
                    reference TEXT NOT NULL,
                    name TEXT NOT NULL,
                    faction TEXT NOT NULL,
                    card_type TEXT NOT NULL,
                    card_set TEXT NOT NULL,
                    rarity INTEGER NOT NULL,
                    image TEXT NOT NULL,
                    qr_details TEXT NOT NULL,
                    main_cost INTEGER NOT NULL,
                    reserve_cost INTEGER NOT NULL,
                    mountain_power INTEGER NOT NULL,
                    ocean_power INTEGER NOT NULL,
                    forest_power INTEGER NOT NULL,
                    suspended INTEGER NOT NULL,
                    cardEffects TEXT,
                    cardRulings TEXT NOT NULL
                )
            ''')
            db.execute('''
                CREATE TABLE IF NOT EXISTS rulings (
                    ruling_id TEXT PRIMARY KEY NOT NULL,
                    format TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            ''')
            dbFile.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        

def add_cards(cards):
    preparedCards = []
    for card in cards:
        preparedCards.append(
            {
                'id': card['id'],
                'reference': card['reference'],
                'name': card['name'],
                'faction': card['mainFaction']['name'],
                'cardType': card['cardType']['name'],
                'cardSet': card['cardSet']['name'],
                'rarity': card['rarity']['name'],
                'image': card['imagePath'],
                'details': card['qrUrlDetail'],
                'mainCost': card['elements']['MAIN_COST'],
                'recallCost': card['elements']['RECALL_COST'],
                'mountainPower': card['elements']['MOUNTAIN_POWER'],
                'oceanPower': card['elements']['OCEAN_POWER'],
                'forestPower': card['elements']['FOREST_POWER'],
                'isSuspended': int(card['isSuspended']),
                'cardEffects': card['cardEffects'],
                'cardRulings': card['cardRulings']
            }
        )
        
    with sqlite3.connect(dbName) as dbFile:
        db = dbFile.cursor()
        db.execute('BEGIN TRANSACTION')
        sql = '''INSERT OR REPLACE INTO cards (
                api_id,
                reference,
                name,
                faction,
                card_type,
                card_set,
                rarity,
                image,
                qr_details,
                main_cost,
                reserve_cost,
                mountain_power,
                ocean_power,
                forest_power,
                suspended,
                cardEffects,
                cardRulings
            )
            VALUES (:id, 
            :name,
            :reference,
            :faction, 
            :cardType, 
            :cardSet, 
            :rarity, 
            :image, 
            :details, 
            :mainCost, 
            :recallCost, 
            :mountainPower, 
            :oceanPower, 
            :forestPower, 
            :isSuspended,
            :cardEffects,
            :cardRulings)'''
        db.executemany(sql,preparedCards)
        dbFile.commit()
        
def add_rulings(cardRulings):
    preparedRulings = []
    rule_string = []
    
    for rule in cardRulings:
        preparedRulings.append(
            {
                'ruling_id': rule['@id'],
                'format': rule['eventFormat'],
                'created_at': rule['createdAt'],
                'question': rule['question'],
                'answer': rule['answer']
            }
        )
        rule_string.append(rule['@id'])
    
    with sqlite3.connect(dbName) as dbFile:
        db = dbFile.cursor()
        db.execute('BEGIN TRANSACTION')
        sql = '''INSERT OR REPLACE INTO rulings (ruling_id,format,created_at,question,answer)
            VALUES (:ruling_id,:format,:created_at,:question,:answer)'''
        db.executemany(sql,preparedRulings)
        dbFile.commit()
    
    rule_string = ",".join(rule_string)
    return rule_string

def build_card_list():
    extractedCards = AlteredAPI['response']['hydra:member']
    pages = AlteredAPI['response']['hydra:view']
        
    if pages['@id'] != pages['hydra:last']:
        previous_parameters = AlteredAPI['parameters']
        previous_response = AlteredAPI['response']
        for card in extractedCards:
            current_response = web_request_send(f"{AlteredAPI['endpoint']}/cards/{card['reference']}?locale={AlteredAPI['locale']}")           
            card['cardRulings'] = add_rulings(current_response['cardRulings'])
            if 'MAIN_EFFECT' in current_response['elements']:
                card['cardEffects'] = current_response['elements']['MAIN_EFFECT']
            else:
                card['cardEffects'] = ''
        
        
        #AlteredAPI['parameters'] = previous_parameters
        AlteredAPI['response'] = previous_response               
        add_cards(extractedCards)
        AlteredAPI['parameters'] = pages['hydra:next']
        web_request_send(f"{AlteredAPI['endpoint']}{AlteredAPI['parameters']}&locale={AlteredAPI['locale']}")
        build_card_list()
        
        
def web_request_send(uri):
    AlteredAPI['httpRequest'] = request.Request(uri,headers=AlteredAPI['headers'])
    if AlteredAPI['bearerToken'] != "":
        AlteredAPI['httpRequest'].add_header("Authorization", f"Bearer {AlteredAPI['bearerToken']}")
        
    print(f"Scanning... {uri}")
    response = request.urlopen(AlteredAPI['httpRequest'])
    json_response = json.loads(response.read())
    AlteredAPI['response'] = json_response
    return json_response


if __name__ == "__main__":   
    main(sys.argv[1:])
