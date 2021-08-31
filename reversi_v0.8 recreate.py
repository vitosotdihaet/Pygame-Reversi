import pygame as pg
import sys
import os
from pygame import gfxdraw
from random import randrange
from itertools import product

from pygame.constants import RESIZABLE

pg.font.init()

# CLASSES
class Button:
    def __init__(self, color, x, y, width, height, text=""):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, outline=None):
        if outline:
            pg.draw.rect(
                screen_surf,
                outline,
                (self.x + 5, self.y + 5, self.width, self.height),
                0,
            )
        pg.draw.rect(
            screen_surf, self.color, (self.x, self.y, self.width, self.height), 0
        )

        if self.text != "" and self.text != "DELAY":
            lines = self.text.split("\n")
            for i, line in enumerate(lines, start=1):
                text = font_lil.render(line, 1, (255, 255, 255))
                screen_surf.blit(
                    text,
                    (
                        self.x + (self.width / 2 - text.get_width() / 2),
                        self.y
                        + (self.height / (len(lines) + 1) * i - text.get_height() / 2),
                    ),
                )

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


class Board:
    def __init__(self, grid):
        self.grid = grid

    def draw(self, cur_player):
        for y, x in product(range(8), repeat=2):
            xr = x * 100 + 50
            yr = y * 100 + 50

            pg.draw.rect(
                screen_surf, BACKGR, pg.Rect(((x) * 100 + 1, (y) * 100 + 1, 98, 98))
            )  # draws bg cell

            if self.grid[y][x] == 1:
                draw_checker(xr, yr, 48, CHECKER_RED, CHECKER_RED_add)
            elif self.grid[y][x] == 2:
                draw_checker(xr, yr, 48, CHECKER_WHITE, CHECKER_WHITE_add)

        draw_checker(
            250, 870, 50, player_color[not cur_player], player_color_add[not cur_player]
        )
        draw_checker(50, 860, 25, CHECKER_WHITE, CHECKER_WHITE_add)
        draw_checker(50, 940, 25, CHECKER_RED, CHECKER_RED_add)

        for i in range((self.available())):
            x, y = (
                self.available_tiles()[0][i][0] * 100 + 1,
                self.available_tiles()[0][i][1] * 100 + 1,
            )
            pg.draw.rect(screen_surf, (0, 200, 0), pg.Rect((x, y, 98, 98)))
            num = font.render(str(self.available_tiles()[1][i]), 1, (0, 0, 0))
            num_rect = num.get_rect(center=(x + 48, y + 50))
            screen_surf.blit(num, num_rect)

    def player_turn(self, cur_x, cur_y, acceptable, new):
        global wrong_tile_bool, second_score_text, first_score_text, first_score, second_score, cur_player
        try:
            if self.grid[cur_y][cur_x] == 0:
                for y, x in product(range(3), repeat=2):
                    find_x, find_y = x - 1, y - 1
                    dir_x, dir_y = find_x, find_y

                    if (
                        self.grid[cur_y + find_y][cur_x + find_x]
                        == int(not cur_player) + 1
                    ):
                        acceptable += 1
                        while (
                            self.grid[cur_y + find_y][cur_x + find_x]
                            == int(not cur_player) + 1
                        ):
                            new.append((cur_y + find_y, cur_x + find_x))
                            find_x += dir_x
                            find_y += dir_y
                            if (
                                self.grid[cur_y + find_y][cur_x + find_x]
                                == int(cur_player) + 1
                            ):
                                pass
                            elif self.grid[cur_y + find_y][cur_x + find_x] == 0:
                                new = []
                                acceptable -= 1

                        for i in range(len(new)):
                            self.grid[new[i][0]][new[i][1]] = int(cur_player) + 1
                            self.grid[cur_y][cur_x] = int(cur_player) + 1

                if acceptable == 0:
                    wrong_tile_bool = True
                    self.grid[cur_y][cur_x] = 0
                    cur_player = not cur_player
                else:
                    wrong_tile_bool = False
                    if RGC_mod:
                        RGC()
                    else:
                        DEFAULT_COLORS()

            else:
                wrong_tile_bool = True
                cur_player = not cur_player

        except IndexError:
            pass

        first_score, second_score = 0, 0
        for y, x in product(range(8), repeat=2):
            if self.grid[y][x] == 1:
                first_score += 1
            elif self.grid[y][x] == 2:
                second_score += 1

        second_score_text = font.render(str(first_score), 1, BACKGR)
        first_score_text = font.render(str(second_score), 1, BACKGR)

        cur_player = not cur_player

    def computer_turn(self):
        temp = self.available_tiles()
        steps_count = temp[1]
        poss_steps = temp[0]
        if type_of_game == "HIGHEST SCORE":
            try:
                maxi = steps_count.index(max(steps_count))
                cur_x = poss_steps[maxi][0]
                cur_y = poss_steps[maxi][1]
            except ValueError:
                pass
        # elif type_of_game == "smart":
        else:
            next_random = randrange(0, self.available())
            cur_x = poss_steps[next_random][0]
            cur_y = poss_steps[next_random][1]
        grid.player_turn(cur_x, cur_y, 0, [])

    def available_tiles(self):
        available = [[], []]
        for cur_y, cur_x in product(range(8), repeat=2):
            try:
                if self.grid[cur_y][cur_x] == 0:
                    acceptable = 0
                    fc = 0
                    for y, x in product(range(3), repeat=2):
                        find_x, find_y = x - 1, y - 1
                        dir_x, dir_y = find_x, find_y
                        counter = 0

                        if (
                            self.grid[cur_y + find_y][cur_x + find_x]
                            == int(not cur_player) + 1
                        ):
                            acceptable += 1
                            while (
                                self.grid[cur_y + find_y][cur_x + find_x]
                                == int(not cur_player) + 1
                            ):
                                find_x += dir_x
                                find_y += dir_y
                                counter += 1
                                if self.grid[cur_y + find_y][cur_x + find_x] == 0:
                                    acceptable -= 1
                                    counter = 0
                        fc += counter

                    if acceptable != 0:
                        available[0].append((cur_x, cur_y))
                        available[1].append(fc)

            except IndexError:
                pass

        return available

    def available(self):
        return len(self.available_tiles()[0])


