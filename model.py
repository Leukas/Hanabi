# model.py
import itertools
import re
import numpy as np
import networkx as nx
from enum import Enum
import copy
import pickle
from card import Card

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


def convert_cards_to_node(cards):
	"""
	Converts [1,1,1] to '1,1,1'
	"""
	return ','.join(str(w) for w in cards)

def convert_node_to_cards(node):
	"""
	Converts '1,1,1' to [1,1,1]
	"""
	return list(map(int, node.split(',')))

class Model():
	def __init__(self, num_players, cards_per_player, player_hands, initialize=True, simple_model=True):
		print("Creating nodes...")
		self.graph = nx.MultiGraph()
		self.num_players = num_players
		self.cards_per_player = cards_per_player
		print("Nodes created.")
		if simple_model:
			self.initialize_simple_model(list(map(int,player_hands)))
		elif initialize:
			self.initialize_model(list(map(int,player_hands)))
		else:
			self.load_model('model.bin')
		print("Model initialized.")

	def load_model(self, filepath):
		file = open(filepath,'rb')
		self.graph = pickle.load(file)

	def initialize_simple_model(self, hands):
		"""
		Hands = 9 number array following CardDigit
		"""

		for p_idx in range(0,self.num_players):
			card_deck = self.remove_known_cards(p_idx, list(map(int,hands)))
			# get all n-card combinations for each players
			perms = itertools.permutations(card_deck, self.cards_per_player)			
			perms = set(list(perms))
			worlds = []
			for p in perms:
				world = hands[0:p_idx*self.cards_per_player] + list(p) + hands[(p_idx+1)*self.cards_per_player:]
				world = convert_cards_to_node(world)

				# if the hand combination doesnt exist in the model, add it to the model
				# if another player has already added the world into the model, dont add it
				if world not in self.graph.nodes:
					self.graph.add_node(world)
				
				# if more than 1 player can access the same world, still need to add those edges into the graph
				worlds.append(world)

			self.connect_nodes(worlds, p_idx)
		self.add_self_loops()

	def initialize_model(self, hands):
		"""
		Hands = 9 number array following CardDigit
		"""
		card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 #+ [G2]*2 #+ [G3] #+ [B1]*3 + [B2]*2 + [B1]
		perms = itertools.permutations(card_deck, self.cards_per_player*self.num_players)
		perms = set(list(perms))
		perms = np.array(list(perms))
		# perms = np.unique(perms)
		for i, p in enumerate(perms):
			# if i %100000 == 0:
			# break
			world = convert_cards_to_node(p)
			self.graph.add_node(world)


			# if world not in self.graph.nodes:	
				# self.graph.add_node(world)


		for p_idx in range(0,self.num_players):
			print('P',p_idx)
			for node1 in self.graph.nodes:
				n1 = self.convert_node_to_cards(node1)
				n1 = n1[0:p_idx*self.cards_per_player]+n1[(p_idx+1)*self.cards_per_player:]
				for node2 in self.graph.nodes:
					n2 = self.convert_node_to_cards(node2)
					n2 = n2[0:p_idx*self.cards_per_player]+n2[(p_idx+1)*self.cards_per_player:]
					if (n1 == n2):
						if p_idx == 0:
							self.graph.add_edge(node1,node2,p0=1)
						elif p_idx == 1:
							self.graph.add_edge(node1,node2,p1=1)
						elif p_idx == 2:		
							self.graph.add_edge(node1,node2,p2=1)

		output_file = open('model.bin', mode='wb')
		pickle.dump(self.graph, output_file)
		output_file.close()
		print("Done initialising")
			# player_visible_worlds = np.concatenate((perms[:,0:p_idx*self.cards_per_player],perms[:,(p_idx+1)*self.cards_per_player:]), axis=1)
			# _, idxs = np.unique(player_visible_worlds, return_index=True, axis=0)
			# mask = np.ones(perms.shape[0])
			# mask[idxs] = 0
			# mask = mask.astype(bool)
			# non_unique_ones = perms[mask]
			# player_visible_worlds = player_visible_worlds[mask]

			# for p in perms:

		# for p_idx in range(0,self.num_players):
		# 	# card_deck = self.remove_known_cards(p_idx, list(map(int,hands)))
		# 	# get all n-card combinations for each players
		# 	perms = set(list(perms))
		# 	worlds = []
		# 	for p in perms:
		# 		world = hands[0:p_idx*self.cards_per_player] + list(p) + hands[(p_idx+1)*self.cards_per_player:]
		# 		world = convert_cards_to_node(world)

		# 		# if the hand combination doesnt exist in the model, add it to the model
		# 		# if another player has already added the world into the model, dont add it
		# 		if world not in self.graph.nodes:
		# 			self.graph.add_node(world)
				
		# 		# if more than 1 player can access the same world, still need to add those edges into the graph
		# 		worlds.append(world)

		# 	self.connect_nodes(worlds, p_idx)
		# self.add_self_loops()

	def add_self_loops(self):
		self.graph.add_edges_from(list(zip(self.graph.nodes,self.graph.nodes)), p0=1)
		self.graph.add_edges_from(list(zip(self.graph.nodes,self.graph.nodes)), p1=1)
		self.graph.add_edges_from(list(zip(self.graph.nodes,self.graph.nodes)), p2=1)

	def get_visible_hands(self, hands, player_idx):
		return hands[0:player_idx*self.cards_per_player] + hands[(player_idx+1)*self.cards_per_player:]

	def get_player_hand(self, hands, player_idx):
		return hands[player_idx*self.cards_per_player:(player_idx+1)*self.cards_per_player]

	def get_accessible_nodes_from_world(self, player_num, world):
		assert isinstance(world,str), 'World must be a string.'
		player_edges = nx.get_edge_attributes(self.graph, 'p' + str(player_num))

		accessible_nodes = set()
		for i, edge in enumerate(player_edges):
			if edge[0] == world:
				accessible_nodes.add(edge[1])
			elif edge[1] == world:
				accessible_nodes.add(edge[0])
		return accessible_nodes 
	
	def update_discard_and_play(self, card, player_num, hand_idx, discard_pile, stacks, hands):
		# the card that is discarded is still in the player's hand at this point, but also in the discard pile			
		# update the knowledge for the player whose card is discarded 
		visible_hands = self.get_visible_hands(hands, player_num)

		# removing all nodes where the card is different
		for node_key in list(self.graph.nodes.keys()):
			# Skip nodes that are not accessible by player
			if (visible_hands != self.get_visible_hands(self.convert_node_to_cards(node_key),player_num)):
				continue

			split_keys = node_key.split(',')
			if (int(card) != int(split_keys[player_num*self.cards_per_player+hand_idx])):

				self.graph.remove_node(node_key)
			
	def update_draw_card(self, card, player_num, hand_idx, discard_pile, stacks, hands):
		# Hand is the old hand without the new card

		nodes_to_add = set()
		nodes_to_remove = set()

		for i in range(0,self.num_players):

			player_nodes = self.get_accessible_nodes_from_world(i,convert_cards_to_node(hands))
			if i == player_num:
				for n in player_nodes:
					nodes_to_remove.add(n)
					node = self.convert_node_to_cards(n)
					player_hand = self.get_player_hand(node, player_num)
					partial_state = player_hand[:hand_idx] + player_hand[hand_idx+1:]
					cards_left = self.left_in_deck(player_num, discard_pile, stacks, hands, partial_state)

					for c in cards_left:
						node[player_num*self.cards_per_player+hand_idx] = c
						node_to_add = convert_cards_to_node(node)
						nodes_to_add.add(node_to_add)
			else:
				# modifying the players knowledge who arent getting a new card
				# modifies only the index of the new card
				for n in player_nodes:
					nodes_to_remove.add(n)
					node = self.convert_node_to_cards(n)
					node[player_num*self.cards_per_player+hand_idx] = int(card)
					node = convert_cards_to_node(node)
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
		player_nodes = self.get_accessible_nodes_from_world(player_num, convert_cards_to_node(hands))
		player_hand = np.array(self.get_player_hand(hands, player_num))
		nodes_to_remove = []
		if clue[0] == 0: # NUMBER CLUE
			# indices where cards are equal to num
			player_hand_nums = np.array(list(map(Card.num_of_card,player_hand)))
			num_idxs = player_hand_nums==clue[1]
			not_num_idxs = player_hand_nums!=clue[1]
			for node in player_nodes:
				player_world_hand = self.get_player_hand(self.convert_node_to_cards(node), player_num)
				player_world_hand_nums = np.array(list(map(Card.num_of_card,player_world_hand)))
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
			for node in player_nodes:
				player_world_hand = self.get_player_hand(self.convert_node_to_cards(node), player_num)
				player_world_hand_colors = np.array(list(map(Card.color_of_card,player_world_hand)))
				if (player_hand_colors[color_idxs] != player_world_hand_colors[color_idxs]).any():
					nodes_to_remove.append(node)		
				# If Red clue, removes R1,R1,R1 if actual hand has 2 reds.
				if np.array(player_world_hand_colors[not_color_idxs] == np.array([clue[1]]*np.sum(not_color_idxs))).any():
					nodes_to_remove.append(node)


		self.graph.remove_nodes_from(nodes_to_remove)

	@staticmethod
	def break_it_like_you_hate_it(formula):
		formula = formula.replace('\n','')
		formula = formula.replace(' ','')
		formula = formula.replace('\r','')
		formula = formula.replace('\t','')
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
			elif par_depth == 0 and char == "M":
				op = "~"
				sub1 = "K" + formula[i+1] + "(~(" + formula[i+3:len(formula)-1] + "))"
				return op, sub1, sub2
			elif par_depth == 0 and char == "K":
				op = "K" + formula[i+1]
				sub1 = formula[i+3:len(formula)-1]
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
			worlds = worlds_of_strings(worlds)
			# Evaluate the query
			# Parse the atomic query
			for world in worlds:
				for i, ch in enumerate(query):
					if ch != '*':
						if ch != world[i]:
							return False		

			return True
		else:
			op, sub1, sub2 = self.break_it_like_you_hate_it(query)
			if op == '~':
				return not self.query_model(sub1, hands, worlds)
			elif op == "&":
				return self.query_model(sub1, hands, worlds) and self.query_model(sub2, hands, worlds)
			elif op == "|":
				return self.query_model(sub1, hands, worlds) or self.query_model(sub2, hands, worlds)
			elif op[0] == 'K':
				for world in worlds:
					nodes = self.get_accessible_nodes_from_world(int(op[1]), world)
					boo = True
					for node in nodes:
						boo = self.query_model(sub1, hands, [node])
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
				all_cards.append(len(stacks)*(col_idx)+num)

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
		
		self.add_self_loops()
			
	def connect_nodes(self, worlds, p):
		"""
		Adds accessibility relations for each player
		"""
		world_edges = itertools.combinations(worlds,2)
		# world_edges = itertools.combinations_with_replacement(worlds,2)

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
		card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3 + [G2]*2 + [G3] + [B1]*3 + [B2]*2 + [B3]
		for i in range(0, len(visible_cards)):
			if int(i/self.cards_per_player) == player_num:
				continue
			# will throw an error here if the deck configuration isn't possible
			if int(visible_cards[i]) != NC:
				del card_deck[card_deck.index(visible_cards[i])]
		return card_deck


