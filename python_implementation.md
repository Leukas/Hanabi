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
Implemented as a multigraph with the package NetworkX. https://networkx.github.io/

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
##### query_model
##### left_in_deck
##### reconnect_nodes
##### connect_nodes



For each file
	3 lines about each class

Model file:
	Update functions
		Update draw card takes a card, and player num, 
	Query functions "implemented here"
	Break it like you hate it
	left in deck
	get acc
	etc

Instructions of how to execute code