"""
    def find_best_step_1(self, cur_player, steps):
        for i in range(available()):
            pre_score = (first_score, second_score)
"""

# ---
def turn_on_main_menu():
    global cur_player, over, wrong_tile_text, grid
    board = [[0 for _ in range(9)] for _ in range(9)]
    board[3][3], board[4][4] = 1, 1
    board[3][4], board[4][3] = 2, 2
    grid = Board(board)
    cur_player = True
    main_menu(True, screen_surf)
    grid.player_turn(3, 3, 0, [])
    over = False
    wrong_tile_text = font_lil.render("Choose a tile", 1, BACKGR)


def edit_winning_text():
    global player_1_text, player_2_text, player_1_rect, player_2_rect
    player_1_text = font_huge.render(str(checkers[1]) + " WIN", 1, (0, 0, 0))
    player_2_text = font_huge.render(str(checkers[0]) + " WIN", 1, (0, 0, 0))
    player_1_rect = player_1_text.get_rect(center=(400, 550))
    player_2_rect = player_2_text.get_rect(center=(400, 550))


def blit():
    screen_surf.fill(MAINBACK)
    grid.draw(cur_player)
    if over:
        temp = pg.Rect(0, 0, 750, 300)
        temp.center = (400, 480)
        pg.draw.rect(screen_surf, (65, 65, 65), temp, 0, 30)
    screen.blit(screen_surf, (0, 0))
    screen.blit(turn_text, turn_rect)
    screen.blit(first_score_text, first_score_rect)
    screen.blit(second_score_text, second_score_rect)

    if over:
        screen.blit(game_over_text, game_over_rect)
        if first_score > second_score:
            screen.blit(player_1_text, player_1_rect)
        elif second_score > first_score:
            screen.blit(player_2_text, player_2_rect)
        elif first_score == second_score:
            screen.blit(tie_text, tie_rect)

    if first_score + second_score == 4:
        wrong_tile_text = font_lil.render("Choose a tile", 1, BACKGR)
        screen.blit(wrong_tile_text, wrong_tile_rect)
    else:
        wrong_tile_text = font_lil.render("Choose another tile", 1, BACKGR)

    if wrong_tile_bool and (pvp or pvc and cur_player):
        screen.blit(wrong_tile_text, wrong_tile_rect)


