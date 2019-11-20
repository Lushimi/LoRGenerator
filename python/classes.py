import inspect
import re
import json
import random
from collections import defaultdict

class Deck:
    """
    A collection of cards and meta data about the collection of cards.
    """
    def __init__(self, region: str, secondRegion: str, *genres: (lambda card, deck: Bool) ):
        assert region in REGIONS, "First region specified not found."
        assert secondRegion == None or secondRegion in REGIONS, "Second region specified not found."
        gp = [i.property for i in genres]
        for i in gp:
            if gp.count(i) > 1:
                raise ValueError("Cannot have more than one genre of the same type.")
        self.genres = sorted([i for i in genres], key = lambda x: x.property)
        self.region = region
        if secondRegion == None:
            self.secondRegion = region
        else:
            self.secondRegion = secondRegion
                 
        '''
            "deckData" is a nested dict that is structured as such:
            deckData
                |
                -> region (Region in deck)
                    |
                    -> card (Card object in deck)
                        |
                        -> count (Count of how many times that card is in the deck.)
        '''
            
        self.possibleCards = DECKS[region]
        self.possibleCards.extend(DECKS[secondRegion])
        self.deckData = dict()
        self.deckData[self.region] = defaultdict(int)
        self.deckData[self.secondRegion] = defaultdict(int)
#        Dictionary that keeps track of card costs in the deck, and how many cards of a specific cost there are.
        self.cardCostCount = defaultdict(int)
#        Dictionary that keeps track of subtypes in deck, and how many cards of each subtype there are.
        self.cardTypeCount = defaultdict(int)
        self.maxCards = 40
        self.championCount = 0
#        Dictionary that keeps track of the regions and how many cards are in that region.
        self.cardCount = defaultdict(int)
        
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
            if region != None: rString += f"{region} ({self.cardCount[region]} Cards): \n"
            for card, count in sorted(data.items(), key = lambda x: x[0].name):
                rString += f"\t[{card.type}] {card.name}: {count}\n"
        return rString
    
#     Iterates through every card in the deck.
    def __iter__(self):
        wholeList = []
        for regions, data in self.deckData.items():
            for card,count in data.items():
                wholeList += [card]*count
        for i in wholeList:
            yield i
              
    def addCard(self, card, override = False):
#         Only add card if ALL genres are satisfied
        b = []
        for i in self.genres:
            b.append(i(card, self))
        if all(b) == True or override:
            assert card.region in self.deckData, "Tried to add card to deck without required region."
            self.deckData[card.region][card] += 1
            self.cardCount[card.region] += 1
            self.cardCostCount[card.cost] += 1
            self.cardTypeCount[card.type] += 1
            if card.supertype == "Champion":
                self.championCount += 1
    
    def returnDeck(self)-> list:
        rList = []
        for data in self.deckData.values():
            for card, count in data.items():
                rList.append( f"{count}:{card.cardCode}" )
        return rList

    #     Add cards to specific regions or randomly assigns regions if none are specified, returns if it filled a valid deck or not (bool).
    def fillDeck(self)-> bool:
        try:
            infinitePrevention = 0
            while len(self) < 40:
                card = random.choice(self.possibleCards)
                self.addCard(card)
                infinitePrevention += 1
                assert infinitePrevention < 9999, "\n\t!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\t\t=+= COULD NOT CREATE A DECK WITH THE SPECIFIED CRITERIA. =+=\t\t!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            return True
        except AssertionError as errorStatement:
            print(errorStatement)
            return False
        
    #     Add cards bypassing the genres.
    def cardOverride(self, cardName:str, amount:int):
        for card in self.possibleCards:
            if (card.name == cardName or card.cardCode == cardName) and card.collectible:
                addingCard = card
                break
        for i in range(amount):
            self.addCard(addingCard, True)

#     Outputs a bunch of print statements to test a deck
    def printDeckInfo(self):
#         Tests str, repr, len, and return self functions
        print(repr(self))
        print()
        print(self)
        print("Amount of Cards in Deck: " + str(len(self)))
        print()
#         Prints a count of keywords in card's keyword list
        K = defaultdict(int)
        for i in self:
            for j in i.keywords:
                K[j] += 1
        print("Keywords: \n" + '\n'.join( ["    " + o + ": " + str(p) if len(K) != 0 else "None" for o,p in sorted(K.items())] ))
        print("=======================||")
#         Prints a count of keywords embedded in the card descriptions
        dK = defaultdict(int)
        for i in self:
            for j in i.descriptionKeywords:
                dK[j] += 1
        print("Description Keywords: \n" + '\n'.join( ["    " + o + ": " + str(p) if len(dK) != 0 else "None" for o,p in sorted(dK.items())] ))
        print("=======================||")
