# model.py
import itertools
import re
import networkx as nx
from enum import Enum
from player import *

NC = -1 # No Card
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
	def __init__(self, num_players, cards_per_player, player_hands):
		print("Creating nodes...")
		self.graph = nx.Graph()
		self.num_players = num_players
		self.cards_per_player = cards_per_player
		print("Nodes created.")
		self.initialize_model(self.convert_hands(player_hands))
		print("Model initialized.")

	def convert_hands(self, board_hands):
		model_hands = []
		for i in range(0, len(board_hands)):
			model_hands.append((board_hands[i].color.value-1)*3+(board_hands[i].number-1))
		
		return model_hands

	def initialize_model(self, hands):
		"""
		Hands = 9 number array following CardDigit
		"""
		for p in range(0,self.num_players):
			card_deck = self.remove_known_cards(p, hands)
			# get all n-card combinations for each players
			combs = itertools.combinations(card_deck, 3)
			combs = set(list(combs))
			worlds = []
			for c in combs:
				world = hands[0:p*self.cards_per_player] + list(c) + hands[(p+1)*self.cards_per_player:]
				world = ''.join(str(w) for w in world)


				# if the hand combination doesnt exist in the model, add it to the model
				if world not in self.graph.nodes:
					self.graph.add_node(world)
					worlds.append(world)

			self.connect_nodes(worlds, p)

	def update_discard(self, card, hand_idx, player_num, discard_pile, stacks, hands):
		for i in range(0, self.num_players):
			# the card that is discarded is still in the player's hand at this point, but also in the discard pile
			
			# update the knowledge for the player whose card is discarded 
			if i == player_num:

				# removing all nodes where the card is different
				for node_key in list(self.graph.nodes.keys()):
					if int(card) != node_key[player_num*3+hand_idx]:
						self.graph.remove_node(node_key)

				# update player's knowledge about other cards


			# update the other people's knowledge
			else:
				pass


	def update_partial_knowledge(self, agents):
		pass

	def update_common_knowledge(self):
		pass

	def connect_nodes(self, worlds, p):
		"""
		Adds accessibility relations for each player
		"""
		world_edges = itertools.combinations(worlds,2)
		self.graph.add_edges_from(world_edges, player=p)



	def remove_known_cards(self, player_num, hands):
	# card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]
		card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]

		for i in range(0, len(hands)):
			if (i/3) == player_num:
				continue
			del card_deck[card_deck.index(hands[i])]

		return card_deck



def count_cards(card, discard_pile, stacks, hands):
	"""
	Hands = 6 value array not including the player's own cards
	"""
	all_cards = hands
	all_cards.extend(map(int,discard_pile))
	for col_idx in range(0,len(stacks)):
		for num in range(0,stacks[col_idx]):
			all_cards.append(3*(col_idx)+num)



	return all_cards.count(int(card)), all_cards
	# return all_cards


	# num_repeats = 0
	# for c in discard_pile:
	# 	if c == card:
	# 		num_repeats += 1
	# for stack in stacks:
	# 	pass


if __name__ == '__main__':
	g = Game()
	print(g.board.player_hands[0].color)
	model = Model(3,3, g.board.player_hands)
	# print(model.graph.nodes.data())
	# model.graph.add_node('hi', value='x')
	# model.graph.nodes['hi']['value'] = 'y'
	# print(model.graph.nodes.data())
	# d = Deck(3,(3,2,1))
	# cards = d.draw(3)
	# card = d.draw(1)[0]
	# c, all_c = count_cards(card,d.draw(3),[1,1,1],[0,0,0,1,1,1])
	# print(card, int(card), c, all_c)
	# print(list(map(int,cards)))


	# graph = nx.Graph()
	# graph.add_nodes_from(range(100), val="x")
	# key = list(graph.nodes.keys())[9]
	# print(key)
	# print(graph.nodes[graph.nodes%10==0])

	# a = [1,2,3,4]
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

