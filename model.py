# model.py
import itertools
import re
import numpy as np
import networkx as nx
from enum import Enum
from player import *
import copy

NA = 45 # Card doesnt matter
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

card_dict = {'NA': 45 ,
'NC': -1,
'R1': 0,
'R2': 1,
'R3': 2,
'G1': 3,
'G2': 4,
'G3': 5,
'B1': 6,
'B2': 7,
'B3': 8}

card_dict_inv = {v: k for k, v in card_dict.items()}

def worlds_of_strings(nodes):
	'''
	Converts all worlds from number-string format to string-string format
	Ex: '0,0,0' to 'R1,R1,R1' for all worlds
	'''
	node_nums = []
	for node in nodes:
		node_nums.append(','.join(map(lambda x: str(card_dict_inv[int(x)]), node.split(','))))
	return node_nums

def worlds_of_numbers(nodes):
	'''
	Converts all worlds from string-string format to number-string format
	Ex: 'R1,R1,R1' to '0,0,0' for all worlds
	'''
	node_nums = []
	for node in nodes:
		node_nums.append(','.join(map(lambda x: str(card_dict[x]), node.split(','))))
	return node_nums

class Model():
	def __init__(self, num_players, cards_per_player, player_hands):
		print("Creating nodes...")
		self.graph = nx.MultiGraph()
		self.num_players = num_players
		self.cards_per_player = cards_per_player
		print("Nodes created.")
		self.initialize_model(list(map(int,player_hands)))
		print("Model initialized.")

	def initialize_model(self, hands):
		"""
		Hands = 9 number array following CardDigit
		"""
		for p_idx in range(0,self.num_players):
			card_deck = self.remove_known_cards(p_idx, self.get_visible_hands(hands, p_idx))
			# get all n-card combinations for each players
			perms = itertools.permutations(card_deck, self.cards_per_player)
			perms = set(list(perms))
			worlds = []
			for p in perms:
				world = hands[0:p_idx*self.cards_per_player] + list(p) + hands[(p_idx+1)*self.cards_per_player:]
				world = self.convert_cards_to_node(world)

				# if the hand combination doesnt exist in the model, add it to the model
				# if another player has already added the world into the model, dont add it
				if world not in self.graph.nodes:
					self.graph.add_node(world)
				
				# if more than 1 player can access the same world, still need to add those edges into the graph
				worlds.append(world)

			self.connect_nodes(worlds, p_idx)
			# self.add_self_loops()

	# def add_self_loops(self):
	# 	self.graph.add_edges_from(list(zip(self.graph.nodes,self.graph.nodes)), p0=1)
	# 	self.graph.add_edges_from(list(zip(self.graph.nodes,self.graph.nodes)), p1=1)
	# 	self.graph.add_edges_from(list(zip(self.graph.nodes,self.graph.nodes)), p2=1)

	def convert_cards_to_node(self, cards):
		return ','.join(str(w) for w in cards)

	def convert_node_to_cards(self, node):
		return list(map(int, node.split(',')))

	def get_visible_hands(self, hands, player_idx):
		return hands[0:player_idx*self.cards_per_player] + hands[(player_idx+1)*self.cards_per_player:]

	def get_player_hand(self, hands, player_idx):
		return hands[player_idx*self.cards_per_player:(player_idx+1)*self.cards_per_player]

	# def get_player_cliques(self, player_num, hands, worlds=None):
	# 	"""
	# 	Gets cliques of size > 1 and 1 for the specified player
	# 	"""
	# 	if worlds is None:
	# 		worlds = self.graph.nodes
	# 	player_edges = nx.get_edge_attributes(self.graph, 'p' + str(player_num))
	# 	player_edges = np.array(list(player_edges.keys()))
		
	# 	non_self_loop_idxs = np.argwhere(player_edges[:,0]!=player_edges[:,1]).flatten()
	# 	self_loop_idxs = np.argwhere(player_edges[:,0]==player_edges[:,1]).flatten()
		
	# 	non_self_player_edges = player_edges[non_self_loop_idxs].flatten()
	# 	self_player_edges = player_edges[self_loop_idxs].flatten()
		
	# 	non_self_player_nodes = set(list(non_self_player_edges[0::3]) + list(non_self_player_edges[1::3]))
	# 	self_player_nodes = set(list(self_player_edges[0::3]) + list(self_player_edges[1::3]))
	# 	self_player_nodes = self_player_nodes - non_self_player_nodes
	# 	true_node = self.convert_cards_to_node(hands)
	# 	non_self_player_nodes.add(true_node)
	# 	# print('player_nodes', non_self_player_nodes, player_num)
	# 	self_player_nodes -= {true_node}
	# 	return non_self_player_nodes, self_player_nodes

	def get_accessible_nodes_from_world(self, player_num, world):
		player_edges = nx.get_edge_attributes(self.graph, 'p' + str(player_num))

		accessible_nodes = set()
		for i, edge in enumerate(player_edges):
			if edge[0] == world:
				accessible_nodes.add(edge[1])
			elif edge[1] == world:
				accessible_nodes.add(edge[0])
		return accessible_nodes 
	
	# CHANGE THIS
	def get_accessible_nodes(self, player_num):
		player_edges = nx.get_edge_attributes(self.graph, 'p' + str(player_num))
		player_nodes = list(np.array(list(player_edges.keys())).flatten())
		# Remove every third element (insertion order from the multigraph)
		player_nodes = set(player_nodes[0::3] + player_nodes[1::3])
		return player_nodes

	def update_discard_and_play(self, card, player_num, hand_idx, discard_pile, stacks, hands):
		# the card that is discarded is still in the player's hand at this point, but also in the discard pile			
		# update the knowledge for the player whose card is discarded 
		visible_hands = self.get_visible_hands(hands, player_num)
		# card_count, color_count, number_count = count_cards(card, discard_pile, stacks, visible_hands)

		# removing all nodes where the card is different
		for node_key in list(self.graph.nodes.keys()):
			# Skip nodes that are not accessible by player
			if (visible_hands != self.get_visible_hands(self.convert_node_to_cards(node_key),player_num)):
				continue

			# player_card_count, player_color_count, player_number_count = count_cards(card, [], [], self.convert_node_to_cards(node_key[player_num*self.cards_per_player:(player_num+1)*self.cards_per_player]))
			split_keys = node_key.split(',')
			# print("sk_ind", split_keys[player_num*3+hand_idx])
			if (int(card) != int(split_keys[player_num*3+hand_idx])):
			# update player's knowledge about other cards
				# counting number of cards that are the same that the player considers possible in this world
				# removing 1 because the card hasnt been removed yet from their hand
				# or (card_count + player_card_count > 4-card.number)
				# update player's knowledge about colors
				# or (color_count + player_color_count > 6)
				# update player's knowledge about numbers 
				# or (number_count + player_number_count > (4-card.number)*3)):

				self.graph.remove_node(node_key)
			
	def update_draw_card(self, player_num, hand_idx, discard_pile, stacks, hands):
		# Hand is already updated with the new card drawn

		nodes_to_add = set()
		nodes_to_remove = set()

		for i in range(0,self.num_players):
			player_nodes = self.get_accessible_nodes(i)
			# print('player_nodes', player_nodes)
			if i == player_num:
				for n in player_nodes:
					nodes_to_remove.add(n)
					node = self.convert_node_to_cards(n)
					player_hand = self.get_player_hand(node, player_num)
					partial_state = player_hand[:hand_idx] + player_hand[hand_idx+1:]
					cards_left = self.left_in_deck(player_num, discard_pile, stacks, hands, partial_state)

					for c in cards_left:
						node[player_num*3+hand_idx] = c
						node_to_add = self.convert_cards_to_node(node)
						nodes_to_add.add(node_to_add)
			else:
				# modifying the players knowledge who arent getting a new card
				# modifies only the index of the new card
				card = hands[player_num*3+hand_idx]
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
			player_hand_nums = np.array(list(map(Card.num_of_card,player_hand)))
			num_idxs = player_hand_nums==clue[1]
			not_num_idxs = player_hand_nums!=clue[1]
			# print("Player's hand (numbers):", player_hand_nums)
			for node in player_nodes:
				player_world_hand = self.get_player_hand(self.convert_node_to_cards(node), player_num)
				player_world_hand_nums = np.array(list(map(Card.num_of_card,player_world_hand)))
				# print(num_idxs)
				# print("Possible nums:", player_world_hand_nums)
				if (player_hand_nums[num_idxs] != player_world_hand_nums[num_idxs]).any():
					nodes_to_remove.append(node)
				# If clue number 1, removes R1,R1,R1 if actual hand has 2 ones.
				if np.array(player_world_hand_nums[not_num_idxs] == np.array([clue[1]]*np.sum(not_num_idxs))).any():
					nodes_to_remove.append(node)
		else: # COLOR CLUE	
			# indices where cards are equal to num
			player_hand_colors = np.array(list(map(Card.color_of_card,player_hand)))
			color_idxs = player_hand_colors==clue[1]
			not_color_idxs = player_hand_colors!=clue[1]
			# print("Player's hand (colorbers):", player_hand_colors)
			for node in player_nodes:
				player_world_hand = self.get_player_hand(self.convert_node_to_cards(node), player_num)
				player_world_hand_colors = np.array(list(map(Card.color_of_card,player_world_hand)))
				# print(color_idxs)
				# print("Possible colors:", player_world_hand_colors)
				if (player_hand_colors[color_idxs] != player_world_hand_colors[color_idxs]).any():
					nodes_to_remove.append(node)		
				# If Red clue, removes R1,R1,R1 if actual hand has 2 reds.
				if np.array(player_world_hand_colors[not_color_idxs] == np.array([clue[1]]*np.sum(not_color_idxs))).any():
					nodes_to_remove.append(node)


		self.graph.remove_nodes_from(nodes_to_remove)

	@staticmethod
	def break_it_like_you_hate_it(formula):
		op = ""
		sub1 = ""
		sub2 = ""
		par_depth = 0
		for i in range(0,len(formula)):
			char = formula[i]
			if char == "(":
				par_depth += 1
			elif char == ")":
				par_depth -= 1
			elif par_depth == 0 and char == "K":
				op = "K" + formula[i+1]
				sub1 = formula[i+3:len(formula)-1]
				# print(op,sub1,sub2)
				return op, sub1, sub2
			elif par_depth == 0 and (char == "&" or char == "|"):
				op = char
				sub1 = formula[1:i-1]
				sub2 = formula[i+2:len(formula)-1]
				return op, sub1, sub2
			elif par_depth == 0 and  char == "~":
				op = char
				sub1 = formula[i+2:len(formula)-1]
				return op, sub1, sub2
	
	@staticmethod
	def check_formula_at_world(formula, world):
		"""
		"""

	def query_model(self, query, hands, worlds = None):
		"""
		Query is of form : (((K0(p)) | ((r) & (q))) | (~ (q))
		Example: Player 2 knows Player 1 has a red card
						K2(R1,R2,R3,NA,NA,NA,NA,NA,NC Batman)
		"""
		if worlds is None:
			worlds = self.graph.nodes

		# if there are no parentheses, then the query is atomic
		if '(' not in query:
			print('worlds:', worlds_of_strings(worlds))
			# Evaluate the query
			# Parse the atomic query
			query_cards = query.split(',')


			query_cards = list(map(lambda x: card_dict[x], query_cards))
			query_cards = np.array(query_cards)
			na_filter = np.argwhere(query_cards!=45).flatten()
			# print("NA filter",na_filter)
			query_cards = query_cards[na_filter]
			# print(query_cards)
			for world in worlds:
				world_cards = self.convert_node_to_cards(world)
				world_cards = np.array(world_cards)
				# print('cardz', query_cards, world_cards)
				# print(query_cards!=world_cards[na_filter])
				if (query_cards!=world_cards[na_filter]).any():
				# if (query_cards!=world_cards).any():
					return False
				# for i in range(0,len(query_cards)):
					# if query_cards[i] != NA:
						# if query_cards[i] != world_cards[i]:
							# return False
			return True
		else:
			op, sub1, sub2 = self.break_it_like_you_hate_it(query)#, worlds)
			if op == '~':
				return not self.query_model(sub1, hands, worlds)
			elif op == "&":
				return self.query_model(sub1, hands, worlds) and self.query_model(sub2, hands, worlds)
			elif op == "|":
				return self.query_model(sub1, hands, worlds) or self.query_model(sub2, hands, worlds)
			elif op[0] == 'K':
				# 1 world left: 
				#	Get all accessible nodes to agent 
				#	Check if formula is true in all these nodes 
				if len(worlds)==1:
					nodes = self.get_accessible_nodes_from_world(int(op[1]), worlds[0])

					# print('# acc nodes:',len(nodes))
					boo = True
					for node in nodes:
						boo = self.query_model(sub1, hands, [node])
						if not boo:
							return boo
					return boo
				# N worlds left:
				#	Check if the knowledge formula is true in all worlds
				else:
					boo = True
					player_acc_nodes = self.get_accessible_nodes(int(op[1]))
					for world in player_acc_nodes:
						# print('player world', world)
						boo = self.query_model(sub1, hands, [world])
						# print('aaaah you scared me', boo)
						if not boo:
							return boo
					return boo
			else:
				print("Oops, something went terribly wrong...")

	def left_in_deck(self, player_num, discard_pile, stacks, hands, partial_state):
		"""
		This takes into account the possible world(partial_state) and gets all 
		possible combinations of the possible hands. There is a longer way of doing 
		this by not taking partial_state into account; by simply taking all 
		combinations !

		Partial state is the n-1 cards that the player has that they arent discarding
		partial state is an int list
		"""
		all_cards = copy.deepcopy(hands)
		all_cards.extend(map(int,discard_pile))

		for col_idx in range(0,len(stacks)):
			for num in range(0,stacks[col_idx]):
				all_cards.append(3*(col_idx)+num)

		all_cards.extend(partial_state)
		# this works since all_cards contains hands as the first 9 entries
		cards_left = self.remove_known_cards(player_num, all_cards)
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
		
		# self.add_self_loops()
			
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

	def remove_known_cards(self, player_num, visible_cards):
		"""
		Removes all cards that player_num can see.
		"""
		# card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]
		card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]
		for i in range(0, len(visible_cards)):
			if int(i/3) == player_num:
				continue
			# will throw an error here if the deck configuration isn't possible
			if int(visible_cards[i]) != NC:	
				del card_deck[card_deck.index(visible_cards[i])]

		return card_deck



