# model.py
import itertools
import re
import networkx as nx
from enum import Enum
from player import *

class CardDigit(Enum):
	R1 = 0
	R2 = 1
	R3 = 2
	G1 = 3
	G2 = 4
	G3 = 5
	B1 = 6
	B2 = 7
	B3 = 8

class Model():
	def __init__(self, board):
		print("Creating nodes...")
		self.graph = nx.Graph()
		self.board = board
		# self.initialize_model()
		print("Nodes created.")

	def initialize_model(self, hands):
		"""
		Hands = 9 digit string following CardDigit
		"""
		for p in range(0,self.board.num_players):
			card_deck = remove_known_cards(p)
			combs = itertools.combinations(card_deck, 3)
			combs = set(list(combs))
			worlds = []
			for c in combs:
				world = hands[0:p*board.cards_per_player] + c + hands[(p+1)*board.cards_per_player:]
				world = ''.join(str(w) for w in world)
				if not self.graph.nodes[world]:
					self.graph.add_node(world)
					worlds.append(world)

			self.connect_nodes(worlds, p)


	def connect_nodes(self, worlds, p):
		world_edges = itertools.combinations(worlds,2)
		self.graph.add_edges_from(world_edges, player=p)



	def remove_known_cards(self, player_num):
		# card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]
		card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]

		for i in range(0, len(hands)):
			if (i/3) == player_num:
				continue
			del card_deck[card_deck.index(hands[i])]

		return card_deck



if __name__ == '__main__':
	g = Game()
	model = Model(g.board)
	# print(model.graph.nodes.data())
	model.graph.add_node('hi', value='x')
	model.graph.nodes['hi']['value'] = 'y'
	# print(model.graph.nodes.data())

	a = [1,2,3,4]
	# print(a[4:])
	# (?# print(re.sub(r'\[,\]','',a)))
	# print(''.join(str(b) for b in a))
	# b = itertools.combinations(a[0:3],2)
	# model.graph.add_edges_from(b, color='b')
	# print(model.graph.edges.data())

	# print(a.index(2))
	# print(set(list(b)))
# --- Model --
# State construction
# 
#
#