# Not currently in use
def count_cards(card, discard_pile, stacks, hands):
	"""
	Returning the number of cards, colors, and numbers from what's seen on the board
	Hands = 6 value array not including the player's own cards
	"""
	all_cards = copy.deepcopy(hands)
	all_cards.extend(map(int,discard_pile))
	
	for col_idx in range(0,len(stacks)):
		for num in range(0,stacks[col_idx]):
			all_cards.append(self.cards_per_player*(col_idx)+num)

	num_card = all_cards.count(int(card))

	all_cards = np.array(all_cards).astype(np.int16)
	# removes any NC cards
	all_cards = all_cards[all_cards!=NC]

	num_color = len(all_cards[np.floor(all_cards/self.cards_per_player)==(card.color.value-1)])
	num_number = len(all_cards[all_cards%self.cards_per_player==(card.number-1)])

	return num_card, num_color, num_number

# Purely for testing purposes
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
	model.add_self_loops()
	# x = model.get_player_cliques(0, hands=list(map(int,g.board.player_hands)), worlds=model.graph.nodes)
	# x = model.get_player_cliques(1, hands=list(map(int,g.board.player_hands)), worlds=model.graph.nodes)
	# x = model.get_player_cliques(2, hands=list(map(int,g.board.player_hands)), worlds=model.graph.nodes)

	val = model.query_model("M0(**,B1,**,G3,R1,B1,B2,R2,R3)", list(map(int,g.board.player_hands)))#|(K2(B1,B3,B2,G3,R1,B1,B2,R2,R3))")
	# val = model.query_model("K2(B1,B3,B2,G3,R1,B1,B2,R2,R3)")
	print(val)




