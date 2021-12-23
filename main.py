import pygame as pg
from pygame import gfxdraw
import sys
import os
from random import randrange
from itertools import product

pg.font.init()

# CLASSES
class OnScreenText:
    def __init__(self, text, fontsize, coords, antial=True, center=True, color=(0, 0, 0)):
        self.text = text
        self.fontsize = fontsize
        self.color = color
        self.antial = antial
        self.coords = coords
        self.center = center

        self.rendered_text = self.fontsize.render(self.text, self.antial, self.color)
        if self.center == True: self.rect = self.rendered_text.get_rect(center=self.coords)
        else: self.rect = coords

    def blit(self):
        SCREEN.blit(self.rendered_text, self.rect)

    def update(self):
        self.rendered_text = self.fontsize.render(self.text, self.antial, self.color)
        if self.center == True: self.rect = self.rendered_text.get_rect(center=self.coords)
        else: self.rect = self.coords


class Button:
    def __init__(self, color, x, y, width, height, text=""):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, outline=None):
        if outline: pg.draw.rect(screen_surf, outline, (self.x + 5, self.y + 5, self.width, self.height), 0)
        pg.draw.rect(screen_surf, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != "":
            lines = self.text.split("\n")
            for i, line in enumerate(lines, start=1):
                text = font_little.render(line, True, (255, 255, 255))

                screen_surf.blit(
                    text,
                    (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/(len(lines) + 1) * i - text.get_height()/2))
                    )

    def is_over(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


class Board:
    def __init__(self, grid, player):
        self.grid = grid
        self.player = player

    def new(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        board[3][3], board[4][4] = 1, 1
        board[3][4], board[4][3] = 2, 2
        return Board(board, True)

    def print(self, text='end'):
        for row in range(8):
            for col in range(8):
                print(self.grid[row][col], end="|")
            print()
        print(text)

    def draw(self):
        for y, x in product(range(8), repeat=2):
            xcord = x * 100 + 50
            ycord = y * 100 + 50

            pg.draw.rect(screen_surf, GREEN, pg.Rect(((x) * 100 + 1, (y) * 100 + 1, 98, 98)))

            if self.grid[y][x] == 2:
                draw_checker((xcord, ycord), 48, CHECKER_BLACK, CHECKER_BLACK_add)
            elif self.grid[y][x] == 1:
                draw_checker((xcord, ycord), 48, CHECKER_WHITE, CHECKER_WHITE_add)

        draw_checker((250, 860), 50, player_color[self.player], player_color_add[self.player])
        draw_checker((50, 860), 25, CHECKER_BLACK, CHECKER_BLACK_add)
        draw_checker((50, 940), 25, CHECKER_WHITE, CHECKER_WHITE_add)

        moves = self.moves()
        for i in range(len(moves[0])):
            xcord = moves[0][i][0] * 100 + 1
            ycord = moves[0][i][1] * 100 + 1

            if (pvp or (pvc and self.player)) and hints_on:
                pg.draw.rect(screen_surf, (0, 160, 0), pg.Rect((xcord, ycord, 98, 98)))
                eat_num = font_medium.render(str(moves[1][i]), True, (0, 0, 0))
                eat_num_rect = eat_num.get_rect(center=(xcord + 48, ycord + 50))
                screen_surf.blit(eat_num, eat_num_rect)

    def insert(self, x, y):
        global blk_score_text, wht_score_text, wht_score, blk_score
        if self.grid[y][x] == 0:
            self.grid[y][x] = int(self.player) + 1
            self.player = not self.player

        blk_score, wht_score = 0, 0
        for y, x in product(range(8), repeat=2):
            if self.grid[y][x] == 2: blk_score += 1
            elif self.grid[y][x] == 1: wht_score += 1

        blk_score_text.text = str(blk_score)
        wht_score_text.text = str(wht_score)
        blk_score_text.update()
        wht_score_text.update()

    def cell_can_eat(self, x, y):
        available = []

        eaten_current = 0
        for yd, xd in product([-1, 0, 1], repeat=2):
            if xd == yd == 0: continue

            counter = 0
            xf = x + xd 
            yf = y + yd

            can_eat_in_this_direction = []

            if not (xf in range(8) and yf in range(8)): continue

            while (self.grid[yf][xf] == int(not self.player) + 1):
                can_eat_in_this_direction.append((xf, yf))
                xf += xd
                yf += yd
                counter += 1

                if not (xf in range(8) and yf in range(8)): break
                if self.grid[yf][xf] == int(self.player) + 1:
                    available.extend(can_eat_in_this_direction)
                    eaten_current += counter

        return available

    def moves(self):
        moves = [[], []]
        for y, x in product(range(8), repeat=2):
            t = self.cell_can_eat(x, y)

            if self.grid[y][x] == 0 and len(t) != 0:
                moves[0].append((x, y))
                moves[1].append(len(t))

        return moves

    def turn(self, x, y):
        global wrong_tile_bool
        to_eat = self.cell_can_eat(x, y)
        if len(to_eat) == 0:
            wrong_tile_bool = True
            return
        wrong_tile_bool = False

        for coords in to_eat:
            self.grid[coords[1]][coords[0]] = int(self.player) + 1
        self.insert(x, y)

        if RGC_MOD: SET_RGC()

    def computer_turn(self, tog):
        t = self.choose_tog(tog)
        self.turn(t[0], t[1])

    def choose_tog(self, tog):
        steps = self.moves()
        steps_count = steps[1]
        poss_steps = steps[0]

        if tog == types_of_game[1]:
            maxi = randind_of_max(steps_count)
            x = poss_steps[maxi][0]
            y = poss_steps[maxi][1]

        elif tog == types_of_game[2]:
            t = self.compute_best_step(self.player, tog)
            x, y = t[0], t[1]

        else:
            next_random = randrange(0, len(self.moves()[0]))
            x = poss_steps[next_random][0]
            y = poss_steps[next_random][1]

        return (x, y)

    def compute_best_step(self, player, tog, depth=3):
        if depth <= 0:
            return (-1, -1)

        ogrid = self.grid
        ngrid = [[0 for _ in range(9)] for _ in range(9)]
        good_turns = []
        best_step_ind = 0
        steps = self.moves()

        for i in range(len(steps[0])):
            for r, c in product(range(8), repeat=2):
                ngrid[r][c] = ogrid[r][c]
            tboard = Board(ngrid, player)
            xbest, ybest = -1, -1
            maxis = [-1, -1]

            if wht_score + blk_score < 32:
                for x, y in tboard.moves()[0]:
                    for xc, yc in tboard.cell_can_eat(x, y):
                        if abs(3.5 - xc) > maxis[0] or abs(3.5 - yc) > maxis[1]:
                            xbest = steps[0][i][0]
                            ybest = steps[0][i][1]
                            maxis = [abs(3.5 - xc), abs(3.5 - yc)]

            elif 32 <= wht_score + blk_score < 56:
                for x, y in tboard.moves()[0]:
                    if len(tboard.cell_can_eat(x, y)) > len(tboard.cell_can_eat(xbest, ybest)):
                        xbest = steps[0][i][0]
                        ybest = steps[0][i][1]

            elif wht_score + blk_score >= 56:
                xbest, ybest = tboard.choose_tog(types_of_game[1])

            good_turns.append((xbest, ybest))

        for r, c in product(range(8), repeat=2):
            ngrid[r][c] = ogrid[r][c]
        tboard = Board(ngrid, player)

        # print(good_turns)
        best_step = 0
        if good_turns == [] or good_turns == [(0, 0) for _ in range(len(good_turns))]:
            return tboard.choose_tog(types_of_game[0])

        for i, coords in enumerate(good_turns):
            t = tboard.cell_can_eat(coords[0], coords[1])
            if best_step < len(t):
                best_step_ind = i
                best_step = len(t)

        for i, coords in enumerate(good_turns):
            if coords in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                return coords
            if coords in [(1, 1), (1, 6), (6, 1), (6, 6)]:
                best_step_ind += 1
            if coords in [(0, 1), (1, 0), (0, 6), (6, 0),
                        (1, 7), (7, 1), (6, 7), (7, 6)]:
                t = tboard.cell_can_eat(good_turns[i][0], good_turns[i][1])
                if best_step_ind == i and best_step * RISK_FACTOR < len(t):
                    best_step_ind += 1
                    best_step = len(t)

        if best_step_ind > len(good_turns) - 1:
            best_step_ind = 0

        return (good_turns[best_step_ind])

    def blit(self):
        global wrong_tile_text
        screen_surf.fill(MAINBG)
        self.draw()

        if game_over:
            endscreen = pg.Rect(0, 0, 750, 300)
            endscreen.center = (400, 480)
            pg.draw.rect(screen_surf, (100, 100, 100), endscreen, 0, 30)

        draw_arrow(218, 850, 10, GREEN)
        SCREEN.blit(screen_surf, (0, 0))
        turn_text.blit()
        blk_score_text.blit()
        wht_score_text.blit()

        if game_over:
            game_over_text.blit()
            if wht_score > blk_score:
                player_1_text.blit()
            elif blk_score > wht_score:
                player_2_text.blit()
            elif wht_score == blk_score:
                tie_text.blit()

        if wht_score + blk_score == 4:
            wrong_tile_text.text = "Choose a tile"
            wrong_tile_text.blit()
        else: wrong_tile_text.text = "Choose another tile"

        if wrong_tile_bool:
            wrong_tile_text.blit()

    def turn_on_main_menu(self):
        global game_over, wrong_tile_text
        tboard = self.new()
        main_menu()
        game_over = False
        wrong_tile_text.text = "Choose a tile"
        tboard.insert(3, 3)
        return tboard


# UTILITY
def edit_winning_text():
    global player_1_text, player_2_text, player_1_rect, player_2_rect
    player_1_text.text = str(checkers[0]) + " WIN"
    player_2_text.text = str(checkers[1]) + " WIN"
    player_1_text.update()
    player_2_text.update()

# RANDOM
def randind_of_max(array):
    maximum = max(array)
    ids = []
    for i, num in enumerate(array):
        if num == maximum:
            ids.append(i)
    return ids[randrange(0, len(ids))]

def randind_of_min(array):
    minimum = min(array)
    ids = []
    for i, num in enumerate(array):
        if num == minimum:
            ids.append(i)
    return ids[randrange(0, len(ids))]


# DRAW
def draw_main_buttons():
    PVP_BUTTON.draw((20, 20, 20))
    PVC_BUTTON.draw((20, 20, 20))
    CVC_BUTTON.draw((20, 20, 20))

    RGC_BUTTON.draw((20, 20, 20))
    DELAY_BUTTON.draw((20, 20, 20))

    BOT1_BUTTON.draw((20, 20, 20))
    BOT2_BUTTON.draw((20, 20, 20))
    HINTS_BUTTON.draw((20, 20, 20))

    SCREEN.blit(screen_surf, (0, 0))
    choice_text.blit()

def draw_checker(coords, r1, checker_color, checker_color_add):
    gfxdraw.aacircle(screen_surf, coords[0], coords[1],  r1, checker_color_add)
    gfxdraw.filled_circle(screen_surf, coords[0], coords[1], r1, checker_color_add)

    gfxdraw.aacircle(screen_surf, coords[0], coords[1], r1, checker_color)
    gfxdraw.filled_circle(screen_surf, coords[0], coords[1], int(r1 / 48 * 40), checker_color)

def draw_arrow(x, y, size, color=(0, 0, 0), facing_left=True):
    pg.draw.rect(screen_surf, color, (x, y, 7 * size, 2 * size))
    if facing_left:
        pg.draw.line(screen_surf, color, (x, y + size), (x + 2 * size, y - 2 * size), 5 + size)
        pg.draw.line(screen_surf, color, (x, y + size), (x + 2 * size, y + 4 * size), 5 + size)
    else:
        pg.draw.line(screen_surf,color, (x, y + size), (800 - x + 2 * size, y - 2 * size), 2 + size)
        pg.draw.line( screen_surf, color, (x, y + size), (800 - x + 2 * size, y + 4 * size), 2 + size)


# FUN
def SET_RGC():
    global CHECKER_WHITE, CHECKER_BLACK, CHECKER_WHITE_add, CHECKER_BLACK_add, player_color, player_color_add

    CHECKER_WHITE = (randrange(20, 255), randrange(20, 255), randrange(20, 255))
    CHECKER_WHITE_add = (CHECKER_WHITE[0] - 20, CHECKER_WHITE[1] - 20, CHECKER_WHITE[2] - 20)
    CHECKER_BLACK = (randrange(20, 255), randrange(20, 255), randrange(20, 255))
    CHECKER_BLACK_add = (CHECKER_BLACK[0] - 20, CHECKER_BLACK[1] - 20, CHECKER_BLACK[2] - 20)

    player_color = [CHECKER_WHITE, CHECKER_BLACK]
    player_color_add = [CHECKER_WHITE_add, CHECKER_BLACK_add]

def SET_DEFAULT_COLORS():
    global CHECKER_WHITE, CHECKER_BLACK, CHECKER_WHITE_add, CHECKER_BLACK_add, player_color, player_color_add

    CHECKER_WHITE = (255, 255, 255)
    CHECKER_WHITE_add = (235, 235, 235)
    CHECKER_BLACK = (45, 45, 45)
    CHECKER_BLACK_add = (40, 40, 40)

    player_color = [CHECKER_WHITE, CHECKER_BLACK]
    player_color_add = [CHECKER_WHITE_add, CHECKER_BLACK_add]


# COLORS
CHECKER_WHITE = (255, 255, 255)
CHECKER_WHITE_add = (235, 235, 235)
CHECKER_BLACK = (100, 0, 0)
CHECKER_BLACK_add = (80, 0, 0)
GREEN = (10, 80, 10)
MAINBG = (25, 25, 25)
player_color = [CHECKER_WHITE, CHECKER_BLACK]
player_color_add = [CHECKER_WHITE_add, CHECKER_BLACK_add]

# CONNSTANTS
RISK_FACTOR = 0.5

# MAIN_INFO
MAIN_BOARD = Board.new(self=Board([[0 for _ in range(9)] for _ in range(9)], True))
types_of_game = ["EASY", "MEDIUM", "HARD"]

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

font_little = pg.font.Font((os.path.join(font_path, hp)), 54)
font_medium = pg.font.Font((os.path.join(font_path, hp)), 90)
font_huge = pg.font.Font((os.path.join(font_path, hp)), 120)

# PG_INFO
size = width, height = 800, 1000
SCREEN = pg.display.set_mode(size)
pg.display.set_caption("Reversi by Vitaly Klimenko")
icon = pg.image.load(os.path.join(image_path, "icon.png"))
pg.display.set_icon(icon)
screen_surf = pg.Surface(size)

# STARTING_INFO
main_screen = True
bot1_beh = types_of_game[1]
bot2_beh = types_of_game[2]
game = False
pvp = False
cvc = False
pvc = False
hints_on = True
game_over = False
gray = 40
wrong_tile_bool = False
RGC_MOD = False
delay_time = 200
checkers = ["White", "Black"]
wht_score, blk_score = 2, 2

# TEXT
choice_text = OnScreenText("Choose game type", font_little, (400, 100), color=(255, 255, 255))
turn_text = OnScreenText("TURN", font_medium, (440, 860), color=GREEN)
wrong_tile_text = OnScreenText("Choose another tile", font_little, (196, 920), center=False, color=GREEN)

blk_score_text = OnScreenText(str(blk_score), font_medium, (95, 810), center=False, color=GREEN)
wht_score_text = OnScreenText(str(wht_score), font_medium, (95, 890), center=False, color=GREEN)

game_over_text = OnScreenText("GAME OVER", font_huge, (400, 400))
tie_text = OnScreenText("TIE", font_huge, (400, 550))

player_1_text = OnScreenText(str(checkers[0]) + " WIN", font_huge, (400, 550))
player_2_text = OnScreenText(str(checkers[1]) + " WIN", font_huge, (400, 550))

# BUTTONS
PVP_BUTTON = Button((0, 150, 0), 100, 200, 600, 100, "PVP")
PVC_BUTTON = Button((255, 211, 0), 100, 325, 600, 100, "PVC")
CVC_BUTTON = Button((200, 0, 0), 100, 450, 600, 100, "CVC")
RGC_BUTTON = Button((60, 0, 60), 100, 575, 275, 120, "RGC: OFF")
DELAY_BUTTON = Button((gray, gray, gray), 425, 575, 275, 120, "DELAY: " + str(delay_time))
BOT1_BUTTON = Button((100, 100, 150), 100, 720, 275, 120, "BOT 1:\n" + bot1_beh)
BOT2_BUTTON = Button((100, 100, 150), 425, 720, 275, 120, "BOT 2:\n" + bot2_beh)
HINTS_BUTTON = Button((0, 150, 0), 100, 870, 600, 105, "HINTS: ON")

# MAIN_MENU
def main_menu():
    global pvp, cvc, pvc, RGC_MOD, gray, game, delay_time, checkers, bot1_beh, bot2_beh, hints_on
    bbid1, bbid2 = 1, 2
    game = False
    while not game:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            mouse_pos = pg.mouse.get_pos()

            # CURSOR
            if (
                PVP_BUTTON.is_over(mouse_pos)
                or PVC_BUTTON.is_over(mouse_pos)
                or CVC_BUTTON.is_over(mouse_pos)
                or RGC_BUTTON.is_over(mouse_pos)
                or DELAY_BUTTON.is_over(mouse_pos)
                or BOT1_BUTTON.is_over(mouse_pos)
                or BOT2_BUTTON.is_over(mouse_pos)
                or HINTS_BUTTON.is_over(mouse_pos)
            ): pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            else: pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

            # GAME PARAMETERS
            if event.type == pg.MOUSEBUTTONUP:
                mouse_pos = event.pos
                if event.button == 1 or event.button == 4:
                    if PVP_BUTTON.is_over(mouse_pos):
                        pvp = True
                        cvc = False
                        pvc = False
                        game = True
                        checkers[0] = "White"
                        checkers[1] = "Black"

                    elif PVC_BUTTON.is_over(mouse_pos):
                        pvc = True
                        pvp = False
                        cvc = False
                        game = True
                        checkers[0] = "Bot"
                        checkers[1] = "Player"

                    elif CVC_BUTTON.is_over(mouse_pos):
                        cvc = True
                        pvp = False
                        pvc = False
                        game = True
                        checkers[0] = "B2 (White)"
                        checkers[1] = "B1 (Black)"

                    elif RGC_BUTTON.is_over(mouse_pos):
                        if RGC_MOD:
                            RGC_BUTTON.text = "RGC: OFF"
                            RGC_BUTTON.color = (60, 0, 60)
                        else:
                            RGC_BUTTON.text = "RGC: ON"
                            RGC_BUTTON.color = (230, 0, 153)
                        RGC_MOD = not RGC_MOD

                    elif DELAY_BUTTON.is_over(mouse_pos):
                        delay_time = (delay_time + 50) % 550
                        gray = delay_time // 25 + 30

                    elif BOT1_BUTTON.is_over(mouse_pos):
                        bbid1 = (bbid1 + 1) % len(types_of_game)
                        bot1_beh = types_of_game[bbid1]
                    elif BOT2_BUTTON.is_over(mouse_pos):
                        bbid2 = (bbid2 + 1) % len(types_of_game)
                        bot2_beh = types_of_game[bbid2]

                    elif HINTS_BUTTON.is_over(mouse_pos):
                        hints_on = not hints_on
                        if hints_on:
                            HINTS_BUTTON.text = "HINTS: ON"
                            HINTS_BUTTON.color = (0, 150, 0)
                        else:
                            HINTS_BUTTON.text = "HINTS: OFF"
                            HINTS_BUTTON.color = (0, 100, 0)

                elif event.button == 3 or event.button == 5:
                    if DELAY_BUTTON.is_over(mouse_pos):
                        delay_time = (delay_time - 50) % 550
                        if delay_time < 0:
                            delay_time = 0
                        gray = delay_time // 25 + 30

            if RGC_MOD:
                SET_RGC()
            else:
                SET_DEFAULT_COLORS()

            BOT1_BUTTON.text = "BOT 1:\n" + bot1_beh
            BOT2_BUTTON.text = "BOT 2:\n" + bot2_beh
            DELAY_BUTTON.color = (gray, gray, gray)
            DELAY_BUTTON.text = "DELAY: " + str(delay_time)

            screen_surf.fill(MAINBG)
            draw_main_buttons()
            pg.display.update()

main_menu()

# GAME
while game:
    if len(MAIN_BOARD.moves()[0]) == 0 and not game_over:
        MAIN_BOARD.player = not MAIN_BOARD.player
        if len(MAIN_BOARD.moves()[0]) == 0: game_over = True

    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

        xc, yc = pg.mouse.get_pos()[0] // 100, pg.mouse.get_pos()[1] // 100
        acc_tiles = MAIN_BOARD.moves()[0]

        if (
            (xc, yc) in acc_tiles and hints_on
            and (pvp or (pvc and MAIN_BOARD.player))
            or (xc == 2 and 810 < pg.mouse.get_pos()[1] < 910)
        ):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

        if event.type == pg.MOUSEBUTTONDOWN:
            if xc == 2 and 810 < event.pos[1] < 910:
                MAIN_BOARD = MAIN_BOARD.turn_on_main_menu()

        if pvp and not game_over:
            if event.type == pg.MOUSEBUTTONDOWN:
                if 0 <= xc < 8 and 0 <= yc < 8:
                    MAIN_BOARD.turn(xc, yc)

        if pvc and not game_over:
            if MAIN_BOARD.player:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if 0 <= xc < 8 and 0 <= yc < 8:
                        MAIN_BOARD.turn(xc, yc)
                        MAIN_BOARD.blit()
                        pg.display.update()
            else: # bot turn
                pg.time.delay(delay_time)
                MAIN_BOARD.computer_turn(bot1_beh)

    if cvc and not game_over:
        MAIN_BOARD.blit()
        pg.display.update()
        if MAIN_BOARD.player: 
            MAIN_BOARD.computer_turn(bot1_beh)
        else: 
            MAIN_BOARD.computer_turn(bot2_beh)
        pg.time.delay(delay_time)

    # WINNIG_TEXT
    edit_winning_text()

    # BLITS
    MAIN_BOARD.blit()
    pg.display.update()
