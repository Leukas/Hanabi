## MAS Hanabi Preliminary Report

### About Hanabi
Hanabi is a cooperative card game where the goal is for the players to get as most points as possible. Points are earned by playing cards in numerical order and matching in color. In our simplified version, cards can be Red, Green, or Blue, and are numbered 1, 2, or 3. Unlike most card games, players can see the other players' cards, but not their own. Each turn, a player can do one of three things: play a card on a stack, discard a card, or give a clue to one of the other players about their cards.

#### Playing a card
A player can choose one of their cards to play onto the stacks. If the card they choose isn't playable, then the card is discarded and the players lose a life. If all lives are lost, the game ends.

#### Discarding a card
A player can choose to discard one of their cards. This restores one clue token, which are used to give clues. The discarded cards are visible to all the players.

#### Giving a clue
A player can choose to give a clue to another player. The clue can be given about either the color or the number of the card. For example, a player can say to another player "You have 2 blues", and they can indicate the positions of the blue cards. Giving a clue uses up a clue token. 




### Modelling Knowledge in the Game

At every instance of the game, the  truth regarding the game state and the epistemics of the players are modelled as a Kripke model. The advantage of a constantly updating Kripke model is that we directly have access to all the higher order epistemics as long as the model is updated correctly. 

Another approach could be more syntactic where we define knowledge bases for each of the players, which represents the knowledge that they have. This needs to be designed with a bound in the number of epistemic operators in a formula. The approach that we take however, using Kripke models is much more complete in the epistemic sense. 

### Assumptions Regarding Agents

The players are modelled as perfectly rational agents in the sense of derivability in the S5 epistemic system. The Kripke models we consider are therefore S5 models where the accessibility relations for each of the players form an equivalence class. Real life agents while playing Hanabi even despite being perfectly rational do require some memory with respect to the clues they have given earlier. The rest of the information can be inferred from the board configuration. 

The agents are however not perfect agents since their behavior is modelled with strategies that we defined which are currently just simple heuristics. Therefore, the agents don't make ideal decisions in terms of optimal play for cooperative success. 

### Kripke Model

In the simplified game of Hanabi that we consider, there are three players. Each of the players get 3 cards. There are therefore a total of 18 cards, 6 cards for every player. The 6 cards for each color are such, that there are there are 3 one's, 2 two's and 1 three. 

The Kripke model is of the form ![Alt text](resources/eq1.svg). Each world s ![Alt text](./resources/eq2.svg) is of the form of a 9 tuple, which represents the possible hands for all the players (3 cards per player). The definition of the possible worlds encodes the atomic positions that are true in that possible world. A possible atomic proposition is : "the 2nd card in player 2's hand is a red 3". The accessibility relations ![Alt text](resources/eq3.svg) are defined for each of the respective players. Now ![Alt text](resources/eq4.svg) if, each of the other players hands are the same in both the states. This is in a way, the dual of distributed systems modelling, where the agent doesn't know what he has but can see all the other player's hands.

In the simulation of the game, we first randomly allot the hands to the players from the 18 card deck. We then initialize the Kripke model according to the given hands, keeping in mind the fact that each player can see the other players hands but not his own. Now, importantly the possible worlds represent not only 3 cards the player has, but the position of each of the cards in his hand. Therefore for a player's hand <a,b,c> is distinct from <b,a,c>. We initially thought of representing a person's hand as a combination rather than a permutation, however the game involves giving clues which are on cards in specific positions. Therefore, the idea was to be more inline with the hand configuration in the board game, even though it might be possible to model the game using possible words as nC<sub>3</sub> rather than nP<sub>3</sub>

The structure of the initial Kripke model consists of 3 equivalence classes. There is only one world that lies in the pairwise intersection of the three equivalence classes, and that world represents the actual true hand configuration for each player. 

### Model Updates

Throughout the game there are 4 ways due to which the knowledge of the players change. When the player discards a card, when they play a card, when they draw a new card from the deck and when they give a clue to another player either about a specific number or color. Usually drawing a card after playing or discarding a card is part of the same action, as each player always needs to have 3 cards in his hand. However here we separate them the action into subactions and have a respective model update for that subaction as they result in different epistemic changes. 

#### Discarding and Playing Card

Both discarding a card and playing a new card, result in the same outcome, i.e. all the players can see the card. Therefore both these actions are equivalent in the epistemic sense and are defined as one function. Importantly, only the knowledge of the player who plays or discards the card, changes. The possible words of the player who plays the card reduce. All the worlds where he didn't have that particular card, in that position of his hand are removed, and all the other contradictory information that is implicit from that action are taken into account. Let's say after the person play's the card, all the red card are either in the discard pile or the central stacks in the board, then the player knows that he cant have any red card and removed all the possible worlds where he does have a red card. 

#### Giving a Clue

When a player receives a clue, the model needs to know three things: the person who received the clue, the type of clue, and the clue information (e.g. if the clue is a color clue, the color may be red). A clue should only remove possible worlds since it does not change the state of the board (apart from lowering the number of clues left, which isn't in the model). Additionally, all worlds that will be removed must be accessible by the player receiving the clue, since the other players already know that player's hand, so they do not gain any first-order knowledge. Therefore, we check each world that is accessible to the player receiving the clue, and remove all worlds where the information given in the clue is incompatible with the world.

#### Drawing a card

Drawing a card is done after a card is discarded or played. This simply adds a card in the hand of the player who discarded or played a card. So, we must update every player's knowledge. For the players who are not receiving a new card, we simply get all their accessible worlds and replace the knowledge of the old card with the new card. For the player receiving a new card, we need to add new worlds. We get all of the player's accessible worlds as well as the player's knowledge of the cards left in the deck. Then for each accessible world, a world is added for each possible card left in the deck. For example in a simpler game, let a player only have 2 cards in their hand. If they know one card is a red, and the other is blue, then they have access to worlds: \{B1R1, B2R1, B3R1, ..., B3R3\}. If they discard the blue card, and draw a new card then their worlds will now be \{R1R1,R2R1,...,G3R3\}. 

#### Querying the Model

The Kripke model contains all the levels of knowledge about the other players hand's that they know. While defining strategies, we need to query the model regarding certain formulas for their validity. Therefore, this function just checks the validity of a certain formula in the model. Importantly, we make a model general checker, that can operate on any model and check the validity of any formula of certain form in that model.

### Strategies for each player

We've listed some heuristics that we're going to use for each of the possible actions. They are not complete at this stage, and we haven't yet decided how they are going to fit in with each other.

#### Giving clues

Clues about "save cards" are prioritized, that is, when a player receives a card that is unique (in our case it is either a 3 or a card whose other instances have all been discarded), that card has the highest priority for a clue.

#### Discard strategies

Cards that are given a clue about, are supposed to be played, unless it is certainly known that the card can be discarded (has already been played). A "chop card" (card with the highest priority to be discarded) is the oldest card about which a clue hasn't been given. We define the oldest card as the card that has been in the player's hand for the longest amount of time, and ties are broken the card on the right being older. 

#### Playing a card

If an agent knows a card is definitely playable, then they will play it. A card is playable when either the player knows exactly what the card looks like from the clues and the board configuration, or the partial knowledge about the card is consistent with the board (e.g. all the 1s have been played, and player has been given a clue about a 2, then the 2 can be played).
