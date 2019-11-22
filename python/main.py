from lor_deckcodes import LoRDeck
import os.path
from genres import *

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
    def testingScript(printBool: bool):
        success, failure = 0, 0
         
        if printBool: print("\n\t\t/+/=====================================================[ Specific Test (Shadow Isles/ Ionia) ]=====================================================\+\ \n")
# Test a deck with specifications
        genres = [basicCheck, KBM("Ephemeral", 3), firstRegionBias]
        myDeck = Deck("Shadow Isles", "Ionia", *genres)
        if myDeck.fillDeck():
            if printBool: myDeck.printDeckInfo()
            success += 1
        else:
            failure += 1
        print()
        rCode = LoRDeck(myDeck.returnDeck())
        print(rCode.encode())
        del myDeck
        if printBool: print("\n\t\t/+/=====================================================[ Mix Test (Demacia, Freljord) ]=====================================================\+\ \n")     
# Test the MIX genre
        genres = [basicCheck, MIX(CBM(4, 5), NKBM("Frostbite", 6))]
        myDeck = Deck("Freljord", "Freljord", *genres)  
        myDeck.cardOverride("She Who Wanders", 2)
        myDeck.cardOverride("Tryndamere", 2)
        myDeck.cardOverride("Braum", 2)
        myDeck.cardOverride("Ashe", 2)     
        if myDeck.fillDeck():
            if printBool: myDeck.printDeckInfo()
            success += 1
        else:
            failure += 1
        print()
        rCode = LoRDeck(myDeck.returnDeck())
        print(rCode.encode())
        del myDeck
        if printBool: print("\n\t\t/+/=====================================================[ Partial Import Test (Shadow Isles, Ionia) ]=====================================================\+\ \n")     
# Test a deck from an unfinished deck code
        genres = [basicCheck, CBM(4, 5)]
        myDeck = fromUnfinishedDeck("CEAQCAIFGUAQCAICBEAA", genres)  
        if myDeck.fillDeck():
            if printBool: myDeck.printDeckInfo()
            success += 1
        else:
            failure += 1
        print()
        rCode = LoRDeck(myDeck.returnDeck())
        print(rCode.encode())
        del myDeck
        if printBool: print("\n\t\t/+/=====================================================[ All Random Test ]=====================================================\+\ \n")
# Test a deck with no specifications, filled in by randomness
        genres = randomGenreList(GENRES)
        if basicCheck not in genres: genres.append(basicCheck)
        randomDeck = Deck(random.choice(REGIONS), random.choice(REGIONS), *genres)
        if randomDeck.fillDeck():
            if printBool: randomDeck.printDeckInfo()
            success += 1
        else:
            failure += 1
        print()
        rCode = LoRDeck(randomDeck.returnDeck())
        print(rCode.encode())
        del randomDeck
        return success, failure

#     successRate = defaultdict(int)
#     for tests in range(10):
#         k,v = testingScript(True)
#         successRate["Success"] += k
#         successRate["Failure"] += v
#     print(f"\nTesting finished with a { (successRate['Success']/(successRate['Success']+successRate['Failure']))*100 }% Success rate.")
    savepath = os.getcwd()[:-7] + "\\src\\main\\resources\\"
    with open(os.path.join(os.path.expanduser('~'), savepath, "deckCodes.txt"), "w") as outfile:
        successRate = defaultdict(int)
        genres = randomGenreList(GENRES)
        for i in range(10):
            if basicCheck not in genres: genres.append(basicCheck)
            randomDeck = Deck(random.choice(REGIONS), random.choice(REGIONS), *genres)
            if randomDeck.fillDeck():
                rCode = LoRDeck(randomDeck.returnDeck())
                outfile.write(rCode.encode())
                successRate["Success"] += 1
            else:
                successRate["Failure"] += 1
        print(f"\nTesting finished with a { (successRate['Success']/(successRate['Success']+successRate['Failure']))*100 }% Success rate.")
        del randomDeck
    