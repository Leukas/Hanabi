# player.py
import numpy as np
from card import *
from model import *
from enum import IntEnum

class Action(IntEnum):
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
		return Action.DISCARD

	def give_clue(self, player, color, number):
		"""
		Returns a 
		"""
		pass

	def discard(self):
		return int(np.random.rand()*3)

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
			self.player_hands.extend(self.deck.draw(cards_per_player))
		
		self.discard_pile = []
		self.stacks = [0]*self.deck.num_colors
		self.num_clues = num_clues
		self.num_lives = num_lives

	def stacks_full(self):
		return self.stacks == [len(self.deck.count_nums)]*self.deck.num_colors

	def discard_card(self, player_num, hand_idx):
		"""
		Discards a card from the player's hand and puts it in the discard pile
		Adds a "no card" where the card is discarded
		"""
		card = self.player_hands[player_num*3+hand_idx]
		self.discard_pile.append(card)
		self.player_hands[player_num*3+hand_idx] = Card(-1, -1)
		return card

	def draw_card(self, player_num, hand_idx):
		card = self.deck.draw()[0]
		self.player_hands[player_num*3+hand_idx] = card
		return card

	def play_card(self, player_num, hand_idx):
		card = self.player_hands[player_num*3+hand_idx]
		if card.number == self.stacks[card.color-1] + 1:
			self.stacks[card.color-1] +=1
			self.player_hands[player_num*3+hand_idx] = Card(-1, -1)
		else: # If the play is wrong, then card is discarded
			self.num_lives -=1
			self.discard_card(player_num, hand_idx)
		return card

class Game():
	def __init__(self, deck_num_colors=3, deck_count_nums=(3,2,1), 
		num_players=3, cards_per_player=3, num_clues=3, num_lives=3):
		self.cards_per_player = cards_per_player

		self.board = Board(deck_num_colors,deck_count_nums,num_players,cards_per_player,num_clues,num_lives)
		self.players = [] 
		for i in range(0,num_players):
			self.players.append(Player())

		# self.model = Model(3,3, self.board.player_hands)

	def play_game(self):
		# should include that the last player who draws a card gets to play again 
		while self.board.num_lives > 0 and not self.board.stacks_full() and len(self.board.deck.deck)!=0:
			for i in range(0,self.num_players):
				self.play_turn(i)	

	def play_turn(self, player_num):
		# if discard, args will return the index of 
		action = self.players[player_num].decide_action()
		if action == Action.CLUE:
			self.board.num_clues -= 1
			# clue = players[player_num].give_clue()
			# TODO: EVERYTHING
			# UPDATE MODEL WITH CLUE
			# (0 or 1 for color or number,0-2 color/number idx, 0-2 player number)
		elif action == Action.DISCARD:
			self.board.num_clues += 1
			hand_idx = self.players[player_num].discard()					
			card_discarded = self.board.discard_card(player_num, hand_idx)

			self.model.update_discard_and_play(card_discarded, player_num, hand_idx, 
				self.board.discard_pile, self.board.stacks, list(map(int,self.board.player_hands)))
			card = self.board.draw_card(player_num, hand_idx)
			# update model again
		else: # action == PLAY CARD
			hand_idx = self.players[player_num].play_card()
			card_played = self.board.play_card(player_num, hand_idx)

			self.model.update_discard_and_play(card_played, player_num, hand_idx,
				self.board.discard_pile, self.board.stacks, list(map(int,self.board.player_hands)))
			card = self.board.draw_card(player_num, hand_idx)
			# update model again

if __name__ == '__main__':
	# d = Deck(3,(3,2,1))
	# b = Board(d)
	# print(b.stacks_full())
	g = Game()
	g.play_turn(0)
	# g.play_turn(1)