def count_cards(card, discard_pile, stacks, hands):
	"""
	Returning the number of cards, colors, and numbers from what's seen on the board
	Hands = 6 value array not including the player's own cards
	"""
	all_cards = copy.deepcopy(hands)
	all_cards.extend(map(int,discard_pile))
	
	for col_idx in range(0,len(stacks)):
		for num in range(0,stacks[col_idx]):
			all_cards.append(3*(col_idx)+num)

	num_card = all_cards.count(int(card))

	all_cards = np.array(all_cards).astype(np.int16)
	# removes any NC cards
	all_cards = all_cards[all_cards!=NC]

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


def simple_model_query_test():
	g = Game()
	hands_int = [B1,B3,B2,G3,R1,B1,B2,R2,R3]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))

	g.board.player_hands = hands

	model = Model(3,3, g.board.player_hands)
	model.graph = nx.MultiGraph()
	nodes = [
	'B1,B3,B2,G3,R1,B1,B2,R2,R3',
	# 'B1,B3,B2,G3,R1,B1,B2,R2,R3',
	# 'B1,B3,B2,G3,R1,B1,B2,R2,R3',
	'G1,B3,B2,G3,R1,B1,B2,R2,R3', # 0: G1
	'R1,B1,B2,G3,R1,B1,B2,R2,R3', # 0: R1

	'B1,B3,B2,G1,R1,B1,B2,R2,R3', # 3: G1
	'B1,B3,B2,R1,R1,B1,B2,R2,R3', # 3: R1

	'B1,B3,B2,G3,R1,B1,B1,R2,R3', # 6: B1
	'B1,B3,B2,G3,R1,B1,R1,R2,R3', # 6: R1

	]


	node_nums = []

	for node in nodes:
		node_nums.append(','.join(map(lambda x: str(card_dict[x]), node.split(','))))

	model.graph.add_nodes_from(node_nums)
	model.connect_nodes(node_nums[0:3], 0)
	model.connect_nodes([node_nums[0]]+node_nums[3:5], 1)
	model.connect_nodes([node_nums[0]]+node_nums[5:7], 2)
	# model.add_self_loops()
	# x = model.get_player_cliques(0, hands=list(map(int,g.board.player_hands)), worlds=model.graph.nodes)
	# print('cliques0', x)
	# x = model.get_player_cliques(1, hands=list(map(int,g.board.player_hands)), worlds=model.graph.nodes)
	# print('cliques1', x)
	# x = model.get_player_cliques(2, hands=list(map(int,g.board.player_hands)), worlds=model.graph.nodes)
	# print('cliques2', x)

	val = model.query_model("K1(K0(NA,B3,B2,G3,R1,B1,B2,R2,R3))", list(map(int,g.board.player_hands)))#|(K2(B1,B3,B2,G3,R1,B1,B2,R2,R3))")
	# val = model.query_model("K2(B1,B3,B2,G3,R1,B1,B2,R2,R3)")
	print(val)

