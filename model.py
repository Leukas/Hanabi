# model.py
import itertools
import re
import numpy as np
import networkx as nx
from enum import Enum
from player import *
import copy

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
		self.initialize_model(list(map(int,player_hands)))
		print("Model initialized.")

	# def convert_hands(self, board_hands):
	# 	model_hands = []
	# 	for i in range(0, len(board_hands)):
	# 		model_hands.append((board_hands[i].color.value-1)*3+(board_hands[i].number-1))
		
	# 	return model_hands

	def initialize_model(self, hands):
		"""
		Hands = 9 number array following CardDigit
		"""
		for pl in range(0,self.num_players):
			card_deck = self.remove_known_cards(pl, hands)
			# get all n-card combinations for each players
			perms = itertools.permutations(card_deck, 3)
			perms = set(list(perms))
			worlds = []
			for p in perms:
				world = hands[0:pl*self.cards_per_player] + list(p) + hands[(pl+1)*self.cards_per_player:]
				# world = ','.join(str(w) for w in world)
				world = self.convert_cards_to_node(world)

				# if the hand combination doesnt exist in the model, add it to the model
				# if another player has already added the world into the model, dont add it
				if world not in self.graph.nodes:
					self.graph.add_node(world)
				
				worlds.append(world)

			self.connect_nodes(worlds, pl)
		# print(len(self.graph.nodes))

	def convert_cards_to_node(self, cards):
		return ','.join(str(w) for w in cards)

	def convert_node_to_cards(self, node):
		return list(map(int, node.split(',')))

	def get_visible_hands(self, hands, player_idx):
		return hands[0:player_idx*self.cards_per_player] + hands[(player_idx+1)*self.cards_per_player:]

	def update_discard_and_play(self, card, player_num, hand_idx, discard_pile, stacks, hands):
		# the card that is discarded is still in the player's hand at this point, but also in the discard pile			
		# update the knowledge for the player whose card is discarded 
		visible_hands = self.get_visible_hands(hands, player_num)
		card_count, color_count, number_count = count_cards(card, discard_pile, stacks, visible_hands)

		# removing all nodes where the card is different
		for node_key in list(self.graph.nodes.keys()):
			
			# Skip nodes that are not accessible by player
			if (visible_hands != self.get_visible_hands(self.convert_node_to_cards(node_key),player_num)):
				continue

			player_card_count, player_color_count, player_number_count = count_cards(card, [], [], self.convert_node_to_cards(node_key[player_num*3:(player_num+1)*3]))
			if (int(card) != node_key[player_num*3+hand_idx]
			# update player's knowledge about other cards
				# counting number of cards that are the same that the player considers possible in this world
				# removing 1 because the card hasnt been removed yet from their hand
				or (card_count + player_card_count > 4-card.number)
				# update player's knowledge about colors
				or (color_count + player_color_count > 6)
				# update player's knowledge about numbers 
				or (number_count + player_number_count > (4-card.number)*3)):
				self.graph.remove_node(node_key)
			

	def update_draw_card(self, card, player_num, hand_idx, discard_pile, stacks, hands):
		# Hand is now updated with new card
		nodes_to_add = set()
		nodes_to_remove = set()

		for i in range(0,self.num_players):
			player_edges = nx.get_edge_attributes(self.graph, player_num)
			player_nodes = np.array(list(player_edges.keys()))
			player_nodes = set(list(player_nodes.flatten()))
			if i == player_num:
				for n in player_nodes:
					nodes_to_remove.add(n)
					node = self.convert_node_to_cards(n)
					player_hand = node[player_num*3:(player_num+1)*3]
					partial_state = partial_state[:hand_idx] + player_hand[hand_idx+1:]
					cards_left = self.left_in_deck(player_num, discard_pile, stacks, hands, partial_state)

					for c in cards_left:
						player_hand[hand_idx] = c
						node = self.convert_cards_to_node(player_hand)
						nodes_to_add.add(node)
			else:
				for n in player_nodes:
					nodes_to_remove.add(n)
					node = self.convert_node_to_cards(n)
					node[player_num*3+hand_idx] = int(card)
					node = self.convert_cards_to_node(node)
					nodes_to_add.add(node)

		self.graph.remove_nodes_from(nodes_to_remove)
		self.graph.add_nodes_from(nodes_to_add)

				# Modify nodes for other players so that discarded card is now a new card




	def update_clue(self, agents):
		
		pass

	def left_in_deck(self, player_num, discard_pile, stacks, hands, partial_state):
		"""
		Partial state is the n-1 cards that the player has that they arent discarding
		partial state is an int list
		"""
		card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]
		all_cards = copy.deepcopy(hands)
		all_cards.extend(map(int,discard_pile))

		for col_idx in range(0,len(stacks)):
			for num in range(0,stacks[col_idx]):
				all_cards.append(3*(col_idx)+num)

		all_cards.extend(partial_state)

		cards_left = remove_known_cards(player_num, all_cards)
		return cards_left

	def reconnect_nodes(self):
		nodes = copy.deepcopy(self.graph.nodes)
		self.graph.clear()
		self.graph.add_nodes_from(nodes)
		for p in range(0,self.num_players):
			for node in self.graph.nodes:
				# TODO add edges back into graph
	def connect_nodes(self, worlds, p):
		"""
		Adds accessibility relations for each player
		"""
		world_edges = itertools.combinations_with_replacement(worlds,2)
		self.graph.add_edges_from(world_edges, player=p)



	def remove_known_cards(self, player_num, hands):
		"""
		Removes all cards that player_num can see from hands
		"""
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
	all_cards = copy.deepcopy(hands)
	all_cards.extend(map(int,discard_pile))
	
	for col_idx in range(0,len(stacks)):
		for num in range(0,stacks[col_idx]):
			all_cards.append(3*(col_idx)+num)


	num_card = all_cards.count(int(card))

	all_cards = np.array(all_cards).astype(np.int16)
	all_cards = all_cards[all_cards!=-1]

	num_color = len(all_cards[np.floor(all_cards/3)==(card.color.value-1)])
	num_number = len(all_cards[all_cards%3==(card.number-1)])

	return num_card, num_color, num_number

