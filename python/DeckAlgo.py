import re
import json
from collections import defaultdict
import inspect
import random
from lor_deckcodes import LoRDeck

REGIONS = ["Freljord", "Demacia", "Ionia", "Noxus", "Piltover & Zaun", "Shadow Isles"]
KEYWORDS = ['Obliterate', 'Skill', 'Double Attack', 'Weakest', 'Elusive', 'Drain', 'Stun', 'Trap', 'Piltover & Zaun', 'Demacia', 'Shadow Isles', 'Overwhelm', 'Barrier', 'Capture', 'Frostbite', 'Burst', 'Fleeting', 'Fast', 'Overwhelm', 'Quick Attack', 'Tough', 'Recall', 'Ionia', 'Regeneration', 'Lifesteal', 'Enlightened', 'Slow', 'Noxus', 'Ephemeral', 'Freljord', 'Last Breath', 'Challenger', 'Imbue', 'Fearsome', "Can't Block", 'Neutral', 'Noxus', 'Demacia', 'Freljord', 'Shadow Isles', 'Ionia', 'Piltover & Zaun', 'Slow', 'Burst', 'Fast', 'Common', 'Rare', 'Epic', 'Champion', 'Discard', 'Nexus', 'Create', 'Summon', 'Buff' 'None']
VOCAB = ['Strike', 'Allegiance', 'Support', 'Strongest', 'Play', 'Attack']
SUBTYPES = ['', 'Spider', 'Yeti', 'Tech', 'Elite', 'Elnuk', 'Poro']

class Deck:
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
            for card, count in data.items():
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
              
    def addCard(self, card):
#         Only add card if ALL genres are satisfied
        b = []
        for i in self.genres:
            b.append(i(card, self))
        if all(b) == True:
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

# Genre types (decorator functions).
def basic(f):
    f.property = "basic"
    return f
def region_bias(f):
    f.property = "region_bias"
    return f
def keyword_bias(f):
    f.property = "keyword_bias"
    return f
def type_bias(f):
    f.property ="type_bias"
    return f

# ///////////////////////////////////////////////  All GENRES  \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
"""
    To create a "genre" define a function that returns bool, decorate it with a proper genre type (copy paste following function as a template) => 
    @genre_type
    def genreFunction(deck, card)-> bool:
        if (condition):
#         Card is not added to deck.
            return False
        else:
#         Card is added to deck.
            return True 
    
    If you want to create your own genre type =>
    def genre_type(f):
        f.property = "genre_type"
        return f
"""

@basic
def basicCheck(card, deck) -> bool:
    region = random.choice( [deck.region, deck.secondRegion] )
    assert region in deck.deckData, "Region specified is not in deck."
#     Passes by card if there's already 6 champion cards.
    if card.supertype == "Champion":
        if deck.championCount >= 6:
            return False   
#     Card is in the correct region and is not an undeckable card
    if card.region == region and card.collectible:
#         Max of 40 cards in a deck
#         Cards below 5 cost can only have a count of < 50% (cannot have 20 3-cost cards)
#         Cards above 5 cost can only have a count of < 37.5% (cannot have 14 6-cost cards)
        if len(deck) < deck.maxCards and deck.cardCostCount[card.cost] <= .5*deck.maxCards and not deck.cardCostCount[card.cost] >= .375*deck.maxCards:
            if deck.deckData[region].get(card) == None:
                return True
            elif deck.deckData[region][card] < 3:
                return True
    return False

@region_bias
def firstRegionBias(card, deck)-> bool:
    if deck.secondRegion != deck.region:
        if card.region == deck.secondRegion:
            if deck.cardCount[deck.secondRegion] >= 8:
                return False
    return True

@region_bias  
def secondRegionBias(card, deck)-> bool:
    if deck.secondRegion != deck.region:
        if card.region == deck.region:
            if deck.cardCount[deck.region] >= 8:
                return False
    return True
        
@region_bias
def halfSplit(card, deck)-> bool:
    if deck.secondRegion != deck.region:
        if card.region == deck.region:
            if deck.cardCount[deck.region] == 20:
                return False
    return True

def RBM(secondRegionAmount: int = 20):
    @region_bias
    def ratioRegionBias(card, deck)-> bool:
        if deck.secondRegion != deck.region:
            if card.region == deck.secondRegion:
                if deck.cardCount[deck.secondRegion] >= secondRegionAmount:
                    return False
        return True
    return ratioRegionBias

@type_bias
def spellBias(card, deck)-> bool:
    if card.type == "Unit":
        if deck.cardTypeCount["Unit"] >= 10:
            return False
    return True

@type_bias
def unitBias(card, deck)-> bool:
    if card.type == "Spell":
        if deck.cardTypeCount["Spell"] >= 10:
            return False
    return True

