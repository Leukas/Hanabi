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

def num_of_card(card):
	return card % 3 + 1 # 1 - 3

def color_of_card(card):
	if card == -1:
		return -1
	return int(card / 3) + 1 # 1 - 3

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

	def get_player_hand(self, hands, player_idx):
		return hands[player_idx*self.cards_per_player:(player_idx+1)*self.cards_per_player]

	def get_accessible_nodes(self, player_num):
		# player_edges = nx.get_edge_attributes(self.graph, player_num)
		# print(player_num)
		player_edges = nx.get_edge_attributes(self.graph, 'p' + str(player_num))
		# print(len(self.graph.nodes))
		# print(list(self.graph.nodes.keys())[0])
		# print(self.graph.edges)
		# # print(self.graph.edges['0,0,0,0,0,0,0','0,0'])
		# print(len(player_edges))
		player_nodes = np.array(list(player_edges.keys()))
		player_nodes = set(list(player_nodes.flatten()))
		# print(len(player_nodes))
		return player_nodes

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
			player_nodes = get_accessible_nodes(player_num)
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
		self.reconnect_nodes(hands)



	def update_clue(self, player_num, clue, hands):
		"""
		player_num = player index of the person receivng the clue.
		clue = (x, y) x = {0,1}, y = {0,2}
			x = 0 if a number clue, 1 if a color clue
			y = 1,2,3 = 1,2,3 or = R,G,B

		"""		
		player_nodes = self.get_accessible_nodes(player_num)
		player_hand = np.array(self.get_player_hand(hands, player_num))
		nodes_to_remove = []
		if clue[0] == 0: # NUMBER CLUE
			# indices where cards are equal to num
			player_hand_nums = np.array(list(map(num_of_card,player_hand)))
			num_idxs = player_hand_nums==clue[1]
			print("Player's hand (numbers):", player_hand_nums)
			for node in player_nodes:
				player_world_hand = self.get_player_hand(self.convert_node_to_cards(node), player_num)
				player_world_hand_nums = np.array(list(map(num_of_card,player_world_hand)))
				# print(num_idxs)
				if (player_hand_nums[num_idxs] != player_world_hand_nums[num_idxs]).all():
					print("Possible nums:", player_world_hand_nums)
					nodes_to_remove.append(node)
		else: # COLOR CLUE	
			pass
			# player_hand_colors = np.array(list(map(color_of_card,player_hand)))
			# num_idxs = player_hand_colors==clue[1]
			# nodes_to_remove = []
			# for node in player_nodes:
			# 	player_world_hand = self.get_player_hand(self.convert_node_to_cards(node), player_num)
			# 	player_world_hand_colors = np.array(list(map(color_of_card,player_world_hand)))
			# 	if player_hand_colors[num_idxs] != player_world_hand_colors[num_idxs]:
			# 		nodes_to_remove.append(node)
		print(nodes_to_remove)
		self.graph.remove_nodes_from(nodes_to_remove)




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

	def reconnect_nodes(self, hands):
		"""
		Removes all previous edges, then reconnects them based on 
		current knowledge of other players' hands
		"""
		nodes = copy.deepcopy(self.graph.nodes)
		self.graph.clear()
		self.graph.add_nodes_from(nodes)
		for p in range(0,self.num_players):
			player_nodes = []
			for node in self.graph.nodes:
				visible_hands = self.get_visible_hands(hands, p)
				visible_world_hands = self.get_visible_hands(self.convert_node_to_cards(node), p)
				if visible_hands == visible_world_hands:
					player_nodes.append(node)
			self.connect_nodes(player_nodes, p)

			
	def connect_nodes(self, worlds, p):
		"""
		Adds accessibility relations for each player
		"""
		world_edges = itertools.combinations_with_replacement(worlds,2)
		if p == 0:
			self.graph.add_edges_from(world_edges, p0=1)
		elif p == 1:
			self.graph.add_edges_from(world_edges, p1=1)
		elif p == 2:
			self.graph.add_edges_from(world_edges, p2=1)



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
	# # print(g.board.player_hands[0].color)
	model = Model(3,3, g.board.player_hands)

	print(list(map(int,g.board.player_hands)))
	just_save_it = len(model.get_accessible_nodes(0))
	card_num = num_of_card(int(g.board.player_hands[1]))
	model.update_clue(0, (0, card_num), list(map(int,g.board.player_hands)))
	print("before clue (should be above after clue) what the fuck are you doing:", just_save_it)
	print("after clue:", len(model.get_accessible_nodes(0)))

	# print(model.graph.nodes.data())
	# model.graph.add_node('hi', value='x')
	# model.graph.nodes['hi']['value'] = 'y'
	# print(model.graph.nodes.data())
	# d = Deck(3,(3,2,1))
	# # cards = d.draw(3)
	# card = d.draw(1)[0]

	# c, n_c, n_n = count_cards(card,d.draw(3),[1,1,1],[0,0,0,1,1,1])
	# # print(card, int(card), c, all_c)
	# # print(list(map(int,cards)))
	# # print(card)
	# # print("Card:", c, "Color:",n_c ,"Number:",n_n)
	# G=nx.Graph()
	# G.add_path([1,2,3],player='blue')
	# G.add_path([1,2,3],color='red')
	# G.add_path([7,8,9],player='2')
	# G.add_path([7,8,9],player='3')

	# # p = 1
	# # G.add_edges_from([(7,8),(8,9)], attr_data={p:1})
	# # print([G[u][v]['color'] for u,v in G.edges()])

	# print(G.edges_iter())
	# color=nx.get_edge_attributes(G,'player')
	# player=nx.get_edge_attributes(G,'player')
	# p1=nx.get_edge_data(G,{p:1})
	# print(p1)
	

	# print(color)
	# print(player)
	# col = np.array(list(color.keys()))
	# col = set(list(col.flatten()))
	# nodes = copy.deepcopy(G.nodes)
	# print(nodes)
	# G.clear()
	# G.add_nodes_from(nodes)
	# # G = nx.Graph(G.nodes())
	# print(G.nodes)
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

