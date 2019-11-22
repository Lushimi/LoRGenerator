import re
import json
from collections import defaultdict
import inspect
import random
from lor_deckcodes import LoRDeck
import os.path
from pathlib import Path

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
savepath = Path(os.getcwd()) / "set1-en_us.json"
with open(savepath, encoding ="utf8") as cardset:
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
def vocab_bias(f):
    f.property ="type_bias"
    return f
def cost_bias(f):
    f.property = "cost_bias"
    return f
def name_bias(f):
    f.property = "name_bias"
    return f
def mixed(f):
    f.property ="mixed"
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
    """
    This is to ensure the deck is valid, it is in by default.
    """
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
    """
    Biases the deck towards the first region specified. If mono-region, then it will do nothing.
    """
    if deck.secondRegion != deck.region:
        if card.region == deck.secondRegion:
            if deck.cardCount[deck.secondRegion] >= 8:
                return False
    return True

@region_bias  
def secondRegionBias(card, deck)-> bool:
    """
    Biases the deck towards the second region specified. If mono-region, then it will do nothing.
    """
    if deck.secondRegion != deck.region:
        if card.region == deck.region:
            if deck.cardCount[deck.region] >= 8:
                return False
    return True
        
@region_bias
def halfSplit(card, deck)-> bool:
    """
    Tries to make a 20/20 deck.
    """
    if deck.secondRegion != deck.region:
        if card.region == deck.region:
            if deck.cardCount[deck.region] == 20:
                return False
    return True

@region_bias
def RBM(secondRegionAmount: int = 20):
    """ RBM(30) Specify the second region amount, default is 20. """
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
    """
    Biases the deck towards spell cards.
    """
    if card.type == "Unit":
        if deck.cardTypeCount["Unit"] >= 10:
            return False
    return True

@type_bias
def unitBias(card, deck)-> bool:
    """
    Biases the deck towards unit cards.
    """
    if card.type == "Spell":
        if deck.cardTypeCount["Spell"] >= 10:
            return False
    return True

#Keyword Bias Maker, Soft bias towards keyword.
#Lower strength means higher bias; for example if the keyword was ephemeral, strength of 0 means all cards will be ephemeral.
@keyword_bias
def KBM(keyword: str = random.choice(KEYWORDS), strength: int = 3):
    """
    KBM('Keyword', strength) Soft bias. Specify the key word and strength of bias, default is a random keyword and a strength of 3.
    Lower strength means higher bias; for example if the keyword was ephemeral, strength of 0 means all cards will be ephemeral.
    """
    assert keyword in KEYWORDS, "Specified keyword not found."
    @keyword_bias
    def keywordBias(card, deck)-> bool:
#         assert keyword in REGION_WORDS[deck.region]["Keywords"]|REGION_WORDS[deck.secondRegion]["Keywords"], "Randomly picked invalid word."
        allCardKeywords = set()
        for kw in card.keywords:
                allCardKeywords |= {kw}
        for kw in card.descriptionKeywords:
                allCardKeywords |= {kw}
        allDeckKeywords = defaultdict(int)
        for card in deck:
            for kw in card.keywords:
                allDeckKeywords[kw] += 1
        for card in deck:
            for kw in card.descriptionKeywords:
                allDeckKeywords[kw] += 1
        for cardKW in allCardKeywords:
            if cardKW != keyword:
                if allDeckKeywords[cardKW] >= strength:
                    return False
        return True
    return keywordBias

#Stronger than KBM, hard bias.
#Strength is the minimum number of cards from the keyword you want in your deck.
@keyword_bias
def NKBM(keyword: str = random.choice(KEYWORDS), strength: int = 7):
    """
    NKBM('Keyword', strength) Soft bias. Specify the key word and strength of bias, default is a random keyword and a strength of 7.
    Strength is the minimum number of cards from the keyword you want in your deck.
    """
    assert keyword in KEYWORDS, "Specified keyword not found."
    @keyword_bias
    def keywordBias(card, deck)-> bool:
#         assert keyword in REGION_WORDS[deck.region]["Keywords"]|REGION_WORDS[deck.secondRegion]["Keywords"], "Randomly picked invalid word."
        allCardKeywords = set()
        for kw in card.keywords:
                allCardKeywords |= {kw}
        for kw in card.descriptionKeywords:
                allCardKeywords |= {kw}
        allDeckKeywords = defaultdict(int)
        for card in deck:
            for kw in card.keywords:
                allDeckKeywords[kw] += 1
        for card in deck:
            for kw in card.descriptionKeywords:
                allDeckKeywords[kw] += 1
        if keyword in allCardKeywords:
            return True
        elif allDeckKeywords[keyword] >= strength:
            return True
        else:
            return False
    return keywordBias