# Purely for testing purposes
def model_query_test():
	g = Game()
	hands_int = [B1,B3,B2,G3,R1,B1,B2,R2,R3]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))

	g.board.player_hands = hands
	
	model = Model(3,3, g.board.player_hands)

	val = model.query_model("K0(B*,**,**,G3,R1,B1,B2,R2,R3)", list(map(int,g.board.player_hands))) # true
	print(val)

# Purely for testing purposes
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
	model.add_self_loops()
	hand_format = convert_cards_to_node(list(map(int,g.board.player_hands)))
	print('acc nodes', model.get_accessible_nodes_from_world(2,hand_format))

	# print(list(map(int,g.board.player_hands)))

	# model.get_player_cliques(2,list(map(int,g.board.player_hands)))

	p_num = 1
	card_replaced = 'G3'
	card_that_replaces = 'R1'
	hand_index = 0

	print(worlds_of_strings(model.graph.nodes))
	model.update_discard_and_play(Card(string=card_replaced), player_num=p_num, hand_idx=hand_index, 
		discard_pile=[], stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	discard_pile = list(map(int,[Card(string='R1')]*1+[Card(string='R2')]*1
		+[Card(string='G1')]*2+[Card(string='G2')]*1+[Card(string='G3')]*0
		+[Card(string='B1')]*1+[Card(string='B2')]*0+[Card(string='B3')]*0))


	print(worlds_of_strings(model.graph.nodes))
	NUMBER_CLUE = 0
	COLOR_CLUE = 1


	RED = 1
	GREEN = 2
	BLUE = 3

	# model.update_clue(player_num=2, clue=(COLOR_CLUE,RED), hands=list(map(int,g.board.player_hands)))
	model.update_draw_card(card=Card(string=card_that_replaces), player_num=p_num, hand_idx=hand_index, discard_pile=discard_pile, stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	g.board.player_hands[p_num*self.cards_per_player+hand_index]=Card(string=card_that_replaces)

	print(worlds_of_strings(model.graph.nodes))
	# # model.get_player_cliques(0, model.graph.nodes)




def main():
	# simple_model_query_test()
	# model_query_test()
	# model_update_test()
	# "K0(~p)" agent 0 knows p is false
	# "~K0(p)" agent 0 doesn't know p is true
	g = Game()
	hands_int = [B1,B3,B2,G3,R1,B1,B2,R1,R3]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))

	g.board.player_hands = hands

	model = Model(3,3, g.board.player_hands)

if __name__ == '__main__':
	from player import *
	main()
# --- Model --
# State construction
# 
#
#

