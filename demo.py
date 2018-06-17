# demo.py
from model import *
from player import Game
from card import *

NUMBER_CLUE = 0
COLOR_CLUE = 1
RED = 1
GREEN = 2
BLUE = 3

def demo():
	g, model = init2()
	# step1_demo(g, model)

	p_num = 1
	card_replaced = 'G1'
	card_that_replaces = 'R2'
	hand_index = 1

	print_accessiblity_stuff(g, model)
	# print('nodes', model.graph.nodes)
	# print(worlds_of_strings(model.graph.nodes))
	# model.update_discard_and_play(Card(string=card_replaced), player_num=p_num, hand_idx=hand_index, 
		# discard_pile=[], stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	discard_pile = list(map(int,
		[Card(string='R1')]*0+[Card(string='R2')]*0+[Card(string='R3')]*0+
		[Card(string='G1')]*1+[Card(string='G2')]*2+[Card(string='G3')]*1+
		[Card(string='B1')]*3+[Card(string='B2')]*2+[Card(string='B3')]*1))

	# print_accessiblity_stuff(g, model)

	# print(worlds_of_strings(model.graph.nodes))
	# print('nodes', model.graph.nodes)

	model.update_clue(player_num=1, clue=(NUMBER_CLUE,3), hands=list(map(int,g.board.player_hands)))
	# model.update_draw_card(card=Card(string=card_that_replaces), player_num=p_num, hand_idx=hand_index, discard_pile=discard_pile, stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	
	# g.board.player_hands[p_num*model.cards_per_player+hand_index]=Card(string=card_that_replaces)
	# hand_format = model.convert_cards_to_node(list(map(int,g.board.player_hands)))

	print_accessiblity_stuff(g, model)
	# print(hand_format)
	# print('nodes', model.graph.nodes)
	step2_demo(g, model)

def print_accessiblity_stuff(g, model):
	hand_format = model.convert_cards_to_node(list(map(int,g.board.player_hands)))
	p0_acc = model.get_accessible_nodes_from_world(0,hand_format)
	p1_acc = model.get_accessible_nodes_from_world(1,hand_format)
	p2_acc = model.get_accessible_nodes_from_world(2,hand_format)
	print('p0_acc', worlds_of_strings(p0_acc))
	print('p1_acc', worlds_of_strings(p1_acc))
	print('p2_acc', worlds_of_strings(p2_acc))


def init():
	g = Game(initialize_model=False)
	hands_int = [G1,G3,G2,R1,R1,R1,B1,B1,B1]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))
	g.board.player_hands = hands
	model = Model(3,2, g.board.player_hands,initialize=False)
	hand_format = model.convert_cards_to_node(list(map(int,g.board.player_hands)))
	acc = model.get_accessible_nodes_from_world(1,hand_format)
	# print(worlds_of_strings(acc))
	return g, model

def init2():
	g = Game(initialize_model=False)
	hands_int = [R1,R2,R3,G1,G1,G1]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))
	g.board.player_hands = hands
	model = Model(3,2, g.board.player_hands, initialize=False)
	hand_format = model.convert_cards_to_node(list(map(int,g.board.player_hands)))
	acc = model.get_accessible_nodes_from_world(1,hand_format)
	# print(worlds_of_strings(acc))
	return g, model

