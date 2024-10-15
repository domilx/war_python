import pygame
import random
import sys

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 71, 96  
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GOLD = (212, 175, 55)
VEGAS_GREEN = (1, 68, 33)
FLASH_COLOR = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("War Card Game")

# Clock
clock = pygame.time.Clock()

# Fonts
FONT_SMALL = pygame.font.SysFont('Arial', 20)
FONT_SYMBOL = pygame.font.SysFont('Arial', 36, bold=True)

# Define the ranks and suits
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
suit_colors = {'Hearts': RED, 'Diamonds': RED, 'Clubs': BLACK, 'Spades': BLACK}

# Create the deck
deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]
random.shuffle(deck)

# Split the deck into two players
player1_deck = deck[:26]
player2_deck = deck[26:]

# Card positions
player1_pos = (SCREEN_WIDTH // 4 - CARD_WIDTH // 2, SCREEN_HEIGHT - CARD_HEIGHT - 20)
player2_pos = (3 * SCREEN_WIDTH // 4 - CARD_WIDTH // 2, 20)
table_pos = (SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)

# Game states
game_over = False
winner = None

# Cards on the table
table_cards = []

# Animation variables
animation_in_progress = False
animation_start_time = 0 # milliseconds
animation_duration = 500  # milliseconds
animation_cards = []

# War flash effect
war_flash = False
war_flash_start = 0 # milliseconds
war_flash_duration = 300  # milliseconds

def draw_card_back(screen, x, y):
    # Draw the back of the card
    pygame.draw.rect(screen, GOLD, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=8)
    # Draw the card back design
    pygame.draw.circle(screen, BLACK, (x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2), 20, 2)
    pygame.draw.circle(screen, BLACK, (x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2), 10, 2)
    pygame.draw.line(screen, BLACK, (x + CARD_WIDTH // 2 - 15, y + CARD_HEIGHT // 2), (x + CARD_WIDTH // 2 + 15, y + CARD_HEIGHT // 2), 2)
    pygame.draw.line(screen, BLACK, (x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2 - 15), (x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2 + 15), 2)

def draw_card_face(screen, card, x, y, scale=1.0, opacity=255):
    # Draw the card face with rounded edges, scaling, and opacity
    card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(card_surface, (*WHITE, opacity), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    pygame.draw.rect(card_surface, (*BLACK, opacity), (0, 0, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=8)
    # Draw the rank and suit
    rank_text = FONT_SMALL.render(card['rank'], True, (*BLACK, opacity))
    suit_text = FONT_SMALL.render(suit_symbols[card['suit']], True, (*suit_colors[card['suit']], opacity))
    card_surface.blit(rank_text, (5, 5))
    card_surface.blit(suit_text, (CARD_WIDTH - 20, 5))
    # Draw the suit symbol in the center
    suit_center_text = FONT_SYMBOL.render(suit_symbols[card['suit']], True, (*suit_colors[card['suit']], opacity))
    suit_center_rect = suit_center_text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
    card_surface.blit(suit_center_text, suit_center_rect)
    # Apply scaling
    if scale != 1.0:
        card_surface = pygame.transform.smoothscale(card_surface, (int(CARD_WIDTH * scale), int(CARD_HEIGHT * scale)))
        x -= (CARD_WIDTH * scale - CARD_WIDTH) / 2
        y -= (CARD_HEIGHT * scale - CARD_HEIGHT) / 2
    screen.blit(card_surface, (x, y))

def draw():
    # Draw the Vegas-style table background
    screen.fill(VEGAS_GREEN)
    # Add a decorative pattern to the table
    pygame.draw.rect(screen, GOLD, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 5, border_radius=15)
    
    # Draw player decks
    if player1_deck:
        draw_card_back(screen, *player1_pos)
        p1_cards_text = FONT_SMALL.render(f"{len(player1_deck)} cards", True, WHITE)
        screen.blit(p1_cards_text, (player1_pos[0], player1_pos[1] - 25))
    else:
        p1_out_text = FONT_SMALL.render("No cards", True, WHITE)
        screen.blit(p1_out_text, (player1_pos[0], player1_pos[1] - 25))

    if player2_deck:
        draw_card_back(screen, *player2_pos)
        p2_cards_text = FONT_SMALL.render(f"{len(player2_deck)} cards", True, WHITE)
        screen.blit(p2_cards_text, (player2_pos[0], player2_pos[1] + CARD_HEIGHT + 5))
    else:
        p2_out_text = FONT_SMALL.render("No cards", True, WHITE)
        screen.blit(p2_out_text, (player2_pos[0], player2_pos[1] + CARD_HEIGHT + 5))

    # Draw cards on the table
    for card_info in table_cards:
        card = card_info['card']
        x = card_info['pos'][0]
        y = card_info['pos'][1]
        face_up = card_info['face_up']
        scale = card_info.get('scale', 1.0)
        opacity = card_info.get('opacity', 255)
        if face_up:
            draw_card_face(screen, card, x, y, scale=scale, opacity=opacity)
        else:
            draw_card_back(screen, x, y)
    
    # War flash effect
    global war_flash
    if war_flash:
        time_since_flash = pygame.time.get_ticks() - war_flash_start
        if time_since_flash < war_flash_duration + 200: 
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            alpha = 255 * (1 - time_since_flash / (war_flash_duration + 200))
            flash_surface.set_alpha(alpha)
            flash_surface.fill(FLASH_COLOR)
            screen.blit(flash_surface, (0, 0))
            war_text = FONT_SYMBOL.render("WAR!", True, BLACK)
            war_text_rect = war_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(war_text, war_text_rect)
        else:
            war_flash = False

    # Display game over message
    if game_over:
        winner_text = FONT_SYMBOL.render(f"{winner} wins the game!", True, WHITE)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(winner_text, winner_rect)

    pygame.display.flip()

def move_cards_animation(cards_info):
    global animation_in_progress, animation_start_time, animation_cards, animation_duration
    animation_in_progress = True
    animation_start_time = pygame.time.get_ticks()
    animation_duration = 500  # milliseconds
    animation_cards = []
    for info in cards_info:
        animation_cards.append({'start_pos': info['start_pos'], 'end_pos': info['end_pos'], 'card': info['card'], 'face_up': info['face_up'], 'pos': info['start_pos'], 'table_index': info.get('table_index'), 'action': info.get('action')})

def update_animation():
    global animation_in_progress
    if not animation_in_progress:
        return
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - animation_start_time
    t = min(elapsed_time / animation_duration, 1)
    for i, anim_card in enumerate(animation_cards):
        start_x, start_y = anim_card['start_pos']
        end_x, end_y = anim_card['end_pos']
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        anim_card['pos'] = (x, y)
        # Update the corresponding card in table_cards
        if anim_card.get('table_index') is not None:
            table_card = table_cards[anim_card['table_index']]
            table_card['pos'] = anim_card['pos']
            # Apply animations based on action
            action = anim_card.get('action')
            if action == 'win':
                # Scale up winning card
                scale = 1.0 + 0.2 * t
                table_card['scale'] = scale
            elif action == 'lose':
                # Fade out losing card
                opacity = 255 * (1 - t)
                table_card['opacity'] = opacity
    if t >= 1:
        animation_in_progress = False

def play_round():
    global animation_in_progress
    if not player1_deck or not player2_deck:
        return

    # Each player plays a card
    p1_card = player1_deck.pop(0)
    p2_card = player2_deck.pop(0)

    # Add cards to table
    table_cards.append({'card': p1_card, 'pos': player1_pos, 'face_up': False})
    table_cards.append({'card': p2_card, 'pos': player2_pos, 'face_up': False})

    # Animate cards moving to table simultaneously
    cards_to_animate = [
        {'start_pos': player1_pos, 'end_pos': (table_pos[0] - CARD_WIDTH // 2 - 10, table_pos[1]), 'card': p1_card, 'face_up': False, 'table_index': len(table_cards)-2},
        {'start_pos': player2_pos, 'end_pos': (table_pos[0] + CARD_WIDTH // 2 + 10, table_pos[1]), 'card': p2_card, 'face_up': False, 'table_index': len(table_cards)-1}
    ]
    move_cards_animation(cards_to_animate)
    while animation_in_progress:
        handle_events()
        update_animation()
        draw()
        clock.tick(FPS)

    # Flip the cards face up
    table_cards[-2]['face_up'] = True
    table_cards[-1]['face_up'] = True
    draw()
    pygame.time.wait(500)

    # Compare cards
    result = compare_cards(p1_card, p2_card)
    if result == 1:
        # Player 1 wins the round
        # Animate winning and losing cards
        animate_win_lose([len(table_cards)-2], [len(table_cards)-1])
        collect_cards(player1_deck)
    elif result == 2:
        # Player 2 wins the round
        # Animate winning and losing cards
        animate_win_lose([len(table_cards)-1], [len(table_cards)-2])
        collect_cards(player2_deck)
    else:
        # War!
        initiate_war()

def compare_cards(card1, card2):
    rank1 = ranks.index(card1['rank'])
    rank2 = ranks.index(card2['rank'])
    if rank1 > rank2:
        return 1 # Player 1 wins
    elif rank1 < rank2:
        return 2 # Player 2 wins
    else:
        return 0  # War

def animate_win_lose(winning_indices, losing_indices):
    # Animate winning card scaling up and losing card fading out
    cards_to_animate = []
    for idx in winning_indices:
        card_info = table_cards[idx]
        cards_to_animate.append({
            'start_pos': card_info['pos'],
            'end_pos': card_info['pos'],
            'card': card_info['card'],
            'face_up': True,
            'table_index': idx,
            'action': 'win'
        })
    for idx in losing_indices:
        card_info = table_cards[idx]
        cards_to_animate.append({
            'start_pos': card_info['pos'],
            'end_pos': card_info['pos'],
            'card': card_info['card'],
            'face_up': True,
            'table_index': idx,
            'action': 'lose'
        })
    move_cards_animation(cards_to_animate)
    while animation_in_progress:
        handle_events()
        update_animation()
        draw()
        clock.tick(FPS)
    # Reset scales and opacities
    for idx in winning_indices + losing_indices:
        table_cards[idx]['scale'] = 1.0
        table_cards[idx]['opacity'] = 255

def collect_cards(winner_deck):
    global table_cards, animation_in_progress
    # Animate cards moving to winner's deck simultaneously
    winner_pos = player1_pos if winner_deck == player1_deck else player2_pos
    cards_to_animate = []
    for idx, card_info in enumerate(table_cards):
        cards_to_animate.append({
            'start_pos': card_info['pos'],
            'end_pos': winner_pos,
            'card': card_info['card'],
            'face_up': False,
            'table_index': idx
        })
    move_cards_animation(cards_to_animate)
    while animation_in_progress:
        handle_events()
        update_animation()
        draw()
        clock.tick(FPS)
    # Add cards to winner's deck
    winner_deck.extend([card_info['card'] for card_info in table_cards])
    table_cards.clear()
    pygame.time.wait(500)

def initiate_war():
    global war_flash, war_flash_start
    # Start war flash effect
    war_flash = True
    war_flash_start = pygame.time.get_ticks()
    draw()
    pygame.time.wait(500)
    war()

def war():
    global table_cards, game_over, winner
    # Each player places three cards face down and one card face up
    if len(player1_deck) < 4 or len(player2_deck) < 4:
        # One of the players cannot continue
        game_over = True
        winner = "Player 2" if len(player1_deck) < 4 else "Player 1"
        return

    # Place three face-down cards
    for _ in range(3):
        p1_card = player1_deck.pop(0)
        p2_card = player2_deck.pop(0)
        table_cards.append({'card': p1_card, 'pos': player1_pos, 'face_up': False})
        table_cards.append({'card': p2_card, 'pos': player2_pos, 'face_up': False})

    # Animate face-down cards moving to table simultaneously
    cards_to_animate = []
    for i in range(6):  # Total of 6 cards (3 from each player)
        card_info = table_cards[-6 + i]
        end_x = table_pos[0] - CARD_WIDTH // 2 - 10 - (i // 2) * 10 if i % 2 == 0 else table_pos[0] + CARD_WIDTH // 2 + 10 + (i // 2) * 10
        end_y = table_pos[1]
        cards_to_animate.append({
            'start_pos': player1_pos if i % 2 == 0 else player2_pos,
            'end_pos': (end_x, end_y),
            'card': card_info['card'],
            'face_up': False,
            'table_index': len(table_cards)-6 + i
        })
    move_cards_animation(cards_to_animate)
    while animation_in_progress:
        handle_events()
        update_animation()
        draw()
        clock.tick(FPS)

    # Each player plays one card face up
    p1_card = player1_deck.pop(0)
    p2_card = player2_deck.pop(0)
    table_cards.append({'card': p1_card, 'pos': player1_pos, 'face_up': False})
    table_cards.append({'card': p2_card, 'pos': player2_pos, 'face_up': False})

    # Animate cards moving to table simultaneously
    cards_to_animate = [
        {'start_pos': player1_pos, 'end_pos': (table_pos[0] - CARD_WIDTH // 2 - 10, table_pos[1]), 'card': p1_card, 'face_up': False, 'table_index': len(table_cards)-2},
        {'start_pos': player2_pos, 'end_pos': (table_pos[0] + CARD_WIDTH // 2 + 10, table_pos[1]), 'card': p2_card, 'face_up': False, 'table_index': len(table_cards)-1}
    ]
    move_cards_animation(cards_to_animate)
    while animation_in_progress:
        handle_events()
        update_animation()
        draw()
        clock.tick(FPS)

    # Flip the last two cards face up
    table_cards[-2]['face_up'] = True
    table_cards[-1]['face_up'] = True
    draw()
    pygame.time.wait(500)

    # Compare the last cards
    result = compare_cards(p1_card, p2_card)
    if result == 1:
        # Player 1 wins the war
        # Animate winning and losing cards
        animate_win_lose([len(table_cards)-2], [len(table_cards)-1])
        collect_cards(player1_deck)
    elif result == 2:
        # Player 2 wins the war
        # Animate winning and losing cards
        animate_win_lose([len(table_cards)-1], [len(table_cards)-2])
        collect_cards(player2_deck)
    else:
        # Another war!
        initiate_war()

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

def main():
    global game_over, winner
    while True:
        handle_events()
        if not game_over:
            play_round()
            if not player1_deck:
                game_over = True
                winner = "Player 2"
            elif not player2_deck:
                game_over = True
                winner = "Player 1"
        else:
            draw()
            pygame.time.wait(5000)
            pygame.quit()
            sys.exit()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
