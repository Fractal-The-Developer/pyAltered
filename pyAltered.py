from urllib import request, parse
import json
import sqlite3
import sys, getopt

short_options = ":h"
long_options = ["cardsets=", 
"factions=", 
"rarities=", 
"cardtype=", 
"cardsubtype=", 
"handcost=", 
"reservecost=", 
"forestpower=", 
"mountainpower=", 
"oceanpower=", 
"keyword=", 
"foiled", 
"altart", 
"exclusive=", 
"suspended=",
"collection",
"authtoken",
"locale=",
"scrape",
"cube"]

AlteredAPI = {
    'endpoint': "https://api.altered.gg",
    'headers': {'User-Agent': 'pyAltered/0.0.1', 'Connection': 'keep-alive', 'Accept': '*/*'},
    'parameters': '',
    'httpRequest': '',
    'response': '',
    'bearerToken': '',
    'locale': 'en-us',
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
    scrape_flag = False
    
    prepare_database()
    
    try:
        arguments, values = getopt.getopt(argv,short_options,long_options)
    except getopt.GetoptError as err:
        print (str(err))
        sys.exit(2)
    
    if "-h" in arguments:
    print('usage: pyAltered.py [-h]')
    print('       pyAltered.py --authtoken     [Bearer Token]')
    print('       pyAltered.py --scrape        run in API scrape mode')
    print('       pyAltered.py --collection    flag to scrape only cards you own')
    print('       pyAltered.py --exclusive     [bool] flag to toggle exclusive cards in search')
    print('       pyAltered.py --cardsets      [name] comma delimited. e.g. CORE,COREKS,ALIZE')
    print('       pyAltered.py --rarities      [rarity] comma delimited. e.g. COMMON,RARE,UNIQUE')
    print('       pyAltered.py --cardtype      [type] comma delimited. e.g. HERO,SPELL,TOKEN,PERMANENT')
    print('       pyAltered.py --cardsubtype   [subtype] comma delimited. e.g. BUREAUCRAT,GEAR,DEITY')
    print('       pyAltered.py --handcost      [0-10]')
    print('       pyAltered.py --reserve_cost  [0-10]')
    print('       pyAltered.py --forestpower   [0-10]')
    print('       pyAltered.py --mountainpower [0-10]')
    print('       pyAltered.py --oceanpower    [0-10]')        
    print('       pyAltered.py --keyword       [keyword] comma delimited e.g. RESUPPLY,TOUGH_2,ANCHORED')
    print('       pyAltered.py --foiled        flag to include foiled cards')
    print('       pyAltered.py --altart        flag to include alternate art cards')
    print('       pyAltered.py --suspended     flag to include suspended cards')
    print('       pyAltered.py --locale        [IETF language tag] e.g. en-US')            
    print('')
    print('Options and arguments:')
    print('-h               : print this help message and exit')
    sys.exit(2)
    
    if "-scrape" in arguments:
        scrape_flag = True
    
    for option, values in arguments:
        if values == "":
            print(f"Option {option} is empty. Option {option} will be ignored.")
            continue
        else if len(arguments) > 1:
            delimited_value = values.upper().split(",")

        if scrape_flag == True:
            if option == "--authtoken":
                AlteredAPI['bearerToken'] = values
                
            if option == '--foiled':
                web_request_add_params_scrape("foiled=true")
                
            if option == '--altart':
                web_request_add_params_scrape("altArt=true")
                
            if option == "--suspended":
                web_request_add_params_scrape(f"isSuspended[]={result}")
                
            if option == "--exclusive":
                web_request_add_params_scrape(f"isExclusive[]={result}")
                
            if option == "--locale":
                AlteredAPI['locale'] = values
                web_request_add_params_scrape(f"locale[]={result}") 
                
            if option == "--cardsets":
                result = compare_to_api_table(delimited_value, AlteredAPI['card_sets'])
                if result != None:
                    web_request_add_params_scrape(f"cardSet[]={result}")
                    
            if option == "--factions":
                result = compare_to_api_table(delimited_value, AlteredAPI['factions'])
                if result != None:
                    web_request_add_params_scrape(f"factions[]={result}")
                    
            if option == "--rarities":
                result = compare_to_api_table(delimited_value, AlteredAPI['rarities'])
                if result != None:
                    web_request_add_params_scrape(f"rarity[]={result}")
                   
            if option == "--cardtype":
                result = compare_to_api_table(delimited_value, AlteredAPI['card_types'])
                if result != None:
                    web_request_add_params_scrape(f"cardType[]={result}")  
                    
            if option == "--cardsubtype":
                result = compare_to_api_table(delimited_value, AlteredAPI['card_subtypes'])
                if result != None:
                    web_request_add_params_scrape(f"cardSubType[]={result}")

            if option == "--keyword":
                result = compare_to_api_table(delimited_value, AlteredAPI['keywords'])
                if result != None:
                    web_request_add_params_scrape(f"keyword[]={result}")

            if option = "--collection":
                web_request_add_params_scrape("collection=true") 
                    
            if option == "--handcost":
                if value_in_range(values.int(),card_value_min,card_value_max):
                    web_request_add_params_scrape(f"mainCost[]={result}")     
                    
            if option == "--reservecost":
                if value_in_range(values.int(),card_value_min,card_value_max):
                    web_request_add_params_scrape(f"recallCost[]={result}")

            if option == "--forestpower":
                if value_in_range(values.int(),card_value_min,card_value_max):
                    web_request_add_params_scrape(f"forestPower[]={result}")   
                    
            if option == "--mountainpower":
                if value_in_range(values.int(),card_value_min,card_value_max):
                    web_request_add_params_scrape(f"mountainPower[]={result}") 
                    
            if option == "--oceanpower":
                if value_in_range(values.int(),card_value_min,card_value_max):
                    web_request_add_params_scrape(f"oceanPower[]={result}")
        
        
    web_request_add_headers()
    web_request_send()
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
            db.execute("CREATE UNIQUE INDEX cards_api_id ON cards(api_id)")
            db.execute('''
                CREATE TABLE IF NOT EXISTS rulings (
                    ruling_id TEXT PRIMARY KEY NOT NULL,
                    format TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            ''')
            db.execute("CREATE UNIQUE INDEX rulings_ruling_id ON ruling_id")
            dbFile.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        

def add_cards(cards):
    preparedCards = []
    for card in cards:
        #print(card['name'])
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
        sql = '''INSERT INTO cards (
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
            :cardRulings) ON CONFLICT(api_id) DO NOTHING'''
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
        sql = '''INSERT INTO rulings (
            ruling_id,
            format,
            created_at,
            question,
            answer
            )
            VALUES (:ruling_id,
            :format,
            :created_at,
            :question,
            :answer) ON CONFLICT(ruling_id) DO NOTHING'''
        db.executemany(sql,preparedRulings)
        dbFile.commit()
    
    rule_string = ",".join(rule_string)
    return rule_string

def build_card_list():
    extractedCards = AlteredAPI['response']['hydra:member']
    pages = AlteredAPI['response']['hydra:view']
    
    if pages['@id'] != pages['hydra:last']:
        web_request_add_params_cardeffect(extractedCards)
        add_cards(extractedCards)
        web_request_replace_params(pages['hydra:next'])
        web_request_add_headers()
        web_request_send()
        build_card_list()
        
def compare_to_api_table(value, table):
    for entry in table:
        if value == entry:
            return value
    return None
    
def value_in_range(value,min_range,max_range)
    return(min_range <= value <= max_range)
    
def web_request_add_params_scrape(param):
    if AlteredAPI['parameters'] == '':
        AlteredAPI['parameters'] = "/cards?"
    else:
        AlteredAPI['parameters'] = f"{AlteredAPI['parameters']}&"
    
    AlteredAPI['parameters'] = f"{AlteredAPI['parameters']}{param}"
    
def web_request_add_params_cardeffect(cards):
    previous_parameters = AlteredAPI['parameters']
    previous_response = AlteredAPI['response']
    for card in cards:   
        web_request_replace_params(f"/cards/{card['reference']}?locale={AlteredAPI['locale']}")
        web_request_add_headers()
        current_response = web_request_send()
        
        card['cardRulings'] = add_rulings(current_response['cardRulings'])
        if 'MAIN_EFFECT' in current_response['elements']:
            card['cardEffects'] = current_response['elements']['MAIN_EFFECT']
        else:
            card['cardEffects'] = ''
        
    web_request_replace_params(previous_parameters)
    AlteredAPI['response'] = previous_response
    
def web_request_replace_params(new_params):
    AlteredAPI['parameters'] = new_params
    return AlteredAPI['parameters']
    
def web_request_add_headers():
    AlteredAPI['httpRequest'] = request.Request(f"{AlteredAPI['endpoint']}{AlteredAPI['parameters']}",headers=AlteredAPI['headers'])
    if AlteredAPI['bearerToken'] != "":
        AlteredAPI['httpRequest'].add_header("Authorization", f"Bearer {AlteredAPI['bearerToken']}")
        
def web_request_send():
    print(f"Scanning... {AlteredAPI['endpoint']}{AlteredAPI['parameters']}")
    response = request.urlopen(AlteredAPI['httpRequest'])
    json_response = json.loads(response.read())
    AlteredAPI['response'] = json_response
    return json_response


if __name__ == "__main__":   
    main(sys.argv[1:])