#         Prints a count of vocab words embedded in the card descriptions   
        dV = defaultdict(int)
        for i in self:
            for j in i.vocab:
                dV[j] += 1
        print("Vocab: \n" + '\n'.join( ["    " + o + ": " + str(p) if len(dV) != 0 else "None" for o,p in sorted(dV.items())] ))
        print("=======================||") 
#         Prints cost of cards in self
        for k,v in sorted(self.cardCostCount.items()):
            print(f"Cost {k}: {v}")
        


class Card:
    """
    Is a collection of all data a Legends of Runeterra card has.
    """
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
        self.vocab = []
        prog = re.compile(r'<link=keyword.([a-z|A-Z]*)>')
        hiddenWords = prog.search(self.description)
        if hiddenWords != None:
            hiddenKey = hiddenWords.group(1)
            self.descriptionKeywords += [hiddenKey]
        if ("discard" in self.description or "Discard" in self.description) and "Discard" not in self.descriptionKeywords:
            self.descriptionKeywords += ["Discard"]
        if ("enemy nexus" in self.description or "enemy Nexus" in self.description) and "Burn" not in self.descriptionKeywords:
            self.descriptionKeywords += ["Burn"]
        if "<link=card.create>" in self.description and "<link=card.create><style=AssociatedCard>Spiderling" not in self.description and "Create"  not in self.descriptionKeywords:
            self.descriptionKeywords += ["Create"]  
        if "<link=card.summon>" in self.description and "Summon" not in self.descriptionKeywords:
            self.descriptionKeywords += ["Summon"]
        if ("give " in self.description or "Give " in self.description or "grant " in self.description or "Grant " in self.description) and "Buff" not in self.descriptionKeywords:
            self.descriptionKeywords += ["Buff"]
            
        prog = re.compile(r'<link=vocab.([a-z|A-Z]*)>')
        hiddenWords = prog.search(self.description)
        if hiddenWords != None:
            hiddenKey = hiddenWords.group(1)
            self.vocab += [hiddenKey]
            
        if "<style=VocabNoTooltip>Attack</style>" in self.vocab and "Attack" not in self.vocab:
            self.vocab += ["Attack"]
    
    def __str__(self) -> str:
        return self.name + ": " + self.cardCode

# ///////////////////////////////////////////////  All GLOBAL CONSTANTS  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
"""
    A bunch of global variables to use in other functions.
"""
REGIONS = ["Freljord", "Demacia", "Ionia", "Noxus", "Piltover & Zaun", "Shadow Isles"]
KEYWORDS = ['Obliterate', 'Skill', 'Double Attack', 'Weakest', 'Elusive', 'Drain', 'Stun', 'Trap', 'Piltover & Zaun', 'Demacia', 'Shadow Isles', 'Overwhelm', 'Barrier', 'Capture', 'Frostbite', 'Burst', 'Fleeting', 'Fast', 'Overwhelm', 'Quick Attack', 'Tough', 'Recall', 'Ionia', 'Regeneration', 'Lifesteal', 'Enlightened', 'Slow', 'Noxus', 'Ephemeral', 'Freljord', 'Last Breath', 'Challenger', 'Imbue', 'Fearsome', "Can't Block", 'Neutral', 'Noxus', 'Demacia', 'Freljord', 'Shadow Isles', 'Ionia', 'Piltover & Zaun', 'Slow', 'Burst', 'Fast', 'Common', 'Rare', 'Epic', 'Champion', 'Discard', 'Nexus', 'Create', 'Summon', 'Buff', 'Burn', 'None']
VOCAB = ['Strike', 'Allegiance', 'Support', 'Strongest', 'Play', 'Attack']
SUBTYPES = ['', 'Spider', 'Yeti', 'Tech', 'Elite', 'Elnuk', 'Poro']
#     Creates master deck of cards and a master DECK dictionary for each regions' cards.
with open("set1-en_us.json", encoding ="utf8") as cardset:
    parsed = json.load(cardset)
    
    
    
    DECKS = {}
    for r in REGIONS:
        DECKS[r] = []
    for c in parsed:
        temp = Card(c)
        DECKS[temp.region] += [temp]
    del temp
    del parsed
    masterDeck = [c for l in DECKS.values() for c in l]
    
    REGION_WORDS = defaultdict(dict)
    for k,v in DECKS.items():
        REGION_WORDS[k]["Keywords"] = set()
        REGION_WORDS[k]["Subtypes"] = set()
        REGION_WORDS[k]["Vocab"] = set()
        for c in v:
            REGION_WORDS[k]["Keywords"] |= set(c.keywords) | set(c.descriptionKeywords)
            REGION_WORDS[k]["Subtypes"] |= {c.subtype} 
            REGION_WORDS[k]["Vocab"] |= set(c.vocab)
            

if __name__ == "__main__":
    print('Please run all testing from the main.py')