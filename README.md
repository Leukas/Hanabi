## MAS Hanabi Preliminary Report

### About Hanabi

Hanabi is a cooperative card game where the goal is for the players to get as most points as possible. Points are earned by stacking cards in numerical order and matching in suit. The original game considers five different suits (Red, Green, Blue, Yellow, White) and values from 1 to 5. There are 3 instances of the 1s cards, 2 instances of the 2,3,4s and 1 instance of the 5s. Unlike most card games, players can see the other players' cards, but not their own. This is where the cooperative aspect plays a major role, and the reason why this game is ideal for thinking about distributed knowledge. Each turn, a player can do one of three things: play a card on a stack, discard a card, or give a clue to one of the other players about their cards. Playing a card that is not valid will take a life. A card is not valid when it doesn't follow the numeric order in any of the stacks. The number of clues that the players can give is limited (the maximum amount of clues depends on the number of players). Every time a player discards a card, a clue is made available (up to the maximum). All players can see the cards once they are discarded, so it is possible to estimate the cards left in the deck based on the discarded pile, the other players' hands and the stacks.

In this project we implement a Kripke model to formalize knowledge and allow high order knowledge reasoning. Building such a model is resource intensive, and querying takes a very long time. Thus, we consider a simplified version of the game. In our simplified problem, cards can be either Red, Green, or Blue, and are numbered 1, 2, or 3. We only consider 3 players, and each player can have up to 2 cards in their hand.

#### Playing a card

A player can choose one of their cards to play onto the stacks. If the card they choose isn't playable, then the card is discarded and the players lose a life. If all lives are lost, the game ends.

#### Discarding a card

If there are no clues available, or the player knows that one of his cards is not useful (e.g. has already been played) he or she can choose to get rid of it. This restores one clue token up to the maximum number of tokens.

#### Giving a clue

A player can choose to give a clue to another player. The clue can be given about either the color or the number of the card. When a clue is given, all the cards which share the property of the clue are pointed out. For example, if player A has to Blues and one Red, and player B decides to give A a clue about the Red cards, he will say something like:  "You have 2 blues"; and then indicate the positions of the blue cards. Giving a clue uses up a clue token.

### Modelling Knowledge in the Game

At every instance of the game, the  truth regarding the game state and the epistemics of the players are modelled as a Kripke model. The advantage of a constantly updating Kripke model is that we directly have access to all the higher order epistemics as long as the model is updated correctly.

Another approach could be more syntactic where we define knowledge bases for each of the players, which represents the knowledge that they have. This needs to be designed with a bound in the number of epistemic operators in a formula. The approach that we take however, using Kripke models is much more complete in the epistemic sense.

### Assumptions Regarding Agents

The players are modelled as perfectly rational agents in the sense of derivability in the S5 epistemic system. The Kripke models we consider are therefore S5 models where the accessibility relations for each of the players form an equivalence class. Real life agents while playing Hanabi even despite being perfectly rational do require some memory with respect to the clues they have given earlier. The rest of the information can be inferred from the board configuration.

The agents are however not perfect agents since their behavior is modelled with strategies that we defined which are currently just simple heuristics. Therefore, the agents don't make ideal decisions in terms of optimal play for cooperative success.

### Kripke Model

In the simplified game of Hanabi that we consider, there are three players. Each of the players get 2 cards. There are therefore a total of 18 cards, 6 cards for every color. The 6 cards for each color are such, that there are there are 3 one's, 2 two's and 1 three.

The Kripke model is of the form ![Alt text](resources/eq1.svg). Each world s ![Alt text](./resources/eq2.svg) is of the form of a 6 tuple, which represents the possible hands for all the players (2 cards per player). The definition of the possible worlds encodes the atomic positions that are true in that possible world. A possible atomic proposition is : "the 2nd card in player 2's hand is a red 3". The accessibility relations ![Alt text](resources/eq3.svg) are defined for each of the respective players. Now ![Alt text](resources/eq4.svg) if, each of the other players hands are the same in both the states. This is in a way, the dual of distributed systems modelling, where the agent doesn't know what he has but can see all the other player's hands.

