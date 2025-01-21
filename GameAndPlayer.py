import random
import numpy
import math
from functools import partial
open_utf8 = partial(open, encoding='UTF-8')

MINCARD = 3
MAXCARD = 35
PAYCHIP = 1 #numbers representing player decisions
TAKECARD = 0
DIFFRANGE = 23 #chip differential 
DOWNRANGE = 5 #widest range we check for cards below current card in hands
UPRANGE = 5 #widest range we check for cards above current card in hands
TIMERANGE = 24 #number of cards the game lasts
CARDRANGE = 33 #range of values the current card can have
MUTATECHANCEUP = .001 #chance of adding one to threshhold in mutating
MUTATECHANCEDOWN = .001 #chance of subtracting one from threshhold in mutating
CHIPOFFSET = 11 #Chip differential ranges from 0 to 22 is actually -11 to 11
RANGEOFFSET = 1 #range differential from 0 to 4 is actually 1 to 5
CARDOFFSET = 3 #card range from 0 to 32 is actually 3 to 35
CHIPTOTAL = 22
ENCODEARR = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","H","I","J","K","L","M"]
DECODEARR = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"A":10,"B":11,"C":12,"D":13,"E":14,"F":15,"G":16,"H":17,"I":18,"J":19,"K":20,"L":21,"M":22}
DECKTEST = 10
STARTCHIPS = 11

#generic Player class
class Player:
    #Basic initilization - empty hand, 11 chips, remember player number
    def __init__(self,n):
        self.hand = [0]
        self.chips = STARTCHIPS
        self.playerNo = n
    
    #take n chips
    def takechips(self,n):
        self.chips += n
        print("Player %d has %d chips." % (self.playerNo,self.chips))
    
    #pay 1 chip
    def losechip(self):
        self.chips -= 1
        print("Player %d has %d chips." % (self.playerNo,self.chips))
        
    #decide whether to give a chip or not
    def makedecision(self,gamestate):
        if random.randint(0,1) < .5:
            self.losechip()
            return PAYCHIP
        else:
            self.hand.append(gamestate["curCard"])
            self.takechips(gamestate["cardChips"])
            return TAKECARD
        
class humanPlayer(Player):
    #Basic initilization - empty hand, 11 chips, remember player number
    def __init__(self,n):
        super().__init__(n)
    
    def makedecision(self,gamestate):
        choice = ""
        while choice != "y" and choice != "n":
            print("Take the card? (y/n)")
            choice = input()
        if choice == "n" and self.chips > 0:
            self.losechip()
            return PAYCHIP
        else:
            self.hand.append(gamestate["curCard"])
            self.takechips(gamestate["cardChips"])
            return TAKECARD
        
    
def testMutations(basicStrat,number): #make number of strats, test them against the previous Gen in DECKTEST number of games - return the one that does the best.
    deckArr = [[]]*DECKTEST #make DECKTEST decks
    for deckNum in range(DECKTEST): #shuffle 10 fresh decks and put them in deckArr
        tempdeck = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
        random.shuffle(tempdeck)
        deckArr[deckNum] = tempdeck
    firstStrat = mutateStrat(basicStrat) #make the first strat
    firstScore = 0
    for gameNum in range(DECKTEST): #play first strat against the previous gen in all 10 games
        firstGame = NTGameStrats(basicStrat,firstStrat)
        firstGame.setDeck(deckArr[gameNum])
        while firstGame.deckCounter < 24:
            firstGame.playerMove()
            firstScore += firstGame.reportP1PointDiff() #total the score diff for the new strat
    bestScore = firstScore #this is the best strat we have so far
    bestStrat = firstStrat
    for stratnum in range(number-1): #repeat for the remaining mutated strats
        checkStrat = mutateStrat(basicStrat)
        checkScore = 0
        for gameNum in range(DECKTEST):
            checkGame = NTGameStrats(basicStrat,checkStrat)
            print("Game %s" % gameNum)
            input()
            checkGame.setDeck(deckArr[gameNum])
            while checkGame.deckCounter < 24:
                checkGame.playerMove()
                checkScore += firstGame.reportP1PointDiff()
        if checkScore > bestScore: #lower scores are better for P1, so worse for the new strat
            bestScore = checkScore
            bestStrat = checkStrat
    return bestStrat

