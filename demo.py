# demo.py
from model import *
from player import Game
from card import *


def demo():
	game, model = init()
	step1_demo(game, model)

def init():
	g = Game(initialize_model=False)
	hands_int = [G1,G3,G2,R1,R1,R1,B1,B1,B1]
	hands = []
	colors = [0, Color.RED, Color.GREEN, Color.BLUE]
	for i in range(0,len(hands_int)):
		hands.append(Card(colors[Card.color_of_card(hands_int[i])],Card.num_of_card(hands_int[i])))
	g.board.player_hands = hands
	model = Model(3,3, g.board.player_hands)
	hand_format = model.convert_cards_to_node(list(map(int,g.board.player_hands)))
	acc = model.get_accessible_nodes_from_world(1,hand_format)
	# print(worlds_of_strings(acc))
	return g, model

def step1_demo(g, model):

	queries = []
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
	queries.append("K1(**,**,**,R1,R1,R1,**,**,**)")
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

if __name__ == '__main__':
	demo()