In the simulation of the game, we first randomly allot the hands to the players from the 18 card deck. We then initialize the Kripke model according to the given hands, keeping in mind the fact that each player can see the other players hands but not his own. Now, importantly the possible worlds represent not only 2 cards the player has, but the position of each of the cards in his hand. Therefore for a player's hand <a,b> is distinct from <b,a>. We initially thought of representing a person's hand as a combination rather than a permutation, however the game involves giving clues which are on cards in specific positions. Therefore, the idea was to be more inline with the hand configuration in the board game, even though it might be possible to model the game using possible words as nC<sub>3</sub> rather than nP<sub>3</sub>

The structure of the initial Kripke model consists of 3 equivalence classes. There is only one world that lies in the pairwise intersection of the three equivalence classes, and that world represents the actual true hand configuration for each player. 

Note: This kripke model is what we initially implemented, however it doesn't capture all the 2nd order knowledge. We discuss the newer and the correct initial model in later in "Reimplementation of the model". This model updates were defined taking this Kripke model into account and only work for 1st order knowledge. 

### Model Updates

Throughout the game there are 4 ways due to which the knowledge of the players change. When the player discards a card, when they play a card, when they draw a new card from the deck and when they give a clue to another player either about a specific number or color. Usually drawing a card after playing or discarding a card is part of the same action, as each player always needs to have 3 cards in his hand. However here we separate them the action into subactions and have a respective model update for that subaction as they result in different epistemic changes.

#### Discarding and Playing Card

Both discarding a card and playing a new card, result in the same outcome, i.e. all the players can see the card. Therefore both these actions are equivalent in the epistemic sense and are defined as one function. With respect to the first order knowledge, only the knowledge of the player who plays or discards the card, changes. The possible words of the player who plays the card reduce. All the worlds where he didn't have that particular card, in that position of his hand are removed, and all the other contradictory information that is implicit from that action are taken into account. Let's say after the person play's the card, all the red card are either in the discard pile or the central stacks in the board, then the player knows that he cant have any red card and removed all the possible worlds where he does have a red card. 

#### Giving a Clue

When a player receives a clue, the model needs to know three things: the person who received the clue, the type of clue, and the clue information (e.g. if the clue is a color clue, the color may be red). The type of the clue refers to whether its about a number or a color and the clue information refers to the specific number of color, the clue is about.  Consider a situation where player i receives a clue. Player i's knowledge about his possibilities changes; they are reduced. There is no change in the first order knowledge of the others players. We remove all the nodes for player i's accessible worlds from the real world where he considered cards in those positions which differ from the clue information.

#### Drawing a card

Drawing a card is done after a card is discarded or played. This simply adds a card in the hand of the player who discarded or played a card. So, we must update every player's knowledge. For the players who are not receiving a new card, we simply get all their accessible worlds and replace the knowledge of the old card with the new card. For the player receiving a new card, we need to add new worlds. We get all of the player's accessible worlds as well as the player's knowledge of the cards left in the deck. Then for each accessible world, a world is added for each possible card left in the deck. For example in a simpler game, let a player only have 2 cards in their hand. If they know one card is a red, and the other is blue, then they have access to worlds: \{B1R1, B2R1, B3R1, ..., B3R3\}. If they discard the blue card, and draw a new card then their worlds will now be \{R1R1,R2R1,...,G3R3\}. 

### Reimplementation of the model to capture higher order knowledge

The version of the model explained so far was constructed from the initial hand dealt. The motivation behind this was reducing the size of the model. However, this model doesn't properly capture higher order knowledge. To allow for these type of queries, we reimplemented the initialization of the model. In the new and final version, we are taking all permutations of the entire deck as possible worlds in the model, and connecting them for each of the players according to what they can see (similar to a distributed system). The older model had just one clique for each of the players, and they only shared the actual world. For the new version, each player has several cliques. The new implementation of the Kripke model supports all queries of any order of knowledge.

Since this flaw was caught late in the project, we didn't have enough time to update the model updates according to the reinitialised model. Thus, these updates are inconsistent and only make sense for the 1st order knowledge in the old model.  Instantiating the new model takes an extreme amount of time, since to connect the nodes we need to check for connections in the cartesian product of the nodes. Consequently, querying the model takes also a lot of exploring. Therefore we simplified the game and didn't implement strategies.