# NC = -1 # No Card
# R1 = 0
# R2 = 1
# R3 = 2
# G1 = 3
# G2 = 4
# G3 = 5
# B1 = 6
# B2 = 7
# B3 = 8

	# num_repeats = 0
	# for c in discard_pile:
	# 	if c == card:
	# 		num_repeats += 1
	# for stack in stacks:
	# 	pass


if __name__ == '__main__':
	g = Game()
	# print(g.board.player_hands[0].color)
	model = Model(3,3, g.board.player_hands)

	# print(model.graph.nodes.data())
	# model.graph.add_node('hi', value='x')
	# model.graph.nodes['hi']['value'] = 'y'
	# print(model.graph.nodes.data())
	d = Deck(3,(3,2,1))
	# cards = d.draw(3)
	card = d.draw(1)[0]

	c, n_c, n_n = count_cards(card,d.draw(3),[1,1,1],[0,0,0,1,1,1])
	# print(card, int(card), c, all_c)
	# print(list(map(int,cards)))
	# print(card)
	# print("Card:", c, "Color:",n_c ,"Number:",n_n)
	G=nx.Graph()
	G.add_path([1,2,3],color='red')
	color=nx.get_edge_attributes(G,'color')
	col = np.array(list(color.keys()))
	col = set(list(col.flatten()))
	nodes = copy.deepcopy(G.nodes)
	print(nodes)
	G.clear()
	G.add_nodes_from(nodes)
	# G = nx.Graph(G.nodes())
	print(G.nodes)
	# print(col)
	# for i in col:
	# 	print(i)
	# graph = nx.Graph()
	# graph.add_nodes_from(range(100), val="x")

	# key = list(graph.nodes.keys())[9]
	# print(key)
	# print(graph.nodes[graph.nodes%10==0])

	# a = [1,2,3,4]
	# b = model.convert_cards_to_node(a)
	# print(b)
	# a = set()
	# a.add(1)
	# a.add(1)
	# a.add(12)
	# print(a)

	# print(a%3)
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