#Lower strength means higher bias; for example if the keyword was ephemeral, strength of 0 means all cards will be ephemeral.
def KBM(keyword: str = random.choice(KEYWORDS), strength: int = 3):
    assert keyword in KEYWORDS, "Specified keyword not found."
    @keyword_bias
    def keywordBias(card, deck)-> bool:
        #look at all keywords in cards
        kSet = set()
        for l in card.keywords:
                kSet |= {l}
        for l in card.descriptionKeywords:
                kSet |= {l}
        joinedKeywords = defaultdict(int)
        for i in deck:
            for j in i.keywords:
                joinedKeywords[j] += 1
        for i in deck:
            for j in i.descriptionKeywords:
                joinedKeywords[j] += 1
        for cK in kSet:
            if cK != keyword:
                if joinedKeywords[cK] >= strength:
                    return False
        return True
    return keywordBias

#opposite of KBM
#Lower strength means lower bias; for example if the keyword was ephemeral, strength of 40 means all cards will be ephemeral.
def NKBM(keyword: str = random.choice(KEYWORDS), strength: int = 3):
    assert keyword in KEYWORDS, "Specified keyword not found."
    @keyword_bias
    def keywordBias(card, deck)-> bool:
        #look at all keywords in cards
        kSet = set()
        for l in card.keywords:
                kSet |= {l}
        for l in card.descriptionKeywords:
                kSet |= {l}
        joinedKeywords = defaultdict(int)
        for i in deck:
            for j in i.keywords:
                joinedKeywords[j] += 1
        for i in deck:
            for j in i.descriptionKeywords:
                joinedKeywords[j] += 1
        for cK in kSet:
            if cK == keyword:
                if joinedKeywords[cK] >= strength:
                    return False
        return True
    return keywordBias

GENRES = [basicCheck, firstRegionBias, secondRegionBias, halfSplit, KBM(), NKBM(), RBM(), spellBias, unitBias]

def randomGenreList(genres)-> list:
    gCount = defaultdict(int)
    gList = []
#     TODO change this
    for i in range(len(genres)):
        randomGenre = random.choice(genres)
        gCount[randomGenre.property] += 1
        if gCount[randomGenre.property] <= 1:
            gList.append(randomGenre)
    return gList

if __name__ == "__main__":
#     Creates master deck of cards
    with open("set1-en_us.json", encoding ="utf8") as cardset:
        parsed = json.load(cardset)
        masterDeck = [Card(c) for c in parsed]
        
#     Add cards to specific regions or randomly assigns regions if none are specified
    def fillDeck(deck: Deck):
        infinitePrevention = 0
        while len(deck) < 40:
            card = random.choice(masterDeck)
            deck.addCard(card)
            infinitePrevention += 1
            assert infinitePrevention < 99999, "Cannot create a deck with specified criteria."
        
#     Outputs a bunch of print statements to test a deck
    def testingScript(deck: Deck):
#         Tests str, repr, len, and return deck functions
        print(repr(deck))
        print()
        print(deck)
        print("Amount of Cards in Deck: " + str(len(deck)))
        print()
#         Prints a count of keywords in card's keyword list
        K = defaultdict(int)
        for i in deck:
            for j in i.keywords:
                K[j] += 1
        print("Keywords: \n" + '\n'.join( ["    " + o + ": " + str(p) if len(K) != 0 else "None" for o,p in K.items()] ))
        print("=======================||")
#         Prints a count of keywords embedded in the card descriptions
        dK = defaultdict(int)
        for i in deck:
            for j in i.descriptionKeywords:
                dK[j] += 1
        print("Description Keywords: \n" + '\n'.join( ["    " + o + ": " + str(p) if len(dK) != 0 else "None" for o,p in dK.items()] ))
        print("=======================||")
        dV = defaultdict(int)
        for i in deck:
            for j in i.vocab:
                dV[j] += 1
        print("Vocab: \n" + '\n'.join( ["    " + o + ": " + str(p) if len(dV) != 0 else "None" for o,p in dV.items()] ))
        print()
        for region, data in deck.deckData.items():
            for card, count in data.items():
                if count > 3:
                    print("COULD NOT CREATE A VALID DECK FROM THIS CRITERIA. ADDED AN EXTRA CARD (MORE THAN THE 3-MAX LIMIT).")
        print(deck.returnDeck())
        rCode = LoRDeck(deck.returnDeck())
        print(rCode.encode())
        
        
# TESTING LINES
#     Test a deck with specifications
    print("\n\t\t/+/=====================================================[ Specific Test ]=====================================================\+\ \n")
    myDeck = Deck("Shadow Isles", "Ionia", basicCheck, KBM("Ephemeral", 3), firstRegionBias)
    fillDeck(myDeck)
    testingScript(myDeck)
    print("\n\t\t/+/=====================================================[ All Random Test ]=====================================================\+\ \n")
#     Test a deck with no specifications, filled in by randomness
    g = randomGenreList(GENRES)
    #g = [KBM("Ephemeral")]
    if basicCheck not in g: g.append(basicCheck)
    randomDeck = Deck(random.choice(REGIONS), random.choice(REGIONS), *g)
    fillDeck(randomDeck)
    testingScript(randomDeck)

    