#Vocab Bias Maker, Soft bias for vocab word.
#Lower strength means higher bias; for example if the keyword was "Play", strength of 0 means all cards will be "Play".
@vocab_bias
def VBM(vocabWord: str = random.choice(VOCAB), strength: int = 3):
    """
    VBM('Vocab Word', strength) Soft bias. Specify the vocab word and strength of bias, default is a random vocab word and a strength of 3.
    Lower strength means higher bias; for example if the keyword was "Play", strength of 0 means all cards will be "Play".
    """
    assert vocabWord in VOCAB, "Specified vocab not found."
    @vocab_bias
    def vocabBias(card, deck)-> bool:
#         assert keyword in REGION_WORDS[deck.region]["Vocab"]|REGION_WORDS[deck.secondRegion]["Vocab"], "Randomly picked invalid word."
        #look at all keywords in cards
        vocabList = defaultdict(int)
        for card in deck:
            for vw in card.vocab:
                vocabList[vw] += 1
        for cardVW in card.vocab:
            if cardVW != vocabWord:
                if vocabList[cardVW] >= strength:
                    return False
        return True
    return vocabBias

#Stronger than VBM, hard bias.
#Strength is the minimum number of cards from the vocab word you want in your deck.
@vocab_bias
def NVBM(vocabWord: str = random.choice(VOCAB), strength: int = 7):
    """
    VBM('Vocab Word', strength) Soft bias. Specify the vocab word and strength of bias, default is a random vocab word and a strength of 7.
    Strength is the minimum number of cards from the vocab word you want in your deck.
    """
    assert vocabWord in VOCAB, "Specified vocab not found."
    @vocab_bias
    def vocabBias(card, deck)-> bool:
#         assert keyword in REGION_WORDS[deck.region]["Vocab"]|REGION_WORDS[deck.secondRegion]["Vocab"], "Randomly picked invalid word."
        #look at all keywords in cards
        vocabList = defaultdict(int)
        for card in deck:
            for vw in card.vocab:
                vocabList[vw] += 1
        if vocabWord in card.vocab:
            return True
        elif vocabList[vocabWord] >= strength:
            return True
        else:
            return False
    return vocabBias

#Cost Bias Maker, Soft bias towards cost.
#Allows cards lower than the card cost, but not higher
#Lower strength means higher bias; for example if the cost was 5, strength of 0 means all cards will be 5-cost.
@cost_bias
def CBM(cost: int = random.randint(1,8), strength: int = 3):
    """
    CBM(cost, strength)
    Soft bias towards cost, default is a random cost 1-8 and a strength of 3.
    Allows cards lower than the card cost, but not higher
    Lower strength means higher bias; for example if the cost was 5, strength of 0 means all cards will be 5-cost.
    """
    assert cost >= 0 and cost < 12, "Cost is not valid."
    @cost_bias
    def costBias(card, deck)-> bool:
        if card.cost >= cost:
            if deck.cardCostCount[cost] >= strength:
                return False
        return True
    return costBias

#Stronger than CBM, hard bias.
#Allows cards lower than the card cost, but not higher
#Strength is the minimum number of cards from the cost you want in your deck.
@cost_bias
def NCBM(cost: int = random.randint(1,8), strength: int = 7):
    """
    NCBM(cost, strength)
    Soft bias towards cost, default is a random cost 1-8 and a strength of 7.
    Allows cards lower than the card cost, but not higher
    Strength is the minimum number of cards from the cost you want in your deck.
    """
    assert cost >= 0 and cost < 12, "Cost is not valid."
    @cost_bias
    def costBias(card, deck)-> bool:
        if card.cost == cost:
            return True
        elif deck.cardCostCount[cost] >= strength:
            return True
        else:
            return False
    return costBias

@mixed
def MIX(g1, g2):
    """
    MIX('genre1', 'genre2')
    Takes in two genres and tries to make sure both are true.
    """
    @mixed
    def mixedGenre(card, deck) -> bool:
        if g1(card, deck) and g2(card, deck):
            return True
        elif g1(card, deck) or g2(card, deck):
            return random.choice([True, False])
        return False
    return mixedGenre

GENRES = [basicCheck, firstRegionBias, secondRegionBias, halfSplit, KBM(), RBM(), spellBias, unitBias, VBM(), CBM()]
OTHER =[MIX(lambda x: x, lambda y: y), NKBM(), NVBM(), NCBM()]
SIMPLE_GENRES = [basicCheck, firstRegionBias, secondRegionBias, halfSplit, spellBias, unitBias]
MAKER_GENRES = [KBM, RBM, VBM, CBM, MIX, NKBM, NVBM, NCBM]
ALL_GENRES = [basicCheck, firstRegionBias, secondRegionBias, halfSplit, KBM, RBM, spellBias, unitBias, VBM, CBM, MIX, NKBM, NVBM, NCBM]

