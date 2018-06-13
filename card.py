# card.py
import numpy as np
import random 
from enum import IntEnum

class Color(IntEnum):
	NO_COLOR = -1
	RED = 1
	GREEN = 2
	BLUE = 3
	YELLOW = 4
	WHITE = 5
	RAINBOW = 6


class Card():
	def __init__(self, color, number):
		self.color = color
		self.number = number # 1 - 3
		# NO CARD = 
		# COLOR = -1
		# NUMBER = -1
		# INT VALUE = -1

	def __str__(self):
		return "Color: {}, Number: {}".format(self.color.name, self.number)

	def __eq__(self, x):
		return self.color==x.color and self.number==x.number

	def __int__(self):
		if self.color == -1:
			return -1
		else:
			return 3*(self.color.value-1)+(self.number-1)  
	
	@staticmethod
	def to_card(int_card):
		colors = [0, Color.RED, Color.GREEN, Color.BLUE]
		return Card(colors[Card.color_of_card(int_card)],Card.num_of_card(int_card))

	@staticmethod
	def num_of_card(card):
		if card == -1:
			return -1
		return card % 3 + 1 # 1 - 3
	
	@staticmethod
	def color_of_card(card):
		if card == -1:
			return -1
		return int(card / 3) + 1 # 1 - 3

class Deck():
	def __init__(self, num_colors, count_nums):
		# 6 reds, blues, greens
		# per color: 3 ones, 2 twos, 1 three
		# count_nums = (nx1) the count for all numbers
		self.deck = []
		self.num_colors = num_colors
		self.count_nums = count_nums	
		col = [Color.RED, Color.GREEN, Color.BLUE]
		for i in range(0,num_colors):
			for j in range(0,len(count_nums)):
				for k in range(0,count_nums[j]):
					self.deck.append(Card(col[i],k+1))

		self.shuffle()

	def draw(self, num_cards=1):
		cards = []
		for i in range(0,num_cards):
			if len(self.deck) == 0:
				cards.append(Card(-1,-1)) 
			cards.append(self.deck.pop())
		return cards

	def shuffle(self):
		random.shuffle(self.deck)



if __name__ == '__main__':
	d = Deck(3,(3,2,1))
	d.shuffle()
	print(d.draw())