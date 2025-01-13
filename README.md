# NoThanksGA
A simple genetic algorithm for an AI for the card game No Thanks!

This is a quick attempt at making a genetic AI for a two-player game of No Thanks! (aka Geschenkt!), designed by Thorsten Gimmler. A strategy for playing the game is encoded in a long (about 10MB) string of characters. Each one correpsonds to a certain game situation as measured by the difference in chips between you and your opponent, the value of the current card on offer, the number of cards left in the deck, and the distance that the given card is from connecting to an already chosen card for both you and your opponent. The string has one character corresponding to each possible combination of these parameters, which encodes the number of chips that must be on the card for the strategy to choose to take that card. Otherwise, the strategy says to place a chip if able. 

Each iteration of the genetic algorithm has a small chance to "evolve" the chip threshhold up or down by 1 for each possible situation, thereby mutating the strategy. Ideally the strategy will converge to a very good one in the long run, although, as the program is currently constituted, I believe the run time to get it to do so would be absurd.

Important functions/parameters in GameAndPlayer:

MUTATECHANCEUP/MUTATECHANCEDOWN - constants that control the chance of a mutation in either direction in the evolution process.
DECKTEST - controls the number of games an "offspring" plays against the previous best known algorithm to test if the new algorithm is "better". This probably needs to be higher than 10 to get good data on the evolutions. 

setupFirstFile(newfile) - Creates a file that holds a strategy based on a very basic heuristic (defined in makeBasicStrat()). This file can be the starting point for the evolution process. 

mutateProcess(oldfile,newfile,number) - This is the main wrapper function for the mutation process. It takes in the file oldfile that contains a new strategy, a string newfil which will be the name of the generated string, and number, which chooses the number of candidate mutations to test. The script generates DECKTEST instances of shuffled decks of cards for the game. The first mutated strategy plays against the original using each of those decks, and the total score differential is calculated to determine a winner. The second mutated strategy plays against the winner of the first set of games, etc. until the "last mutation standing" is outputted into the file newfile.

writeStratToFile/writeFileToStrat - these convert files containing a strategy to an array in memory containing that strategy, and vice versa.

NTGameHumanStrat(strat1) - this lets you play against a computer player whose decisions are governed by strat1. The prompts in the console should be answered with "y" to take the given card, or "n" to place a chip on the card.The game state should be outputted at each relevant point.