### Querying the Model

We implemented a simple formula parser, that can work with the operands `&,|,~,M,K`. In order to simplify this parsing, we make extensive use of parenthesis. Queries for binary operands should look like `(subformula1) operand (subformula2)` while queries for unary ones should look like `operand(subformula)`. Note that we only consider up to binary cases, so if one wants to have a more complex 'or', then something like this should be used: `(subformula1) | ((subformula2) | (subformula3))`. The epistemic operators must be followed by the agent the formula is being checked for: `K0, M2`. The `M(formula)` operator is implemented by expanding the operator to `~(K(~(formula)))`. In order to simplify queries, we allow for the use of wild cards. For example, for querying "agent 0 knows that he has a red card in the 0th position" could be expressed as `K0(R*,**,**,**,**,**)`. This way, we don't have to include all the possible combinations in the query. The wildcard '*' can be used for either color, number or both. Prior to evaluation, the query is not being checked for correctness, and syntactically wrong queries will result in unpredictable behaviour.

The query evaluation is implemented recursively, our leaf condition being the atomic formula. The worlds in which formulas must be checked are subsequently passed for each call. For example, for a formula of the type `K0(formula)`, initially the real world will be used for checking `formula`, but then the subsequent formula will be tested for each of the accessible worlds for 0 from the initial world.

### Python Implementation

#### card.py

card.py includes the Card class and Deck class.

##### Card

The Card class handles conversions from readable card text to other formats needed for the model.

##### Deck

The Deck class creates a deck of cards and handles drawing and shuffling. The Deck class was intended for use in simulating an entire game of Hanabi.

#### player.py

player.py includes the Player class, Board class, and Game class.

##### Player

The Player class is currently empty, as it was intended to handle strategies. For any future work, decide_action() can be made to handle a strategy, and give_clue, discard, and play_card can be used as wrappers for querying the model.

##### Board

The board class handles all components of the board, including the deck, players' hands, discard pile, stacks, and number of clues and lives left. discard_card, draw_card, and play_card are all used to update the board based on the players' actions, but they do not update the model.

##### Game

The Game class combines the players, board, and model. play_turn prompts the player for an action and updates the board and model based on the action. play_game runs through an entire game. Needs Player to be implemented to run.

#### model.py

model.py includes the model class, as well as some static helper and testing functions related to the model.
Implemented as a multigraph with the package [NetworkX](https://networkx.github.io/).

##### initialize_simple_model

Initializes a model with worlds and connections that work for first-order knowledge queries.

##### initialize_model

Initializes a reduced model for higher-order knowledge queries, using 9 of the 18 cards in the deck. The other 9 are assumed to be in the discard pile.

##### get_accessible_nodes_from_world

Gets all the worlds accessible to a player from a specific world.

##### update_discard_and_play

Updates the model after a card is discarded or played. The update requires the card being discarded, the player who is discarding, the index of the card in the player's hand, and the board state (discard pile, stacks, all players' hands).

##### update_draw_card

Updates the model after a card is drawn. This is done exclusively after update_discard_and_play. Requires the card drawn, the player and index of where the card will go, and the board state.

##### update_clue

Updates the model after a clue is given. Requires the player who is receiving the clue, and a clue that is either a number or color clue. A number clue looks like (0, 1) for a clue about the number 1. A color clue looks like (1, 1) for a clue about the color red, where red = 1, blue = 2, green = 3. 

##### break_it_like_you_hate_it

Implements query parsing. Breaks the original query into the operand, subformula1 and subformula2. Also expands Mi to ~ Ki ~ as explained above.

##### query_model

Recursive implementation of the parsed query. As inputs takes the query, the actual hand and the world(s) where the query has to be evaluated.

##### left_in_deck

Taking into account what the player_num sees, this function will return the cards that that player thinks are left in the deck.

##### reconnect_nodes

Model updates are implemented by deleting all edges and reconnecting the nodes after each update, to ensure consistency. This function will take care of that.

##### connect_nodes

Adds the actual edges to the NetworkX graph.

#### Instructions of how to execute code

To run the live demo, run "python demo.py"

#### Dependencies

Python 3.6,
NumPy,
NetworkX