# DRAW_FUNCTIONS
def draw_main_buttons():
    DELAY_BUTTON = Button(
        (gray, gray, gray), 450, 575, 250, 150, "DELAY:\n" + str(delay_time)
    )
    TYPE_OF_GAME_BUTTON = Button(
        (80, 80, 150), 100, 750, 600, 150, "BOT BEHAVIOR:\n" + type_of_game
    )
    PVP_BUTTON.draw((20, 20, 20))
    PVC_BUTTON.draw((20, 20, 20))
    CVC_BUTTON.draw((20, 20, 20))
    TYPE_OF_GAME_BUTTON.draw((20, 20, 20))

    if RGC_mod:
        RGC_BUTTON_ON.draw((20, 20, 20))
    else:
        RGC_BUTTON_OFF.draw((20, 20, 20))
    DELAY_BUTTON.draw((20, 20, 20))

    screen.blit(screen_surf, (0, 0))
    screen.blit(choose_text, choose_rect)


def draw_checker(x, y, r1, checker_color, checker_color_add):
    gfxdraw.aacircle(screen_surf, x, y, r1, checker_color_add)
    gfxdraw.filled_circle(screen_surf, x, y, r1, checker_color_add)

    gfxdraw.aacircle(screen_surf, x, y, r1, checker_color)
    gfxdraw.filled_circle(screen_surf, x, y, int(r1 / 48 * 40), checker_color)


# FUN_FUNCTIONS
def RGC():
    global CHECKER_WHITE, CHECKER_RED, CHECKER_WHITE_add, CHECKER_RED_add, player_color, player_color_add
    CHECKER_WHITE = (randrange(20, 255), randrange(20, 255), randrange(20, 255))
    CHECKER_WHITE_add = (
        CHECKER_WHITE[0] - 20,
        CHECKER_WHITE[1] - 20,
        CHECKER_WHITE[2] - 20,
    )
    CHECKER_RED = (randrange(20, 255), randrange(20, 255), randrange(20, 255))
    CHECKER_RED_add = (CHECKER_RED[0] - 20, CHECKER_RED[1] - 20, CHECKER_RED[2] - 20)
    player_color = [CHECKER_WHITE, CHECKER_RED]
    player_color_add = [CHECKER_WHITE_add, CHECKER_RED_add]


def DEFAULT_COLORS():
    global CHECKER_WHITE, CHECKER_RED, CHECKER_WHITE_add, CHECKER_RED_add, player_color, player_color_add
    CHECKER_WHITE = (255, 255, 255)
    CHECKER_WHITE_add = (235, 235, 235)
    CHECKER_RED = (45, 45, 45)
    CHECKER_RED_add = (40, 40, 40)
    player_color = [CHECKER_WHITE, CHECKER_RED]
    player_color_add = [CHECKER_WHITE_add, CHECKER_RED_add]


# COLORS
CHECKER_WHITE = (255, 255, 255)
CHECKER_WHITE_add = (235, 235, 235)
CHECKER_RED = (100, 0, 0)
CHECKER_RED_add = (80, 0, 0)
BACKGR = (10, 80, 10)
MAINBACK = (30, 30, 30)
player_color = [CHECKER_WHITE, CHECKER_RED]
player_color_add = [CHECKER_WHITE_add, CHECKER_RED_add]

