# demo.py
from model import *
from player import Game
from card import *

NUMBER_CLUE = 0
COLOR_CLUE = 1
RED = 1
GREEN = 2
BLUE = 3

def live_demo():
	print("Possible cards: R1 x 3, R2 x 2, R3 x 1, G1 x 3")
	print("Give a starting hand with 6 of the possible cards:")
	hands = input()
	g, model = init2(hands)


	# higher_order_query_demo(g, model)
	print("Input a query:")	
	query = input()
	while query!= "exit":

		if query[0:5] =='query':
			higher_order_query_demo(g, model, q_idx=int(query[5:]))
		else:
			run_live_query(g, model, query)

		hand_format = convert_cards_to_node(list(map(int,g.board.player_hands)))
		input()
		print("----------------------------------")
		print("Actual hands:", worlds_of_strings([hand_format])[0])
		print("Cards left in deck: R1 x 2, R2 x 1" )

		print("Input a query:")
		query = input()


def run_live_query(g, model, query):
	# print(g.board.player_hands)
	hands = list(map(int,g.board.player_hands))
	evaluation = model.query_model(query, hands, [convert_cards_to_node(hands)])
	print("Query:", query, "evaluates to:", evaluation)




def demo():
	g, model = init()

	p_num = 0
	card_replaced = 'R1'
	card_that_replaces = 'R2'
	hand_index = 0

	step1_demo(g, model)
	# print_accessiblity_stuff(g, model)
	model.update_clue(player_num=0, clue=(NUMBER_CLUE,1), hands=list(map(int,g.board.player_hands)))
	step1_demo(g, model)
	# print('nodes', model.graph.nodes)
	# print(worlds_of_strings(model.graph.nodes))
	model.update_discard_and_play(Card(string=card_replaced), player_num=p_num, hand_idx=hand_index, 
		discard_pile=[], stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	discard_pile = list(map(int,
		[Card(string='R1')]*0+[Card(string='R2')]*0+[Card(string='R3')]*0+
		[Card(string='G1')]*0+[Card(string='G2')]*0+[Card(string='G3')]*0+
		[Card(string='B1')]*0+[Card(string='B2')]*0+[Card(string='B3')]*0))

	# print_accessiblity_stuff(g, model)

	# print(worlds_of_strings(model.graph.nodes))
	# print('nodes', model.graph.nodes)

	model.update_draw_card(card=Card(string=card_that_replaces), player_num=p_num, hand_idx=hand_index, discard_pile=discard_pile, stacks=[0,0,0], hands=list(map(int,g.board.player_hands)))
	g.board.player_hands[p_num*model.cards_per_player+hand_index]=Card(string=card_that_replaces)
	
	step1_demo(g, model)
	# hand_format = convert_cards_to_node(list(map(int,g.board.player_hands)))


	# print_accessiblity_stuff(g, model)
	# print(hand_format)
	# print('nodes', model.graph.nodes)

def print_accessiblity_stuff(g, model):
	hand_format = convert_cards_to_node(list(map(int,g.board.player_hands)))
	p0_acc = model.get_accessible_nodes_from_world(0,hand_format)
	p1_acc = model.get_accessible_nodes_from_world(1,hand_format)
	p2_acc = model.get_accessible_nodes_from_world(2,hand_format)
	print('p0_acc', worlds_of_strings(p0_acc))
	print('p1_acc', worlds_of_strings(p1_acc))
	print('p2_acc', worlds_of_strings(p2_acc))


def init():
	g = Game(initialize_model=False)
	hands_int = [R1,R1,G1,G1,B1,B1]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))
	g.board.player_hands = hands
	model = Model(3,2, g.board.player_hands, simple_model=True, initialize=False)
	hand_format = convert_cards_to_node(list(map(int,g.board.player_hands)))
	acc = model.get_accessible_nodes_from_world(1,hand_format)
	print("Actual hands:", worlds_of_strings([hand_format])[0])
	# print(worlds_of_strings(acc))
	return g, model