def setupFirstFile(newfile):
    strat = makeBasicStrat()
    writeStratToFile(strat,newfile)

def mutateProcess(oldfile,newfile,number):
    oldStrat = writeFileToStrat(oldfile)
    newStrat = testMutations(oldStrat,number)
    writeStratToFile(newStrat,newfile)

def repeatMutate(filename,startnum,endnum,number):
    for index in range(startnum,endnum+1):
        mutateProcess("%s%d"%(filename,index),"%s%d"%(filename,index+1),number)
        

#def makeTwosStrat():  #Junk used for testing
#    blankstrat = numpy.empty((DIFFRANGE,DOWNRANGE,UPRANGE,DOWNRANGE,UPRANGE,TIMERANGE,CARDRANGE),dtype=int)
#    for diff in range(DIFFRANGE):
#        for myDown in range(DOWNRANGE):
#            for myUp in range(UPRANGE):
#                for themDown in range(DOWNRANGE):
#                    for themUp in range(UPRANGE):
#                        for cardNo in range(TIMERANGE):
#                            for cardVal in range(CARDRANGE):
#                                blankstrat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] = 2
#    return blankstrat

#set threshhold for the basic strat
def makeBasicStrat():
    blankstrat = numpy.empty((DIFFRANGE,DOWNRANGE,UPRANGE,DOWNRANGE,UPRANGE,TIMERANGE,CARDRANGE),dtype=int)
    for diff in range(DIFFRANGE):
        for myDown in range(DOWNRANGE):
            for myUp in range(UPRANGE):
                for themDown in range(DOWNRANGE):
                    for themUp in range(UPRANGE):
                        for cardNo in range(TIMERANGE):
                            for cardVal in range(CARDRANGE):
                                tempnum = myDown
                                if ((myDown == 0 or myUp == 0) and (themDown == 0 or themUp == 0)):
                                    tempnum = 0
                                elif (myDown ==0 or myUp == 0):
                                    tempnum = min(3,CHIPTOTAL-diff)
                                else:
                                    tempnum = min(math.floor((cardVal+MINCARD)/(1+(2.0-(2*cardNo/23.0)))),CHIPTOTAL)
                                blankstrat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] = tempnum
    return blankstrat                            

#store a strategy array as a file
def writeStratToFile(strat,fileName):
    f = open_utf8("%s.txt" % fileName, "a")
    tempstring = ""
    for diff in range(DIFFRANGE):
        for myDown in range(DOWNRANGE):
            for myUp in range(UPRANGE):
                for themDown in range(DOWNRANGE):
                    for themUp in range(UPRANGE):
                        for cardNo in range(TIMERANGE):
                            for cardVal in range(CARDRANGE):
                                tempNo = strat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal]
                                tempstring += ENCODEARR[tempNo]
    f.write(tempstring) 

#read a file and store it as a strat array
def writeFileToStrat(fileName):
    f = open_utf8("%s.txt" %fileName,"r")
    string = f.read()
    counter=0
    newStrat = numpy.empty((DIFFRANGE,DOWNRANGE,UPRANGE,DOWNRANGE,UPRANGE,TIMERANGE,CARDRANGE),dtype=int)
    for diff in range(DIFFRANGE):
        for myDown in range(DOWNRANGE):
            for myUp in range(UPRANGE):
                for themDown in range(DOWNRANGE):
                    for themUp in range(UPRANGE):
                        for cardNo in range(TIMERANGE):
                            for cardVal in range(CARDRANGE):
                                newStrat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] = DECODEARR[string[counter]]
                                counter+= 1
    return newStrat
                                
