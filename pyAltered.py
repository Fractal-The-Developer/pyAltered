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
"scrape"]

AlteredAPI = {
    'endpoint': "https://api.altered.gg",
    'headers': {'User-Agent': 'pyAltered/0.0.1', 'Connection': 'keep-alive', 'Accept': '*/*'},
    'parameters': '',
    'httpRequest': '',
    'response': '',
    'bearerToken': '',
    'locale': 'en-us'
}

cardTypes = ("TOKEN_MANA",
"HERO",
"CHARACTER",
"TOKEN",
"PERMANENT",
"SPELL",
"LANDMARK_PERMANENT",
"EXPEDITION_PERMANENT")

cardSubTypes = ("ADVENTURER", 
"ANIMAL", 
"APPRENTICE", 
"ARTIST", 
"BOON", 
"BUREAUCRAT", 
"CITIZEN", 
"COMPANION", 
"CONJURATION", 
"DEITY", 
"DISRUPTION", 
"DRAGON", 
"DRUID", 
"ELEMENTAL", 
"ENGINEER", 
"FAIRY",
"GEAR",
"LANDMARK",
"LEVIATHAN",
"MAGE",
"MANEUVER",
"MESSENGER",
"NOBLE",
"PLANT",
"ROBOT",
"SCHOLAR",
"SOLDIER",
"SONG",
"SPIRIT",
"TITAN",
"TRAINER")

keywords = ("RESUPPLY",
"SEASONED",
"BOOSTED",
"BRASSBUG",
"SABOTAGE",
"BOODA",
"ORDIS_RECRUIT",
"GIGANTIC",
"TOUGH_1",
"TOUGH_2",
"TOUGH_X",
"DEFENDER",
"ETERNAL",
"AFTER_YOU",
"MAW",
"ANCHORED",
"FLEETING",
"ASLEEP")
 
dbName = "pyAltered.db"

def main(argv):
    card_value_min = 0
    card_value_max = 10
    
    Prepare_Database()
    
    try:
        arguments, values = getopt.getopt(argv,short_options,long_options)
    except getopt.GetoptError as err:
        print (str(err))
        sys.exit(2)
    
    for arguments, values in arguments:
        if arguments == '-h':
            print('usage: pyAltered.py [option]')
            print('')
            print('Options and arguments:')
            print('-h               : print this help message and exit')
            sys.exit(2)
            
        if arguments == "--authtoken":
            if values != "":
                AlteredAPI['bearerToken'] = values
            
        if arguments == "--cardsets":
            if values != "":
                setList = values.upper().split(",")
                for listValue in setList:
                    if listValue == "COREKS" or "CORE" or "ALIZE":
                        web_request_add_params_scrape(f"cardSet[]={listValue}")
                        
        if arguments == '--factions':
            if values != "":
                factionList = values.upper().split(",")
                for listValue in factionList:
                    if listValue == "AX" or "BR" or "LY" or "MU" or "OR" or "YZ":
                            web_request_add_params_scrape(f"factions[]={listValue}")
                
        if arguments == '--rarities':
            if values != "":
                rarityList = values.upper().split(",")
                for listValue in rarityList:
                    if listValue == "COMMON" or "RARE" or "UNIQUE":
                        web_request_add_params_scrape(f"rarity[]={listValue}")             
                        
        if arguments == '--cardtype':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    for cardType in cardTypes:
                        if listValue == cardType:
                            web_request_add_params_scrape(f"cardType[]={listValue}")   
                            
        if arguments == '--cardsubtype':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    for subType in cardSubTypes:
                        if listValue == subType:
                            web_request_add_params_scrape(f"cardSubType[]={listValue}")    

        if arguments == '--handcost':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    if card_value_min <= listValue.int() <= card_value_max:
                        web_request_add_params_scrape(f"mainCost[]={listValue}")                               
 
        if arguments == '--reservecost':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    if card_value_min <= listValue.int() <= card_value_max:
                        web_request_add_params_scrape(f"recallCost[]={listValue}")  
                        
        if arguments == '--forestpower':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    if card_value_min <= int(listValue) <= card_value_max:
                        web_request_add_params_scrape(f"forestPower[]={listValue}")
                        
        if arguments == '--mountainpower':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    if card_value_min <= int(listValue) <= card_value_max:
                        web_request_add_params_scrape(f"mountainPower[]={listValue}")
                        
        if arguments == '--oceanpower':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    if card_value_min <= int(listValue) <= card_value_max:
                        web_request_add_params_scrape(f"oceanPower[]={listValue}")   
                        
        if arguments == '--keyword':
            if values != "":
                argList = values.upper().split(",")
                for listValue in argList:
                    for word in keywords:
                        if word == listValue:
                            web_request_add_params_scrape(f"keyword[]={listValue}")
                        
        if arguments == '--foiled':
            web_request_add_params_scrape("foiled=true")
            
        if arguments == '--altart':
            web_request_add_params_scrape("altArt=true")
            
        if arguments == '--collection':
            if AlteredAPI['bearerToken'] == "":
                raise Exception("Argument --collection must be used with --authtoken to find your card collection")
            else:
                web_request_add_params_scrape("collection=true")
            
        if arguments == '--suspended':
            if values != "":
                argList = values.split(",")
                for listValue in argList:
                    if type(listValue) == bool:
                        web_request_add_params_scrape(f"isSuspended[]={listValue}")
                        
        if arguments == '--exclusive':
            if values != "":
                argList = values.split(",")
                for listValue in argList:
                    if type(listValue) == bool:
                        web_request_add_params_scrape(f"isExclusive[]={listValue}")
                        
        if arguments == '--locale':
            if values != "":
                AlteredAPI['locale'] = values
                        
    web_request_add_headers()
    web_request_send()
    build_card_list()
    print("Complete!")


def Prepare_Database():
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
        

def Add_Cards(cards):
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
        
def Add_Rulings(cardRulings):
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
        
        card['cardRulings'] = Add_Rulings(current_response['cardRulings'])
        if 'MAIN_EFFECT' in current_response['elements']:
            card['cardEffects'] = current_response['elements']['MAIN_EFFECT']
        else:
            card['cardEffects'] = ''
        
    web_request_replace_params(previous_parameters)
    AlteredAPI['response'] = previous_response
    
      
def build_card_list():
    extractedCards = AlteredAPI['response']['hydra:member']
    pages = AlteredAPI['response']['hydra:view']
    
    if pages['@id'] != pages['hydra:last']:
        web_request_add_params_cardeffect(extractedCards)
        Add_Cards(extractedCards)
        web_request_replace_params(pages['hydra:next'])
        web_request_add_headers()
        web_request_send()
        build_card_list()
    
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