def init2(starting_hands):
	g = Game(initialize_model=False)
	if starting_hands != "":
		hands_int = convert_node_to_cards(worlds_of_numbers([starting_hands])[0])
	# print(hands_int)
	else:
		hands_int = [R1,R2,R3,G1,G1,G1]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))
	g.board.player_hands = hands
	model = Model(3,2, g.board.player_hands,simple_model=False, initialize=False)
	hand_format = convert_cards_to_node(list(map(int,g.board.player_hands)))
	acc = model.get_accessible_nodes_from_world(1,hand_format)
	print("Actual hands:", worlds_of_strings([hand_format])[0])
	card_deck = [R1]*3 + [R2]*2 + [R3] + [G1]*3

	for card in hands_int:
		del card_deck[card_deck.index(card)]
	# print(card_deck)
	print("Cards left in deck:", worlds_of_strings([convert_cards_to_node(card_deck)])[0] )
	# print(worlds_of_strings(acc))
	return g, model

def higher_order_query_demo(g, model, q_idx=None):
	# print(g.board.player_hands)
	queries = []
	# queries.append("K1(R1,R2,**,**,G1,G1)") # T
	# queries.append("K1(**,**,R3,G1,**,**)") # F
	# queries.append("K0(~(**,G1,**,**,**,**))") # T
	# queries.append("M0(**,G1,**,**,**,**)") # F
	queries.append("M1(**,**,G1,G1,**,**)") # F
	queries.append("M2(M1(**,**,G1,G1,**,**))") # T
	queries.append("M0(M1(**,**,G1,G1,**,**))") # F
	queries.append("M0(M2(M1(**,**,G1,G1,**,**)))") # T
	queries.append("M0(M1(M0(**,**,G1,G1,**,**)))") # F
	# queries.append("M2(M0(M1(**,**,G1,G1,**,**)))") # T
	queries.append("K0(M2(M0(M1(**,**,G1,G1,**,**))))") # T
	# queries.append("K0(K1(M0(**,**,G1,G1,**,**)))") # F
	# queries.append("K0(R*,R*,**,**,**,**)") # T
	# queries.append("K1(K0(R*,R*,**,**,**,**))") # F

	qs = []
	if q_idx is not None:
		queries = [queries[q_idx]]

	hands = list(map(int,g.board.player_hands))
	for q in queries:
		qs.append(model.query_model(q, hands, [convert_cards_to_node(hands)]))

	# if q_idx 
	for i, q in enumerate(qs):
		print("Query:", queries[i], "evaluates to:", q)


def step1_demo(g, model):
	queries = []

	queries.append("R1,*1,G1,G1,B*,B1") # F
	queries.append("K0(**,**,G1,G1,**,**)") # T
	queries.append("K0(*1,*1,**,**,**,**)") # F
	queries.append("M0(*2,R*,**,**,**,**)") # T
	# queries.append("M1(**,**,R2,R2,**,**)") # T
	queries.append("(M1(**,**,R2,R2,**,**))&(~(K0(*1,R*,**,**,**,**)))") # T

	qs = []

	hands = list(map(int,g.board.player_hands))
	for q in queries:

		qs.append(model.query_model(q, hands, [convert_cards_to_node(hands)]))
	for i, q in enumerate(qs):
		print("Query:", queries[i], "evaluates to:", q)
		# print(q)		


def step2_demo(g, model):
	# print(g.board.player_hands)
	queries = []

	queries.append("R1,*1,G1,G1,B*,B1") # T
	queries.append("K0(**,**,G1,G1,**,**)") # T
	queries.append("K0(*1,R*,**,**,**,**)") # F
	queries.append("M0(*2,R*,**,**,**,**)") # T
	# queries.append("M1(**,**,R2,R2,**,**)") # T
	queries.append("(M1(**,**,R2,R2,**,**))&(~(K0(*1,R*,**,**,**,**)))") # T

	# queries.append("K0(~(**,G1,**,**,**,**))") # T
	# queries.append("M0(**,G1,**,**,**,**)") # F


	qs = []

	hands = list(map(int,g.board.player_hands))
	for q in queries:

		qs.append(model.query_model(q, hands, [convert_cards_to_node(hands)]))
	for i, q in enumerate(qs):
		print("Query:", queries[i], "evaluates to:", q)
		# print(q)	




if __name__ == '__main__':
	# demo()
	live_demo()