#mutate a strategy array - chance to shift each threshhold up or down by 1.
def mutateStrat(strat):
    newStrat = numpy.empty((DIFFRANGE,DOWNRANGE,UPRANGE,DOWNRANGE,UPRANGE,TIMERANGE,CARDRANGE),dtype=int)
    for diff in range(DIFFRANGE):
        for myDown in range(DOWNRANGE):
            for myUp in range(UPRANGE):
                for themDown in range(DOWNRANGE):
                    for themUp in range(UPRANGE):
                        for cardNo in range(TIMERANGE):
                            for cardVal in range(CARDRANGE):
                                randno = random.random()
                                if randno < MUTATECHANCEDOWN:
                                    newStrat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] = max(0,strat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] -1)
                                if randno > 1 - MUTATECHANCEUP:
                                    newStrat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] = min(22,strat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] +1)
                                else:
                                    newStrat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal] = strat[diff][myDown][myUp][themDown][themUp][cardNo][cardVal]
    return newStrat

#compare card to hand, return DOWNRANGE if distance to next lowest card is that or higher
def checkDown(hand,card):
    for check in range(1,DOWNRANGE): 
        if (card - check) in hand and card > MINCARD -1 + check: #make sure no false positives
            return check
    return DOWNRANGE

#compare card to hand, return UPRANGE if distance to next highest card is that or higher
def checkUp(hand,card):
    for check in range(1,UPRANGE):
        if (card + check) in hand:
            return check
    return UPRANGE

#create a new player whose decisions are bound by the given array
class stratPlayer(Player):
    def __init__(self,stratArray,n):
        Player.__init__(self,n)
        self.strat = stratArray
        
    def makedecision(self,gamestate):
        theCard = gamestate["curCard"]
        theChips = gamestate["cardChips"]
        theCounter = gamestate["deckCounter"]
        if self.chips ==0:   #if I have no chips, take the card.
            self.hand.append(theCard)
            self.takechips(theChips)
            return TAKECARD
        chipDiff = math.floor((2*self.chips - CHIPTOTAL - theChips)/2) #mychips minus theirs
        if self.playerNo ==1:
            opponentHand = gamestate["p2Hand"]
            myHand = gamestate["p1Hand"]
        else:
            opponentHand = gamestate["p1Hand"]
            myHand = gamestate["p2Hand"]
        myDown = checkDown(myHand,theCard)
        myUp = checkUp(myHand,theCard)
        themDown = checkDown(opponentHand,theCard)
        themUp = checkUp(opponentHand,theCard)
        thresh = self.strat[chipDiff + CHIPOFFSET][myDown - RANGEOFFSET][myUp - RANGEOFFSET][themDown - RANGEOFFSET][themUp - RANGEOFFSET][theCounter][theCard - CARDOFFSET]
        if(theChips >= thresh):
            self.hand.append(theCard)
            self.takechips(theChips)
            return TAKECARD
        else:
            self.losechip()
            return PAYCHIP #fix


class proceduralPlayer(Player):
    def makedecision(self,gamestate):
        theCard = gamestate["curCard"]
        theChips = gamestate["cardChips"]
        theCounter = gamestate["deckCounter"]
        if self.playerNo ==1:
            opponentHand = gamestate["p2Hand"]
            myHand = gamestate["p1Hand"]
        else:
            opponentHand = gamestate["p1Hand"]
            myHand = gamestate["p2Hand"]
        if ((theCard + 1) in myHand or (theCard -1) in myHand) and ((theCard + 1) in opponentHand or (theCard -1) in opponentHand) or ((theCard + 1) in myHand or (theCard -1) in myHand) and (theChips > 3 or (theChips + self.chips ==22)):
            self.hand.append(theCard)
            self.takechips(theChips)
            return TAKECARD #take the card if both players like it or if you like it and you got a couple chips or opponent is out of chips
        if ((theChips*(1+(2.0-theCounter/23.0)) > theCard) or (self.chips==0)): #assume chips are worth 3 to start and scale linearly down - take when value is good
            self.hand.append(theCard)
            self.takechips(theChips)
            return TAKECARD #take the card if you have to or got a lot of chips
        else:
            self.losechip()
            return PAYCHIP