# MAIN_INFO
board = [[0 for _ in range(9)] for _ in range(9)]
board[3][3], board[4][4] = 1, 1
board[3][4], board[4][3] = 2, 2

grid = Board(board)

# PARAMETERS
current_path = os.path.dirname(__file__)
resources_path = os.path.join(current_path, "resources")
font_path = os.path.join(resources_path, "fonts")
image_path = os.path.join(resources_path, "images")

# FONTS
microgramma = "microgramma.ttf"
allison = "Allison-Regular.ttf"
hp = "HPSimplified_Rg.ttf"
lobster = "lobster.ttf"
rockwell = "RockwellNovaCond.ttf"
comic = "comic.ttf"
impact = "impact.ttf"
tabs = "AmpleSoundTab.ttf"
gestures = "holomdl2.ttf"

font = pg.font.Font((os.path.join(font_path, hp)), 90)
font_lil = pg.font.Font((os.path.join(font_path, hp)), 54)
font_huge = pg.font.Font((os.path.join(font_path, hp)), 140)

# PG_INFO
size = width, height = 800, 1000
screen = pg.display.set_mode(size)
pg.display.set_caption("REVERSI")
icon = pg.image.load(os.path.join(image_path, "icon.png"))
pg.display.set_icon(icon)
screen_surf = pg.Surface(size, RESIZABLE)

# STARTING_INFO
cur_player = True
main_screen = True
types_of_game = ["RANDOM", "HIGHEST SCORE"]
type_of_game = types_of_game[0]
idx = 0
game = False
pvp = False
cvc = False
pvc = False
over = False
gray = 40
wrong_tile_bool = False
RGC_mod = False
delay_time = 0
checkers = ["P1", "P2"]
first_score, second_score = 2, 2

# TEXT
turn_text = font.render("TURN", 1, BACKGR)
turn_rect = turn_text.get_rect(center=(450, 870))

first_score_text = font.render(str(second_score), 1, BACKGR)
first_score_rect = first_score_text.get_rect(center=(115, 860))

second_score_text = font.render(str(first_score), 1, BACKGR)
second_score_rect = second_score_text.get_rect(center=(115, 940))

wrong_tile_text = font_lil.render("Choose another tile", 1, BACKGR)
wrong_tile_rect = (200, 920)

game_over_text = font_huge.render("GAME OVER", 1, (0, 0, 0))
game_over_rect = game_over_text.get_rect(center=(400, 400))

tie_text = font_huge.render("TIE", 1, (0, 0, 0))
tie_rect = tie_text.get_rect(center=(400, 550))

choose_text = font_lil.render("Choose game type", 1, (255, 255, 255))
choose_rect = choose_text.get_rect(center=(400, 100))

# BUTTONS
PVP_BUTTON = Button((0, 150, 0), 100, 200, 600, 100, "PVP")
PVC_BUTTON = Button((255, 211, 0), 100, 325, 600, 100, "PVC")
CVC_BUTTON = Button((200, 0, 0), 100, 450, 600, 100, "CVC")
RGC_BUTTON_OFF = Button((51, 0, 51), 100, 575, 250, 150, "RGC OFF")
RGC_BUTTON_ON = Button((255, 0, 153), 100, 575, 250, 150, "RGC ON")
DELAY_BUTTON = Button((gray, gray, gray), 450, 625, 250, 100, "DELAY")
TYPE_OF_GAME_BUTTON = Button(
    (100, 100, 150), 100, 750, 600, 150, "BOT BEHAVIOUR:\n" + type_of_game
)