if __name__ == '__main__':
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

#     Creates a deck object from an unfinished deck code.
    def fromUnfinishedDeck(deckCode: str, genres:list = [basicCheck], regions = None):
        cards = []
        if regions == None: tempRegion = set()
        for i in LoRDeck.from_deckcode(deckCode).cards:
            cards += [(i.count, i.card_code)]
            if regions == None:
                temp = i.faction
                if temp == "IO": temp = "Ionia"
                if temp == "SI": temp = "Shadow Isles"
                if temp == "DE": temp = "Demacia"
                if temp == "FR": temp = "Freljord"
                if temp == "NX": temp = "Noxus"
                if temp == "PZ": temp = "Piltover & Zaun"
                tempRegion |= {temp}
        if regions == None: regions = tempRegion
        rDeck = Deck(*regions, *genres)
        for i in cards:
            rDeck.cardOverride(i[1], i[0])
        return rDeck
        
# TESTING LINES
#     def testingScript(printBool: bool):
#         success, failure = 0, 0
#          
#         if printBool: print("\n\t\t/+/=====================================================[ Specific Test (Shadow Isles/ Ionia) ]=====================================================\+\ \n")
# # Test a deck with specifications
#         genres = [basicCheck, KBM("Ephemeral", 3), firstRegionBias]
#         myDeck = Deck("Shadow Isles", "Ionia", *genres)
#         if myDeck.fillDeck():
#             if printBool: myDeck.printDeckInfo()
#             success += 1
#         else:
#             failure += 1
#         print()
#         rCode = LoRDeck(myDeck.returnDeck())
#         print(rCode.encode())
#         del myDeck
#         if printBool: print("\n\t\t/+/=====================================================[ Mix Test (Demacia, Freljord) ]=====================================================\+\ \n")     
# # Test the MIX genre
#         genres = [basicCheck, MIX(CBM(4, 5), NKBM("Frostbite", 6))]
#         myDeck = Deck("Freljord", "Freljord", *genres)  
#         myDeck.cardOverride("She Who Wanders", 2)
#         myDeck.cardOverride("Tryndamere", 2)
#         myDeck.cardOverride("Braum", 2)
#         myDeck.cardOverride("Ashe", 2)     
#         if myDeck.fillDeck():
#             if printBool: myDeck.printDeckInfo()
#             success += 1
#         else:
#             failure += 1
#         print()
#         rCode = LoRDeck(myDeck.returnDeck())
#         print(rCode.encode())
#         del myDeck
#         if printBool: print("\n\t\t/+/=====================================================[ Partial Import Test (Shadow Isles, Ionia) ]=====================================================\+\ \n")     
# # Test a deck from an unfinished deck code
#         genres = [basicCheck, CBM(4, 5)]
#         myDeck = fromUnfinishedDeck("CEAQCAIFGUAQCAICBEAA", genres)  
#         if myDeck.fillDeck():
#             if printBool: myDeck.printDeckInfo()
#             success += 1
#         else:
#             failure += 1
#         print()
#         rCode = LoRDeck(myDeck.returnDeck())
#         print(rCode.encode())
#         del myDeck
#         if printBool: print("\n\t\t/+/=====================================================[ All Random Test ]=====================================================\+\ \n")
# # Test a deck with no specifications, filled in by randomness
#         genres = randomGenreList(GENRES)
#         if basicCheck not in genres: genres.append(basicCheck)
#         randomDeck = Deck(random.choice(REGIONS), random.choice(REGIONS), *genres)
#         if randomDeck.fillDeck():
#             if printBool: randomDeck.printDeckInfo()
#             success += 1
#         else:
#             failure += 1
#         print()
#         rCode = LoRDeck(randomDeck.returnDeck())
#         print(rCode.encode())
#         del randomDeck
#         return success, failure