def step1_demo(g, model):
	# print(g.board.player_hands)
	queries = []
	queries.append("R*,*2,R*,G*,*1,**") # T
	queries.append("K1(R1,R2,**,**,G1,G1)") # T
	queries.append("K1(**,**,R3,G1,**,**)") # F
	queries.append("K0(~(**,G1,**,**,**,**))") # T
	queries.append("M0(**,G1,**,**,**,**)") # F
	queries.append("M2(M1(**,**,G1,G1,**,**))") # T
	queries.append("M0(M1(**,**,G1,G1,**,**))") # F
	queries.append("M0(M2(M1(**,**,G1,G1,**,**)))") # T
	queries.append("M2(M0(M1(**,**,G1,G1,**,**)))") # T
	queries.append("M0(M1(M0(**,**,G1,G1,**,**)))") # F
	queries.append("K0(K1(M0(**,**,G1,G1,**,**)))") # F
	queries.append("K1((~(**,**,G1,G1,**,**))&(**,**,R2,R2,**,**))") # F


	queries.append("K0(R*,R*,**,**,**,**)") # T
	queries.append("K1(K0(R*,R*,**,**,**,**))") # F






	# Checks if player 0 knows what he can see, should be TRUE
	# queries.append("K0(**,**,**,R1,**,**,**,**,**)")
	# Checks if player 0 considers possible that there is a R1 in his hand, should be FALSE
	# queries.append("""((K0(R1,**,**,**,**,**,**,**,**))
		# |(K0(**,R1,**,**,**,**,**,**,**)))
		# |(K0(**,**,R1,**,**,**,**,**,**))""")
	# queries.append("""K2((K0(~(R1,**,**,**,**,**,**,**,**))
		# |(K0(~(**,R1,**,**,**,**,**,**,**))))
		# |(K0(~(**,**,R1,**,**,**,**,**,**))))""")
	# queries.append("""K2(K0(~(R1,**,**,**,**,**,**,**,**)))""")
	# queries.append("""K1(K0(~(R1,**,**,**,**,**,**,**,**)))""")
	# queries.append("K1(**,**,**,R1,R1,R1,**,**,**)")
	# Checks if player 1 knows that player 0 considers possible that he has an R1, should be FALSE
	# queries.append("K1(" + queries[1] + ")")
	# Checks if player 2 knows that player 0 considers possible that he has an R1, should be FALSE
	# queries.append("K2(" + queries[1] + ")")

	qs = []
	# hands = list(map(int,g.board.player_hands))
	# qs.append(model.query_model(queries[2], hands, [model.convert_cards_to_node(hands)]))

	hands = list(map(int,g.board.player_hands))
	for q in queries:

		qs.append(model.query_model(q, hands, [model.convert_cards_to_node(hands)]))

	# q1 = model.query_model("K0(B*,**,**,G3,R1,B1,B2,R2,R3)", list(map(int,g.board.player_hands))) # true
	# q1 = model.query_model("K0(B*,**,**,G3,R1,B1,B2,R2,R3)", list(map(int,g.board.player_hands))) # true
	# val = model.query_model("K0(~(R1,R1,R1,G3,R1,B1,B2,R2,R3))") # true
	# val = model.query_model("K0(R1,R1,R1,G3,R1,B1,B2,R2,R3)")

	# possibly useless
	# val = model.query_model("K1(K0(~(R1,R1,R1,NA,NA,NA,NA,NA,NA)))") # true 
	# val = model.query_model("K0(~(R1,R1,R1,NA,NA,NA,NA,NA,NA))") # true

	# val = model.query_model("K0(NA,NA,NA,G3,R1,B1,B2,R2,R3)")
	for i, q in enumerate(qs):
		print(queries[i])
		print(q)	
	# print(val)

def step2_demo(g, model):
	# print(g.board.player_hands)
	queries = []

	queries.append("K1(**,**,R3,**,**,**)") # T
	queries.append("K2(K1(**,**,R3,**,**,**))") # T

	# queries.append("K0(~(**,G1,**,**,**,**))") # T
	# queries.append("M0(**,G1,**,**,**,**)") # F
	# queries.append("M2(M1(**,**,G1,G1,**,**))") # T
	# queries.append("M0(M1(**,**,G1,G1,**,**))") # F
	# queries.append("M0(M2(M1(**,**,G1,G1,**,**)))") # T
	# queries.append("M2(M0(M1(**,**,G1,G1,**,**)))") # T

	# queries.append("K0(R*,R*,**,**,**,**)") # T
	# queries.append("K1(K0(R*,R*,**,**,**,**))") # F





	qs = []

	hands = list(map(int,g.board.player_hands))
	for q in queries:

		qs.append(model.query_model(q, hands, [model.convert_cards_to_node(hands)]))
	for i, q in enumerate(qs):
		print(queries[i])
		print(q)	




if __name__ == '__main__':
	demo()