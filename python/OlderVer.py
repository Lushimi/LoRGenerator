'''
Created on Nov 6, 2019

RGAPI-aed6922c-1314-4f08-a726-82995180ccde

@author: lexth
'''
import re
import json
from collections import defaultdict
import inspect
import random
from lor_deckcodes import LoRDeck

apiKey = "RGAPI-aed6922c-1314-4f08-a726-82995180ccde"

regions = {"Freljord", "Demacia", "Ionia", "Noxus", "Piltover & Zaun", "Shadow Isles"}
keywords = {'Obliterate', 'Skill', 'Double Attack', 'Weakest', 'Elusive', 'Drain', 'Stun', 'Trap', 'Piltover & Zaun', 'Demacia', 'Shadow Isles', 'Overwhelm', 'Barrier', 'Capture', 'Frostbite', 'Burst', 'Fleeting', 'Fast', 'Overwhelm', 'Quick Attack', 'Tough', 'Recall', 'Ionia', 'Regeneration', 'Lifesteal', 'Enlightened', 'Slow', 'Noxus', 'Ephemeral', 'Freljord', 'Last Breath', 'Challenger', 'Imbue', 'Fearsome', "Can't Block", 'Neutral', 'Noxus', 'Demacia', 'Freljord', 'Shadow Isles', 'Ionia', 'Piltover & Zaun', 'Slow', 'Burst', 'Fast', 'Common', 'Rare', 'Epic', 'Champion', 'None'}


class Deck:
    def __init__(self, region: str, secondRegion: str = None, *genres: "list of comparison statements that return bool"):
        assert region in regions, "First region specified not found."
        self.region = region
        #deckData is a nested dict that is sructured
#         deckData
#            ->Regions.
#                 ->Card Codes.
#                     -> Count of how many times that card code is in the deck.
        self.deckData = dict()
        self.deckData[region] = defaultdict(int)
        if secondRegion:
            assert secondRegion in regions, "Second region specified not found"
            self.secondRegion = secondRegion
            self.deckData[secondRegion] = defaultdict(int) 
        self.maxCards = 40
        self.genres = [i for i in genres]
        self.cardCostCount = defaultdict(int)
        self.championCount = 0
        self.cardCount = 0
        
    def addCard(self, card, region = None):
        if region == None:
            region = self.region
        if region == self.region or region == self.secondRegion:
            self.deckData[region][card.cardCode] += 1
            self.cardCostCount[card.cost] += 1
            if card.supertype == "Champion":
                self.championCount += 1
        self.cardCount += 1
        
    def __setattr__(self, name, value):
        calling = inspect.stack()[1]
        assert calling.function != '__init__' or calling.function != 'addCard', "Cannot set attributed directly, only can be intialized or done with addCard."
        self.__dict__[name] = value
        

    def __len__(self)-> int:
        return(self.cardCount)

        
    def __repr__(self)-> str:
        return str(self.__dict__)

    def __str__(self)-> str:
        rString = ""
        for region, data in self.deckData.items():
            rString += f"{region}: \n"
            for k,v in data.items():
                rString += f"{v}:{k}\n"
        return rString
    
    def returnDeck(self)-> list:
        rList = []
        for data in self.deckData.values():
            for k,v in data.items():
                rList.append( f"{v}:{k}" )
        return rList


class Card:
    def __init__(self, db: dict):
        self.associatedCards = db["associatedCards"]
        self.associatedCardRefs = db["associatedCardRefs"]
        self.assets = db["assets"]
        self.region = db["region"]
        self.regionRef = db["regionRef"]
        self.attack = db["attack"]
        self.cost = db["cost"]
        self.health = db["health"]
        self.description = db["description"]
        self.descriptionRaw = db["descriptionRaw"]
        self.flavorText = db["flavorText"]
        self.artistName = db["artistName"]
        self.name = db["name"]
        self.cardCode = db["cardCode"]
        self.keywords = db["keywords"]
        self.keywordRefs = db["keywordRefs"]
        self.spellSpeed = db["spellSpeed"]
        self.spellSpeedRef = db["spellSpeedRef"]
        self.rarity = db["rarity"]
        self.rarityRef = db["rarityRef"]
        self.subtype = db["subtype"]
        self.supertype = db["supertype"]
        self.type = db["type"]
        self.collectible = db["collectible"]
    
    def __str__(self):
        return self.name + ": " + self.cardCode


def basicCheck(card, deck: Deck, region = None):
    if region == None: region = deck.region
    assert region in deck.deckData, "Faction specified is not in deck."
    
    if card.supertype == "Champion":
        if deck.championCount >= 6:
            return False   
    # if card is the correct region and isn't a subtype
    if card.region == region and len(card.cardCode) <= 7:
        #Max of 40 cards in a deck
#         Cards below 5 cost can only have a count of < 50% (cannot have 20 3-cost cards)
#         Cards above 5 cost can only have a count of < 37.5% (cannot have 14 6-cost cards)
        if len(deck) < deck.maxCards and deck.cardCostCount[card.cost] <= .5*deck.maxCards and not deck.cardCostCount[card.cost] >= .375*deck.maxCards:
            if (deck.deckData.get(card.cardCode) == None or deck.deckData[card.cardCode] <= 3):
                return True
    return False


if __name__ == "__main__":
    with open("set1-en_us.json", encoding ="utf8") as cardset:
        parsed = json.load(cardset)
#         keywordDict = defaultdict(set)
        myDeck = Deck("Shadow Isles", "Ionia", (lambda x: x.cost < 5 ) )
        print(repr(myDeck))
        
        prog = re.compile(r'<link=keyword.([a-z|A-Z]*)>')
        descString = card['description']
        hiddenWords = prog.search(descString)
        if hiddenWords != None:
            hiddenKey = hiddenWords.group(1)
            keywordDict[card["region"]] |= set([hiddenKey])
        keywordDict[card["region"]] |= set(card["keywords"])
        
        masterDeck = [Card(c) for c in parsed]
        for i in range(len(masterDeck) + 1):
            card = random.choice(masterDeck)
            if basicCheck(card, myDeck, "Ionia"):
                myDeck.addCard(card, "Ionia")
            if basicCheck(card, myDeck, "Shadow Isles"):
                myDeck.addCard(card, "Shadow Isles")

#         for card in parsed:
#             keywordDict[card["region"]] = dict.fromkeys(keywordDict[card["region"]], 1)
#         for card in parsed:
#             for keyword in card["keywords"]:
#                 keywordDict[card["region"]][keyword] += 1
# 
#         rString = ""
#         for region, data in keywordDict.items():
#             rString += f"{region}: "
#             for key, count in data.items():
#                 rString += f"{key}[{count}], "
#             rString = rString[:-2]
#             rString += "\n"
#     print(rString)
    print(myDeck)
    print(repr(myDeck))
    print(len(myDeck))
    print(myDeck.returnDeck())
    deckCode = LoRDeck(myDeck.returnDeck())
    print(deckCode.encode())