#     successRate = defaultdict(int)
#     for tests in range(1):
#         k,v = testingScript(True)
#         successRate["Success"] += k
#         successRate["Failure"] += v
#     print(f"\nTesting finished with a { (successRate['Success']/(successRate['Success']+successRate['Failure']))*100 }% Success rate.\n")
#     
    print("Genres are given in the form of: \n\t[property]GenreName\n")
    print("GENRES:", end = " ")
    print( ["["+ i.property + "]" + i.__name__ for i in ALL_GENRES] )
    userGenres = []
    userInput = input("\nGive genre names from the list above. You cannot specify two genres of the same property.\nYou can 'stop' without adding anything for random genres. To see more info about a genre, type 'help {genre name}'\n")
    while userInput.lower() != 'stop':
        
        if userInput in [i.__name__ for i in SIMPLE_GENRES]:
            exec(f"""
if {userInput}.property in [i.property for i in userGenres]:
    print("Cannot add genre of the same type.")
else:
    userGenres += [{userInput}]
    print ('{userInput} added.')
                """)

        if userInput in [i.__name__ for i in MAKER_GENRES]:
            exec(f"print('['+{userInput}.property+']'+{userInput}.__doc__)")
            prevInput = userInput
            userInput = input("Please input this genre with the parameters as shown in the help menu.\n")
            try:
                assert prevInput in userInput, "Make sure the genre was spelled correctly and the parameters are correct."
                exec(f"""
if {userInput}.property in [i.property for i in userGenres]:
    print("Cannot add genre of the same type.")
else:
        userGenres += [{userInput}]
        print ('{userInput} added.')
                """)
            except Exception as report:
                print("Error: "+report)
                
        if userInput[:4] == "help":
            if userInput[4:] == "":
                print("To see more info about a genre use 'help {genre name}'")
            elif userInput[5:] in [i.__name__ for i in ALL_GENRES]:
                exec(f"print('['+{userInput[5:]}.property+']'+{userInput[5:]}.__doc__)")
        if userInput.lower() == "genres":
            print("Your Genres: "+ str(userGenres))
        if userInput.lower() == "genre list":
            print(["["+ i.property + "]" + i.__name__ for i in ALL_GENRES])
        userInput = input("\tPlease enter a valid genre from the list. Type 'genre list' to see the list of genres again. Type 'stop' to finish.\n")

    userRegions = []
    print("GENRES:", end = " ")
    print( [i for i in REGIONS] )
    userInput = input("\nGive region names from the list above. You can 'stop' without specifying anything to have random regions.'\n")
    while userInput.lower() != 'stop' and len(userRegions) < 3:
        if userInput in REGIONS:
            userRegions += userInput
                
        if userInput.lower() == "regions":
            print("Your Regions: "+ str(userRegions))
        if userInput.lower() == "region list":
            print([i for i in REGIONS])
        userInput = input("\tPlease enter a valid region from the list. Type 'region list' to see the list of regions again. Type 'stop' to finish.\n")
    
    userInput = input("How many times would you like to try and generate your deck? (1-10 times)\n")
    while True:
        try:
            if int(userInput) <= 10:
                numPulls = int(userInput)
                break
            else:
                raise ValueError
        except:
            userInput = input('Please specify a number 1-10.\n ')
    userInput = input("\n Would you like to see the deck info? (y/n)\n  ")
    if userInput[0].lower() == 'y':
        userBool = True
    else: userBool = False
    userInput = 'y'
    try:
        while userInput[0] == 'y':
            successRate = defaultdict(int)
            for i in range(numPulls):
                if len(userGenres) == 0:
                    userGenres = randomGenreList(GENRES)
                if basicCheck not in userGenres: userGenres.append(basicCheck)
                if len(userRegions) == 0:
                    userRegions.append(random.choice(REGIONS))
                    userRegions.append(random.choice(REGIONS))
                if len(userRegions) == 1:
                    userRegions.append(random.choice(REGIONS))
                userDeck = Deck(*userRegions, *userGenres)
                if userDeck.fillDeck():
                    if userBool:
                        print() 
                        userDeck.printDeckInfo()
                    rCode = LoRDeck(userDeck.returnDeck())
                    successRate["Success"] += 1
                else:
                    successRate["Failure"] += 1
                del userDeck
            print(f"\nTesting finished with a { (successRate['Success']/(successRate['Success']+successRate['Failure']))*100 }% Success rate.")
            if ((successRate['Success']/(successRate['Success']+successRate['Failure']))*100) == 0 and numPulls >= 6:
                print("\n\t This deck probably chose genres that are impossible to go together.")
            userInput = input("\t Would you like to try again with the same genres? (y/n)\n")
    except MemoryError:
        print("Sorry that's too much.")
        
# with open("deckCodes.txt", "w") as outfile:
#     print(os.path.dirname(os.path.abspath(__file__)))
#     print(os.path.realpath(outfile.name))
#     successRate = defaultdict(int)
#     genres = randomGenreList(GENRES)
#     for i in range(10):
#         if basicCheck not in genres: genres.append(basicCheck)
#         randomDeck = Deck(random.choice(REGIONS), random.choice(REGIONS), *genres)
#         if randomDeck.fillDeck():
#             rCode = LoRDeck(randomDeck.returnDeck())
#             outfile.write(rCode.encode() + "\n")
#             successRate["Success"] += 1
#         else:
#             successRate["Failure"] += 1
#         del randomDeck
#     print(f"\nTesting finished with a { (successRate['Success']/(successRate['Success']+successRate['Failure']))*100 }% Success rate.")
    