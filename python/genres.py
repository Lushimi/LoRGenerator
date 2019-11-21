from classes import *

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

#Soft bias towards keyword.
#Lower strength means higher bias; for example if the keyword was ephemeral, strength of 0 means all cards will be ephemeral.
def KBM(keyword: str = random.choice(KEYWORDS), strength: int = 3):
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
def NKBM(keyword: str = random.choice(KEYWORDS), strength: int = 7):
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

#Soft bias for vocab word.
#Lower strength means higher bias; for example if the keyword was "Play", strength of 0 means all cards will be "Play".
def VBM(vocabWord: str = random.choice(VOCAB), strength: int = 3):
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
def NVBM(vocabWord: str = random.choice(VOCAB), strength: int = 7):
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

#Soft bias towards cost.
#Allows cards lower than the card cost, but not higher
#Lower strength means higher bias; for example if the cost was 5, strength of 0 means all cards will be 5-cost.
def CBM(cost: int = random.randint(1,8), strength: int = 3):
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
def NCBM(cost: int = random.randint(1,8), strength: int = 7):
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


def MIX(g1, g2):
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
ALL_GENRES = GENRES + OTHER

if __name__ == "__main__":
    print('Please run all testing from the main.py')