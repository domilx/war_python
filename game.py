import random
import time

# Define the ranks and suits
ranks = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
suits = ("hearts", "diamonds", "clubs", "spades")

# Create a deck of cards
deck = [(rank, suit) for rank in ranks for suit in suits]

# Shuffle the deck 
random.shuffle(deck)

# Split the deck into two hands
player1_hand = deck[:26]
player2_hand = deck[26:]

def card_comparison(p1_card, p2_card):
	return 1 if ranks.index(p1_card[0]) > ranks.index(p2_card[0]) else 2 if ranks.index(p1_card[0]) < ranks.index(p2_card[0]) else 0

def play_round(player1_hand, player2_hand):
	if not player1_hand or not player2_hand:
		return

	p1_card = player1_hand.pop(0)
	p2_card = player2_hand.pop(0)

	print(f"Player 1 plays: {p1_card[0]} of {p1_card[1]}")
	print(f"Player 2 plays: {p2_card[0]} of {p2_card[1]}")

	result = card_comparison(p1_card, p2_card)
	if result == 1:
		print("Player 1 wins the round!")
		player1_hand.extend([p1_card, p2_card])
	elif result == 2:
		print("Player 2 wins the round!")
		player2_hand.extend([p1_card, p2_card])
	else:
		print("It's a tie! Time for war!")
		war(player1_hand, player2_hand)

def war(player1_hand, player2_hand):
	if len(player1_hand) < 4 or len(player2_hand) < 4:
		print("A player does not have enough cards for war. Game over.")
		return

	p1_war_cards = [player1_hand.pop(0) for _ in range(4)]
	p2_war_cards = [player2_hand.pop(0) for _ in range(4)]

	print(f"Player 1's war card: {p1_war_cards[-1][0]} of {p1_war_cards[-1][1]}")
	print(f"Player 2's war card: {p2_war_cards[-1][0]} of {p2_war_cards[-1][1]}")

	result = card_comparison(p1_war_cards[-1], p2_war_cards[-1])
	if result == 1:
		print("Player 1 wins the war!")
		player1_hand.extend(p1_war_cards + p2_war_cards)
	elif result == 2:
		print("Player 2 wins the war!")
		player2_hand.extend(p1_war_cards + p2_war_cards)
	else:
		print("It's a tie again! Continuing the war...")
		player1_hand.extend(p1_war_cards[:-1])
		player2_hand.extend(p2_war_cards[:-1])
		war(player1_hand, player2_hand)
	return result

def play_game():
	while player1_hand and player2_hand:
		play_round(player1_hand, player2_hand)
		time.sleep(1)  # Add a delay to make the game more readable
		print(f"Player 1 has {len(player1_hand)} cards")
		print(f"Player 2 has {len(player2_hand)} cards")

	if player1_hand and not player2_hand:
		print("Player 1 wins the game!")
	elif player2_hand and not player1_hand:
		print("Player 2 wins the game!")
	else:
		print("The game is a draw due to round limit!")
	"""Main function to run the game."""

# Call the main function to start the game
play_game()
