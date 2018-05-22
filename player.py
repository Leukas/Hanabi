# player.py
from card import *

class Action(Enum):
	CLUE = 1
	DISCARD = 2
	PLAY = 3

class Player():
	def __init__(self):
		pass 

	def decide_action(self):
		"""
		Returns: Action
		"""
		pass

	def give_clue(self, player, color, number):
		pass

	def discard(self, hand_idx):
		pass

	def play_card(self):
		pass

class Board():
	def __init__(self, deck_num_colors, deck_count_nums, 
		num_players, cards_per_player, num_clues, num_lives):
		self.deck = Deck(deck_num_colors, deck_count_nums)
		self.num_players = num_players
		self.cards_per_player = cards_per_player
		
		self.player_hands = []
		for i in range(0,num_players):
			self.player_hands.append(self.deck.draw(cards_per_player))
		
		self.discard_pile = []
		self.stacks = [0]*self.deck.num_colors
		self.num_clues = num_clues
		self.num_lives = num_lives

	def stacks_full(self):
		return self.stacks == [len(self.deck.count_nums)]*self.deck.num_colors

	def discard_card(self, player_num, hand_idx):
		card = self.player_hands[player_num*3+hand_idx]
		self.discard_pile.append(card)
		self.player_hands[player_num*3+hand_idx] = self.deck.draw()

class Game():
	def __init__(self, deck_num_colors=3, deck_count_nums=(3,2,1), 
		num_players=3, cards_per_player=3, num_clues=3, num_lives=3):
		self.board = Board(deck_num_colors,deck_count_nums,num_players,cards_per_player,num_clues,num_lives)
		self.players = [] 
		for i in range(0,num_players):
			self.players.append(Player())

		# self.model = Model()

	def play_turn(self):
		# should include that the last player who draws a card gets to play again 
		while self.board.num_lives > 0 and not self.board.stacks_full() and len(self.board.deck.deck)!=0:
			for i in range(0,self.num_players):
				# if discard, args will return the index of 
				action, args = players[i].decide_action()
				if action == CLUE:
					self.num_clues -= 1
					players[i].give_clue()
				elif action == DISCARD:
					self.num_clues += 1
					players[i].discard()
					self.board.discard_card(i, args)
				else:
					players[i].play_card()
					pass
			pass

if __name__ == '__main__':
	# d = Deck(3,(3,2,1))
	# b = Board(d)
	print(b.stacks_full())