class NTGame:
    def __init__(self):
        self.deck = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
        random.shuffle(self.deck)
        self.player1 = Player(1)
        self.player2 = Player(2)
        self.p1Cards = [0]
        self.p2Cards = [0]
        self.deckCounter = 0
        self.cardChips = 0
        self.curPlayer = 1
        
    def setDeck(self,stackedDeck):
        self.deck = stackedDeck
    
    def outputState(self):
        return {"curCard" : self.deck[self.deckCounter], "cardChips" : self.cardChips, "p1Hand": self.p1Cards, "p2Hand":self.p2Cards, "deckCounter":self.deckCounter}
    
    def cardToPlayer(self,n):
        self.cardChips = 0
        if n ==1 :
            self.p1Cards.append(self.deck[self.deckCounter])
        else :
            self.p2Cards.append(self.deck[self.deckCounter])
        self.deckCounter += 1
        self.curPlayer = n
        if self.deckCounter == TIMERANGE:
            self.endGame()
            
    def playerMove(self):
        print("Hand 1: %s. Hand 2: %s" % (self.p1Cards,self.p2Cards))
        print("Player 1 chips: %d. Player 2 chips: %d" % (self.player1.chips,self.player2.chips))
        print("Card is %d with %d chips. Asking Player %d what they do." % (self.deck[self.deckCounter],self.cardChips,self.curPlayer))
        if self.curPlayer == 1:
            temp = self.player1.makedecision(self.outputState())
        else:
            temp = self.player2.makedecision(self.outputState())
        if temp == PAYCHIP:
            self.cardChips += 1
            self.curPlayer = 3 - self.curPlayer
        else:
            self.cardToPlayer(self.curPlayer)

        
    def playGame(self):
        while(self.deckCounter < TIMERANGE):
            self.playerMove()
    
    
    def endGame(self):
        print("The game is over.")
        print("Player 1's hand is:")
        print(self.p1Cards)
        print("Player 2's hand is:")
        print(self.p2Cards)
        temp = 0
        for num in range(MINCARD,MAXCARD,1):
            if(num in self.p1Cards and not (num-1 in self.p1Cards)):
                temp += num
        print("Player 1 has %d points" % (temp - self.player1.chips))
        temp = 0
        for num in range(MINCARD,MAXCARD,1):
            if(num in self.p2Cards and not (num-1 in self.p2Cards)):
                temp += num
        print("Player 2 has %d points" % (temp - self.player2.chips))
        
    def reportP1PointDiff(self): #gives number of points that P1 exceeded P2 by.
        temp1 = 0
        for num in range(MINCARD,MAXCARD,1):
            if(num in self.p1Cards and not (num-1 in self.p1Cards)):
                temp1 += num
        temp1 -= self.player1.chips
        temp2 = 0
        for num in range(MINCARD,MAXCARD,1):
            if(num in self.p2Cards and not (num-1 in self.p2Cards)):
                temp2 += num
        temp2 -= self.player2.chips
        return temp1-temp2   #remember higher scores are worse!

class NTGameProcedural(NTGame):
    def __init__(self):
        NTGame.__init__(self)
        self.player1 = proceduralPlayer(1)
        self.player2 = proceduralPlayer(2)

class NTGameStrats(NTGame):
    def __init__(self,strat1,strat2):
        NTGame.__init__(self)
        self.player1 = stratPlayer(strat1,1)
        self.player2 = stratPlayer(strat2,2)
        
class NTGameHumanStrat(NTGame):
    def __init__(self,strat1):
        NTGame.__init__(self)
        self.player1 = stratPlayer(strat1,1)
        self.player2 = humanPlayer(2)
    