# MAIN_MENU
def main_menu(main_screen, screen_surf):
    global pvp, cvc, pvc, game, delay_time, checkers, type_of_game, idx, TYPE_OF_GAME_BUTTON, RGC_mod, gray
    while main_screen:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.VIDEORESIZE:
                screen_surf = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)

            mouse_pos = pg.mouse.get_pos()

            # CURSOR_CHANGES
            if (
                PVP_BUTTON.isOver(mouse_pos)
                or PVC_BUTTON.isOver(mouse_pos)
                or CVC_BUTTON.isOver(mouse_pos)
                or RGC_BUTTON_ON.isOver(mouse_pos)
                or DELAY_BUTTON.isOver(mouse_pos)
                or TYPE_OF_GAME_BUTTON.isOver(mouse_pos)
            ):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            else:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

            # TYPE_OF_A_GAME/PARAMETERS
            if event.type == pg.MOUSEBUTTONUP:
                mouse_pos = event.pos
                if event.button == 1 or event.button == 4:
                    if PVP_BUTTON.isOver(mouse_pos):
                        pvp = True
                        cvc = False
                        pvc = False
                        game = True
                        main_screen = False
                        checkers[0] = "Player 1"
                        checkers[1] = "Player 2"

                    elif PVC_BUTTON.isOver(mouse_pos):
                        pvc = True
                        pvp = False
                        cvc = False
                        game = True
                        main_screen = False
                        checkers[0] = "Player"
                        checkers[1] = "Computer"

                    elif CVC_BUTTON.isOver(mouse_pos):
                        cvc = True
                        pvp = False
                        pvc = False
                        game = True
                        main_screen = False
                        checkers[0] = "Comp 1"
                        checkers[1] = "Comp 2"

                    elif RGC_BUTTON_ON.isOver(mouse_pos):
                        RGC_mod = not RGC_mod

                    elif DELAY_BUTTON.isOver(mouse_pos):
                        delay_time = (delay_time + 50) % 550
                        gray += 10
                        if gray >= 150:
                            gray = 40

                    elif TYPE_OF_GAME_BUTTON.isOver(mouse_pos):
                        idx = (idx + 1) % len(types_of_game)
                        type_of_game = types_of_game[idx]

                elif RGC_BUTTON_ON.isOver(mouse_pos):
                    RGC_mod = not RGC_mod

                elif event.button == 3 or event.button == 5:
                    if DELAY_BUTTON.isOver(mouse_pos):
                        delay_time = (delay_time - 50) % 550
                        gray -= 10
                        if gray < 40:
                            gray = 140
                        if delay_time < 0:
                            delay_time = 0

            if RGC_mod:
                RGC()
            else:
                DEFAULT_COLORS()

            TYPE_OF_GAME_BUTTON = Button((0, 150, 0), 100, 800, 600, 100, type_of_game)

            screen_surf.fill(MAINBACK)
            draw_main_buttons()
            pg.display.update()


main_menu(main_screen, screen_surf)

# GAME
while game:
    over = not grid.available()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.VIDEORESIZE:
            screen_surf = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)

        cur_x, cur_y = pg.mouse.get_pos()[0] // 100, pg.mouse.get_pos()[1] // 100
        acc_tiles = grid.available_tiles()[0]

        if (cur_x, cur_y) in acc_tiles or (
            cur_x == 2 and 850 < pg.mouse.get_pos()[1] < 950
        ):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

        if event.type == pg.MOUSEBUTTONDOWN:

            if 200 < event.pos[0] < 300 and 850 < event.pos[1] < 950:
                turn_on_main_menu()

        if pvp and not over:
            if event.type == pg.MOUSEBUTTONDOWN:
                if 0 <= cur_x < 8 and 0 <= cur_y < 8:
                    grid.player_turn(cur_x, cur_y, 0, [])

        if pvc and not over:
            if cur_player:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if 0 <= cur_x < 8 and 0 <= cur_y < 8:
                        grid.player_turn(cur_x, cur_y, 0, [])
                        blit()
                        pg.display.update()
                        if delay_time > 0 and (not cvc and not cur_player) and not pvp:
                            pg.time.delay(delay_time)
            else:
                grid.computer_turn()

    if cvc and not over:
        grid.computer_turn()
        blit()
        pg.display.update()
        pg.time.delay(delay_time)

    # WINNIG_TEXT
    edit_winning_text()

    # BLITS
    blit()
    pg.display.update()
