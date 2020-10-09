from math import inf

import pygame_menu

import queue
import sys
import threading
import time
from board import *
from timer import Timer

# Initialize Pygame
pygame.init()

# Fonts
FONT = pygame.font.Font(pygame_menu.font.FONT_OPEN_SANS_BOLD, 18)
BIG_FONT = pygame.font.Font(pygame_menu.font.FONT_OPEN_SANS_BOLD, 26)

# Title and Icon
pygame.display.set_caption("ChessAI")
icon = pygame.image.load(os.path.join('img', 'icon.png'))
pygame.display.set_icon(icon)


class Game:

    def __init__(self):
        self.p1_name = "Player 1"
        self.p2_name = "Minimax"

        self.p1_timer = Timer(600, "bot")
        self.p2_timer = Timer(600, "top")

        self.p1_color = WHITE
        self.p2_color = BLACK

        self.ai_move = queue.Queue()
        self.lock = threading.Lock()

        self.board = Board(self.p1_color)
        self.board.initialize_pieces()

        self.menu_screen()
        #self.TEST_SCREEN()

    def test_screen(self):

        running = True

        self.reset()

        moves = [((6, 7), (7, 5)), ((7, 1), (7, 3)), ((1, 6), (1, 5)), ((2, 1), (2, 2)), ((7, 7), (6, 7)), ((3, 0), (2, 1)), ((1, 5), (1, 4)), ((2, 1), (7, 6)), ((2, 6), (2, 5)), ((7, 6), (6, 7)), ((7, 5), (5, 4)), ((6, 7), (5, 7)), ((4, 7), (5, 7)), ((4, 0), (3, 0)), ((5, 4), (3, 3)), ((2, 2), (3, 3)), ((1, 7), (0, 5)), ((3, 0), (2, 1)), ((5, 6), (5, 4)), ((2, 1), (2, 2)), ((2, 5), (2, 4)), ((3, 3), (2, 4)), ((0, 7), (1, 7)), ((2, 2), (3, 2)), ((4, 6), (4, 4)), ((3, 2), (4, 2)), ((5, 4), (5, 3)), ((4, 2), (3, 2)), ((3, 7), (0, 4)), ((3, 2), (4, 3)), ((3, 6), (3, 4)), ((4, 3), (4, 4)), ((2, 7), (3, 6)), ((4, 4), (3, 4)), ((0, 4), (0, 1)), ((0, 0), (0, 1)), ((0, 5), (2, 6)), ((3, 4), (4, 4)), ((1, 7), (1, 5)), ((2, 4), (1, 5)), ((3, 6), (4, 5)), ((1, 5), (2, 6)), ((0, 6), (0, 5)), ((4, 4), (4, 5)), ((5, 7), (4, 7)), ((0, 1), (0, 5)), ((5, 3), (5, 2)), ((4, 1), (5, 2))]

        i = 0
        for move in moves:
            self.board.tilemap[move[0][0]][move[0][1]].select()
            self.board.tilemap[move[1][0]][move[1][1]].fill(LARGE_TEXT_COLOR)
            self.board.draw()
            pygame.display.flip()

            self.board.print()

            i += 1
            if i > len(moves) - 5:
                time.sleep(3)

            self.board.make_move(move[0], move[1])
            self.board.next_turn()

            self.board.tilemap[move[1][0]][move[1][1]].fill(self.board.tilemap[move[1][0]][move[1][1]].color)

            if self.board.gameover:
                print("GAME OVER: ", self.board.gameover[0])
                if self.board.gameover[0] == "Insufficient Material":
                    self.end_screen(self.board.gameover[0], None)
                else:
                    if self.board.gameover[1] == self.board.player:
                        self.end_screen(self.board.gameover[0], self.p1_name)
                    else:
                        self.end_screen(self.board.gameover[0], self.p2_name)

        self.board.print()

        # Test screen loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.board.draw()

            pygame.display.flip()

    def reset(self):
        """
        Resets board and makes changes to game state to prepare for new game
        :return: None
        """
        self.p2_name = "Minimax"
        self.p1_timer.reset()
        self.p2_timer.reset()
        self.board = Board(self.p1_color)
        self.board.initialize_pieces()
        self.ai_move = queue.Queue()

    def set_name(self, name):
        """
        Sets name of human player
        :param name: name of human player (str)
        :return: None
        """
        self.p1_name = name

    def set_color(self, color, value):
        """
        Sets color of human player
        :param color: color selected by player (str)
        :param value: RGB representation of color (tuple)
        :return: None
        """
        self.board.player = value
        self.p1_color = value
        if value == WHITE:
            self.p2_color = BLACK
            self.board.bottomPlayerTurn = False
        else:
            self.p2_color = WHITE
            self.board.bottomPlayerTurn = True
        self.board = Board(value)
        self.board.initialize_pieces()

    def set_ai(self, tup, value):
        """
        Updates name of AI to correspond to underlying method of move choice
        :param tup: tuple containing color as a string and as an RGB tuple (tuple)
        :param value: numerical value representing AI (int)
        :return: None
        """
        self.p2_name = tup[0]

    def menu_screen(self):
        """
        Displays menu screen
        :return: None
        """
        theme = pygame_menu.themes.Theme(title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
                                         menubar_close_button=False,
                                         widget_font_color=SMALL_TEXT_COLOR,
                                         background_color=BG_COLOR,
                                         widget_font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                                         cursor_color=WHITE)

        menu = pygame_menu.Menu(height=SCREEN_HEIGHT, width=SCREEN_WIDTH, title="", theme=theme, menu_position=(50, 0))
        menu.add_label("ChessAI", align=pygame_menu.locals.ALIGN_CENTER, font_name=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                       font_color=LARGE_TEXT_COLOR, font_size=90, margin=(0, 50))
        menu.add_text_input('Name : ', default=self.p1_name, maxchar=10, onchange=self.set_name)
        menu.add_selector('Color : ', [('White', WHITE), ('Black', BLACK)], onchange=self.set_color)
        menu.add_selector('AI : ', [('Minimax', 1), ('Random', 2)], onchange=self.set_ai)
        menu.add_button('Play', self.game_screen)
        menu.add_button('Quit', pygame_menu.events.EXIT)
        menu.add_label("", align=pygame_menu.locals.ALIGN_CENTER, font_color=BLACK, font_size=70, margin=(0, 50))
        menu.center_content()

        # Keeps track of whether menu screen should keep running or stop
        running = True

        # Menu screen loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            menu.mainloop(SCREEN)

            pygame.display.flip()

    def determine_move(self):
        """
        Determines move for AI and places move in thread-safe container (Queue)
        :return: None
        """
        # Determine move based on selected AI
        if self.p2_name == "Minimax":
            self.ai_move.put(AI.minimax2(self.board.copy(), 1, -inf, inf, True, self.p2_color)[0])
        else:
            self.ai_move.put(AI.random_move(self.board))

        # Close thread after move has been found
        sys.exit()

    def game_screen(self):
        """
        Displays game screen
        :return: None
        """

        # Create clock to keep track of time
        clock = pygame.time.Clock()

        # Stores time passed since last frame (used to tick player timers)
        dt = 0

        # Create a thread which will be used to determine AI's move concurrently with rest of game
        t = threading.Thread(target=self.determine_move)

        # Keeps track of whether or not human player has resigned
        p1_resigned = False

        # Creates collision box for resign button
        resign_button = pygame.Rect(BOARD_X+BOARD_SIZE+8, BOARD_Y+BOARD_SIZE+8, int((TILE_SIZE*4+8)/2-4), 28)

        # Game screen loop
        while True:

            for event in pygame.event.get():
                # Pygame window was closed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Check if any buttons were pressed or pieces were selected
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.board.select()
                    mouse_pos = event.pos
                    self.board.draw()
                    pygame.display.flip()
                    # Resign button was pressed
                    if resign_button.collidepoint(mouse_pos):
                        p1_resigned = True

            # Draw background first (everything else goes on top of it)
            SCREEN.fill(BG_COLOR)

            # Decrement timer for player of current turn
            if self.board.turn == self.p2_color:
                self.p2_timer.tick(dt)
            else:
                self.p1_timer.tick(dt)

            # Draw UI elements
            self.draw_names()
            self.draw_turn_indicator()
            self.p1_timer.draw()
            self.p2_timer.draw()
            self.draw_resign_button()

            # GAME OVER: Checkmate, Stalemate, or Insufficient Material
            if self.board.gameover:
                print("GAME OVER: ", self.board.gameover[0])
                if self.board.gameover[0] == "Insufficient Material":
                    return self.end_screen(self.board.gameover[0], None)
                else:
                    if self.board.gameover[1] == self.board.player:
                        return self.end_screen(self.board.gameover[0], self.p1_name)
                    else:
                        return self.end_screen(self.board.gameover[0], self.p2_name)

            # GAME OVER: Player 1 ran out of time
            if self.p1_timer.time <= 0:
                print("GAME OVER: Timeout")
                return self.end_screen("Timeout", self.p2_name)

            # GAME OVER: Player 2 ran out of time
            if self.p2_timer.time <= 0:
                print("GAME OVER: Timeout")
                return self.end_screen("Timeout", self.p1_name)

            # GAME OVER: Player 1 has resigned
            if p1_resigned:
                print("GAME OVER: Resignation")
                return self.end_screen("Resignation", self.p2_name)

            # Tell AI to determine move if...
            # 1 - It is their turn
            # 2 - They haven't found a move already
            # 3 - The game is not over
            # 4 - They aren't currently searching for a move (ensure 'determine_move' thread is not running)
            self.lock.acquire()
            if self.board.turn == self.p2_color \
                    and self.ai_move.qsize() == 0 \
                    and not self.board.gameover \
                    and not t.is_alive():
                # Need to remake thread, since a thread can only be started once
                t = threading.Thread(target=self.determine_move)
                t.start()
            self.lock.release()

            if self.board.turn == self.p1_color:
                move = AI.random_move(self.board)
                self.board.make_move(move[0], move[1])
                self.board.next_turn()

            # Tell AI to make their move if...
            # 1 - It is their turn
            # 2 - They found a move
            # 3 - The game is not over
            if self.board.turn == self.p2_color \
                    and self.ai_move.qsize() > 0 \
                    and not self.board.gameover:
                move = self.ai_move.get()
                self.board.make_move(move[0], move[1])
                self.board.next_turn()

            # Update time since last frame
            dt = clock.tick(30) / 1000

            # Draw all components of board
            self.board.draw()

            # Update display
            pygame.display.flip()

    def end_screen(self, condition, winner=None):
        """
        Displays end screen
        :param condition: string representing win condition that ended the game (str)
        :param winner: name of winner if applicable (str)
        :return: None
        """

        # Create background for end screen
        bg = pygame.Rect(int(BOARD_X+TILE_SIZE*2.5), int(BOARD_Y+TILE_SIZE*2.5), TILE_SIZE*3, TILE_SIZE*2)

        # Creates collision boxes for rematch and leave buttons
        rematch_button = pygame.Rect(bg.left, bg.bottom-28, bg.centerx-bg.left-2, 28)
        leave_button = pygame.Rect(bg.centerx+2, bg.bottom-28, bg.centerx-bg.left-2, 28)

        # Creates fade transitional effect for end screen
        def fade(width, height):
            f = pygame.Surface((width, height))
            f.fill(BG_COLOR)
            for alpha in range(0, 175):
                f.set_alpha(alpha)
                self.board.draw()
                SCREEN.blit(f, (0, 0))
                pygame.display.update()
                pygame.time.delay(1)

        # Controls fade effect
        fading = True

        # End screen loop
        while True:
            for event in pygame.event.get():
                # Pygame window was closed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Check if any buttons were pressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos

                    # Rematch button was pressed
                    if rematch_button.collidepoint(mouse_pos):
                        self.reset()
                        return self.game_screen()

                    # Leave button was pressed
                    if leave_button.collidepoint(mouse_pos):
                        self.reset()
                        return self.menu_screen()

            # Apply fade effect
            if fading:
                fade(SCREEN_WIDTH, SCREEN_HEIGHT)
                fading = False

            # Draw UI elements
            self.draw_end_message(condition, winner)

            # Update display
            pygame.display.flip()

            # Self-play
            time.sleep(1)
            self.reset()
            return self.game_screen()

    def draw_names(self):
        """
        Draws names for both players
        :return: None
        """
        # Draw top name (player 2)
        pygame.draw.rect(SCREEN, BG_COLOR_LIGHT, [BOARD_X, BOARD_Y - 36, TILE_SIZE*2, 28])
        p1name = FONT.render(self.p2_name, True, SMALL_TEXT_COLOR)
        SCREEN.blit(p1name, (BOARD_X+4, BOARD_Y - 34))
        # Draw bottom name (player 1)
        pygame.draw.rect(SCREEN, BG_COLOR_LIGHT, [BOARD_X, BOARD_Y+BOARD_SIZE+8, TILE_SIZE*2, 28])
        p2name = FONT.render(self.p1_name, True, SMALL_TEXT_COLOR)
        SCREEN.blit(p2name, (BOARD_X+4, BOARD_Y+BOARD_SIZE+10))

    def draw_turn_indicator(self):
        """
        Draws turn indicator based on turn of current player in game screen
        :return: None
        """
        if self.board.turn == self.p1_color:
            txt = FONT.render("YOUR TURN", True, LARGE_TEXT_COLOR)
            SCREEN.blit(txt, (int(BOARD_X + TILE_SIZE * 3.5 + 8), BOARD_Y+BOARD_SIZE+10))
        else:
            txt = FONT.render("AI is thinking...", True, LARGE_TEXT_COLOR)
            SCREEN.blit(txt, (int(BOARD_X + TILE_SIZE * 3.5 + 8), BOARD_Y+BOARD_SIZE+10))

    def draw_resign_button(self):
        """
        Draws resign button in game screen
        :return:
        """
        pygame.draw.rect(SCREEN, BG_COLOR_LIGHT, [BOARD_X + BOARD_SIZE + 8, BOARD_Y + BOARD_SIZE + 8,
                                        int((TILE_SIZE * 4 + 8) / 2 - 4), 28])
        txt = FONT.render("Resign", True, SMALL_TEXT_COLOR)
        SCREEN.blit(txt, (BOARD_X + BOARD_SIZE + 40, BOARD_Y+BOARD_SIZE+10))

    def draw_end_message(self, condition, winner):
        """
        Draws end message in end screen
        :param condition: string representing win condition that ended the game (str)
        :param winner: name of winner if applicable (str)
        :return:
        """
        # Draw 'Game Over' text
        bg = pygame.draw.rect(SCREEN, BG_COLOR_LIGHT,
                              [int(BOARD_X + TILE_SIZE * 2.5), int(BOARD_Y + TILE_SIZE * 2.5), TILE_SIZE * 3,
                               TILE_SIZE * 2])
        pygame.draw.rect(SCREEN, BLACK,
                         [int(BOARD_X + TILE_SIZE * 2.5), int(BOARD_Y + TILE_SIZE * 2.5), TILE_SIZE * 3, TILE_SIZE * 2],
                         1)
        txt = BIG_FONT.render("Game Over", True, LARGE_TEXT_COLOR)
        SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3 - 8, int(BOARD_Y + TILE_SIZE * 2.5 + 4)))

        # Draw win condition and winner (if applicable)
        if winner:
            txt = FONT.render(winner + " won", True, SMALL_TEXT_COLOR)
            SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3, BOARD_Y + TILE_SIZE * 3 + 4))
            txt = FONT.render(f"by {condition}", True, SMALL_TEXT_COLOR)
            SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3, int(BOARD_Y + TILE_SIZE * 3.4)))
        else:
            txt = FONT.render(f"{condition}", True, SMALL_TEXT_COLOR)
            SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3 + 32, BOARD_Y + TILE_SIZE * 3))

        # Draw Rematch button
        pygame.draw.rect(SCREEN, BLACK, [bg.left, bg.bottom - 28, bg.centerx - bg.left + 3, 28], 1)
        txt = FONT.render("Rematch", True, SMALL_TEXT_COLOR)
        SCREEN.blit(txt, (bg.left + 8, bg.bottom - 28 + 2))

        # Draw Leave button
        pygame.draw.rect(SCREEN, BLACK, [bg.centerx + 2, bg.bottom - 28, bg.centerx - bg.left - 2, 28], 1)
        txt = FONT.render("Leave", True, SMALL_TEXT_COLOR)
        SCREEN.blit(txt, (bg.centerx + 20, bg.bottom - 28 + 2))


if __name__ == "__main__":
    Game()