def model_query_test():
	g = Game()
	hands_int = [B1,B3,B2,G3,R1,B1,B2,R2,R3]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))

	# print(g.board.player_hands)
	g.board.player_hands = hands
	# print(g.board.player_hands)
	
	# print(hands)
	model = Model(3,3, g.board.player_hands)

	val = model.query_model("K1(K0(NA,NA,NA,G3,R1,B1,B2,R2,R3))", list(map(int,g.board.player_hands))) # true
	# val = model.query_model("K0(~(R1,R1,R1,G3,R1,B1,B2,R2,R3))") # true
	# val = model.query_model("K0(R1,R1,R1,G3,R1,B1,B2,R2,R3)")

	# possibly useless
	# val = model.query_model("K1(K0(~(R1,R1,R1,NA,NA,NA,NA,NA,NA)))") # true 
	# val = model.query_model("K0(~(R1,R1,R1,NA,NA,NA,NA,NA,NA))") # true

	# val = model.query_model("K0(NA,NA,NA,G3,R1,B1,B2,R2,R3)")


	#|(K2(B1,B3,B2,G3,R1,B1,B2,R2,R3))")
	# val = model.query_model("K2(B1,B3,B2,G3,R1,B1,B2,R2,R3)")
	print(val)

def model_update_test():
	g = Game()
	hands_int = [B1,B3,B2,G3,R1,B1,B2,R1,R3]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))

	g.board.player_hands = hands

	model = Model(3,3, g.board.player_hands)
	model.graph = nx.MultiGraph()
	nodes = [
	'B1,B3,B2,G3,NC,B1,B2,R1,R3',
	'G1,B3,B2,G3,NC,B1,B2,R1,R3', # 0: G1
	'R1,B3,B2,G3,NC,B1,B2,R1,R3', # 0: R1

	'B1,B3,B2,G1,NC,B1,B2,R1,R3', # 3: G1
	'B1,B3,B2,R1,NC,B1,B2,R1,R3', # 3: R1

	'B1,B3,B2,G3,NC,B1,B1,G1,R3', # 6: B1
	'B1,B3,B2,G3,NC,B1,R1,G1,R3', # 6: R1
	]

	g.board.player_hands[4] = Card(Color.NO_COLOR, -1)
	node_nums = []

	for node in nodes:
		node_nums.append(','.join(map(lambda x: str(card_dict[x]), node.split(','))))

	model.graph.add_nodes_from(node_nums)
	model.connect_nodes(node_nums[0:3], 0)
	model.connect_nodes([node_nums[0]]+node_nums[3:5], 1)
	model.connect_nodes([node_nums[0]]+node_nums[5:7], 2)
	# model.add_self_loops()

	print(list(map(int,g.board.player_hands)))

	# model.get_player_cliques(2,list(map(int,g.board.player_hands)))

	p_num = 1
	card_replaced = 'G3'
	card_that_replaces = 'R1'
	hand_index = 0

	print(worlds_of_strings(model.graph.nodes))
	model.update_discard_and_play(Card(string=card_replaced), player_num=p_num, hand_idx=hand_index, 
		discard_pile=[], stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	discard_pile = list(map(int,[Card(string='R1')]*1+[Card(string='R2')]*2
		+[Card(string='G1')]*3+[Card(string='G2')]*1+[Card(string='G3')]*0
		+[Card(string='B1')]*1+[Card(string='B2')]*0+[Card(string='B3')]*0))

	g.board.player_hands[p_num*3+hand_index]=Card(string=card_that_replaces)

	print(worlds_of_strings(model.graph.nodes))
	NUMBER_CLUE = 0
	COLOR_CLUE = 1


	RED = 1
	GREEN = 2
	BLUE = 3

	# model.update_clue(player_num=2, clue=(COLOR_CLUE,RED), hands=list(map(int,g.board.player_hands)))
	model.update_draw_card(player_num=p_num, hand_idx=hand_index, discard_pile=discard_pile, stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))

	print(worlds_of_strings(model.graph.nodes))
	# # model.get_player_cliques(0, model.graph.nodes)




def main():
	# simple_model_query_test()
	model_query_test()
	# model_update_test()
	# "K0(~p)" agent 0 knows p is false
	# "~K0(p)" agent 0 doesn't know p is true

	# 
	# "K0 (~ (K0 p) & q)"

	# "K2(~)"

	# just_save_it = len(model.get_accessible_nodes(0))
	# card_num = Card.num_of_card(int(g.board.player_hands[1]))

	# g.board.player


	# model.update_clue(0, (0, card_num), list(map(int,g.board.player_hands)))
	# print("before clue (should be above after clue) what the fuck are you doing:", just_save_it)
	# print("after clue:", len(model.get_accessible_nodes(0)))

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


if __name__ == '__main__':
	main()
# --- Model --
# State construction
# 
#
#

