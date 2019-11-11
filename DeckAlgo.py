
import re
import json
from collections import defaultdict
import inspect
import random
from lor_deckcodes import LoRDeck

regions = ["Freljord", "Demacia", "Ionia", "Noxus", "Piltover & Zaun", "Shadow Isles"]
keywords = ['Obliterate', 'Skill', 'Double Attack', 'Weakest', 'Elusive', 'Drain', 'Stun', 'Trap', 'Piltover & Zaun', 'Demacia', 'Shadow Isles', 'Overwhelm', 'Barrier', 'Capture', 'Frostbite', 'Burst', 'Fleeting', 'Fast', 'Overwhelm', 'Quick Attack', 'Tough', 'Recall', 'Ionia', 'Regeneration', 'Lifesteal', 'Enlightened', 'Slow', 'Noxus', 'Ephemeral', 'Freljord', 'Last Breath', 'Challenger', 'Imbue', 'Fearsome', "Can't Block", 'Neutral', 'Noxus', 'Demacia', 'Freljord', 'Shadow Isles', 'Ionia', 'Piltover & Zaun', 'Slow', 'Burst', 'Fast', 'Common', 'Rare', 'Epic', 'Champion', 'None']


class Deck:
    def __init__(self, region: str = None, secondRegion: str = None, *genres: "list of comparison statements that return bool"):
        assert region == None or region in regions, "First region specified not found."
        assert secondRegion == None or secondRegion in regions, "Second region specified not found."
        self.genres = [i for i in genres]
        self.region = region
        self.secondRegion = secondRegion
        if region == None:
            self.region = random.choice(regions)
        
#     deckData is a nested dict that is sructured as such:
#     deckData
#         ->Regions.
#             ->Card.
#                 -> Count of how many times that card code is in the deck.
        self.deckData = dict()
        self.deckData[self.region] = defaultdict(int)
        self.deckData[self.secondRegion] = defaultdict(int)
            
        self.cardCostCount = defaultdict(int)
        self.maxCards = 40
        self.championCount = 0
        self.cardCount = defaultdict(int)
        
    def addCard(self, card, region = None):
        if region == None:
            region = self.region
        if region == self.region or region == self.secondRegion:            
            self.deckData[region][card] += 1
            self.cardCount[region] += 1
            self.cardCostCount[card.cost] += 1
            if card.supertype == "Champion":
                self.championCount += 1
                
    def removeCard(self, card, region = None):
        if region == None:
            region = self.region
        if region == self.region or region == self.secondRegion:
            self.deckData[region][card] -= 1
            self.cardCount[region] -= 1
            self.cardCostCount[card.cost] -=1
            if card.supertype == "Champion":
                self.championCount -= 1
            
    def __setattr__(self, name, value):
        calling = inspect.stack()[1]
        assert calling.function != '__init__' or calling.function != 'addCard', "Cannot set attributed directly, only can be intialized or done with addCard."
        self.__dict__[name] = value
        

    def __len__(self)-> int:
        count = 0
        for i in self.cardCount.values():
            count += i
        return count

        
    def __repr__(self)-> str:
        return str(self.__dict__)

    def __str__(self)-> str:
        rString = ""
        for region, data in self.deckData.items():
            if region != None: rString += f"{region}: \n"
            for card, count in data.items():
                rString += f"\t[{card.type}] {card.name}: {count}\n"
        return rString
    
    def __iter__(self):
        wholeList = []
        for regions, data in self.deckData.items():
            for card,count in data.items():
                wholeList += [card]*count
        for i in wholeList:
            yield i
    
    def returnDeck(self)-> list:
        rList = []
        for data in self.deckData.values():
            for card, count in data.items():
                rList.append( f"{count}:{card.cardCode}" )
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
        self.descriptionKeywords = []
        prog = re.compile(r'<link=keyword.([a-z|A-Z]*)>')
        hiddenWords = prog.search(self.description)
        if hiddenWords != None:
            hiddenKey = hiddenWords.group(1)
            self.descriptionKeywords += [hiddenKey]

    
    def __str__(self):
        return self.name + ": " + self.cardCode


def basicCheck(card, deck: Deck, region = None):
    if region == None: region = deck.region
    assert region in deck.deckData, "Region specified is not in deck."
    
    # No more than 6 champion cards
    if card.supertype == "Champion":
        if deck.championCount >= 6:
            return False   
    # Card is in the correct region and isnt a subcard
    if card.region == region and len(card.cardCode) <= 7:
#         Max of 40 cards in a deck
#         Cards below 5 cost can only have a count of < 50% (cannot have 20 3-cost cards)
#         Cards above 5 cost can only have a count of < 37.5% (cannot have 14 6-cost cards)
        if len(deck) < deck.maxCards and deck.cardCostCount[card.cost] <= .5*deck.maxCards and not deck.cardCostCount[card.cost] >= .375*deck.maxCards:
            if (deck.deckData[region].get(card.cardCode) == None or deck.deckData[region][card.cardCode] <= 3):
                return True
    return False


if __name__ == "__main__":
    with open("set1-en_us.json", encoding ="utf8") as cardset:
        parsed = json.load(cardset)
        masterDeck = [Card(c) for c in parsed]
    myDeck = Deck("Shadow Isles", "Ionia", (lambda x: x.cost < 5 ) )
    randomDeck = Deck()
    
    for i in range(len(masterDeck) + 1):
        card = random.choice(masterDeck)
        if basicCheck(card, myDeck, "Ionia"):
            myDeck.addCard(card, "Ionia")
        if basicCheck(card, myDeck, "Shadow Isles"):
            myDeck.addCard(card, "Shadow Isles")
        if basicCheck(card, randomDeck):
            randomDeck.addCard(card)

    print(randomDeck)
    print(len(randomDeck))
    rCode = LoRDeck(randomDeck.returnDeck())
    print(rCode.encode())
    
    print(myDeck)
    print(repr(myDeck))
    print(len(myDeck))
    print(myDeck.returnDeck())
    print( [i.descriptionKeywords for i in myDeck] )
    deckCode = LoRDeck(myDeck.returnDeck())
    print(deckCode.encode())