import re
import json
from collections import defaultdict
import inspect
import random
from lor_deckcodes import LoRDeck

regions = ["Freljord", "Demacia", "Ionia", "Noxus", "Piltover & Zaun", "Shadow Isles"]
keywords = ['Obliterate', 'Skill', 'Double Attack', 'Weakest', 'Elusive', 'Drain', 'Stun', 'Trap', 'Piltover & Zaun', 'Demacia', 'Shadow Isles', 'Overwhelm', 'Barrier', 'Capture', 'Frostbite', 'Burst', 'Fleeting', 'Fast', 'Overwhelm', 'Quick Attack', 'Tough', 'Recall', 'Ionia', 'Regeneration', 'Lifesteal', 'Enlightened', 'Slow', 'Noxus', 'Ephemeral', 'Freljord', 'Last Breath', 'Challenger', 'Imbue', 'Fearsome', "Can't Block", 'Neutral', 'Noxus', 'Demacia', 'Freljord', 'Shadow Isles', 'Ionia', 'Piltover & Zaun', 'Slow', 'Burst', 'Fast', 'Common', 'Rare', 'Epic', 'Champion', 'None']


class Deck:
    def __init__(self, region: str, secondRegion: str = None, *genres: "list of comparison statements that return bool"):
        assert region in regions, "First region specified not found."
        assert secondRegion == None or secondRegion in regions, "Second region specified not found."
        self.genres = [i for i in genres]
        self.region = region
        self.secondRegion = secondRegion
        
#     deckData is a nested dict that is sructured as such:
#     deckData
#         ->Regions.
#             ->Card.
#                 -> Count of how many times that card code is in the deck.
        self.deckData = dict()
        self.deckData[self.region] = defaultdict(int)
        self.deckData[self.secondRegion] = defaultdict(int)
            
        #dict that keeps track of card costs in the deck, and how many cards of a specific cost there are
        self.cardCostCount = defaultdict(int)
        self.maxCards = 40
        self.championCount = 0
        #dict that keeps track of the regions and how many cards are in that region
        self.cardCount = defaultdict(int)
        
    def addCard(self, card):       
        self.deckData[card.region][card] += 1
        self.cardCount[card.region] += 1
        self.cardCostCount[card.cost] += 1
        if card.supertype == "Champion":
            self.championCount += 1
        
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
        return f"Deck({self.region}, {self.secondRegion}, {self.genres})"

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
    if region == None: region = random.choice( [deck.region, deck.secondRegion] )
    assert region in deck.deckData, "Region specified is not in deck."
    
    # No more than 6 champion cards
    if card.supertype == "Champion":
        if deck.championCount >= 6:
            return False   
    # Card is in the correct region and is not a undeckable card
    if card.region == region and card.collectible:
#         Max of 40 cards in a deck
#         Cards below 5 cost can only have a count of < 50% (cannot have 20 3-cost cards)
#         Cards above 5 cost can only have a count of < 37.5% (cannot have 14 6-cost cards)
        if len(deck) < deck.maxCards and deck.cardCostCount[card.cost] <= .5*deck.maxCards and not deck.cardCostCount[card.cost] >= .375*deck.maxCards:
            if (deck.deckData[region].get(card.cardCode) == None or deck.deckData[region][card.cardCode] <= 3):
                return True
    return False


if __name__ == "__main__":
    #create master deck of cards
    with open("set1-en_us.json", encoding ="utf8") as cardset:
        parsed = json.load(cardset)
        masterDeck = [Card(c) for c in parsed]
        
    #add cards to specific regions or randomly assigns regions if none are specified
    def fillDeck(deck: Deck, regions: tuple = (None, None)):
        while len(deck) < 40:
            card = random.choice(masterDeck)
            if basicCheck(card, deck, regions[0]):
                deck.addCard(card)
            if basicCheck(card, deck, regions[1]):
                deck.addCard(card)
        
    #outputs a bunch of print statements to test deck
    def testingScript(deck: Deck):
        #tests str, repr, len, and return deck functions
        print(repr(deck))
        print()
        print(deck)
        print("Amount of Cards in Deck: " + str(len(deck)))
        print()
        #prints a count of keywords in card's keyword list
        K = defaultdict(int)
        for i in deck:
            for j in i.keywords:
                K[j] += 1
        print("Keywords: \n" + '\n'.join( [o + ": " + str(p) if len(K) != 0 else "None" for o,p in K.items()] ))
        print("=======================||")
        #prints a count of keywords embedded in the card descriptions
        dK = defaultdict(int)
        for i in deck:
            for j in i.descriptionKeywords:
                dK[j] += 1
        print("Description Keywords: \n" + '\n'.join( [o + ": " + str(p) if len(dK) != 0 else "None" for o,p in dK.items()] ))
        print()
        print(deck.returnDeck())
        rCode = LoRDeck(deck.returnDeck())
        print(rCode.encode())
        
    #create a deck with specifications
    print("\n\t\t/+/=====================================================[ Specific Test ]=====================================================\+\ \n")
    myDeck = Deck("Shadow Isles", "Ionia", (lambda x: x.cost < 5 ) )
    fillDeck(myDeck)
    testingScript(myDeck)
    print("\n\t\t/+/=====================================================[ All Random Test ]=====================================================\+\ \n")
    #create a deck with no specifications, filled in by randomness
    randomDeck = Deck(random.choice(regions), random.choice(regions))
    fillDeck(randomDeck)
    testingScript(randomDeck)

    