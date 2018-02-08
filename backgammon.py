import random
import copy
import pygame
import time


OFF = 'off'
ON = 'on'


def run():
    bg = Backgammon()
    bg.draw((4, 3))
    bg.state['white'] = [3, 0, 0, 0, 0, 4, 7, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, 0, 6]
    time.sleep(3)
    bg.draw((1, 5))
    '''
    bg.print_board()
    bg.roll_dice()
    bg.calc_legal_next_states('white')
    bg.calc_legal_next_states('black')
    print 'bg.white_pips, bg.black_pips = ', bg.white_pips, bg.black_pips
    '''
    raw_input("Press Enter to continue...")

class Backgammon:
    def __init__(self):

        # old english rules mean you are limited to 5 counters on a single point
        self.use_old_english_rules = False
        self.state = {}
        self.state['white'] = [3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,
                                  0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, 0, 6]
        self.state['black'] = [8, 0, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, 0,
                                  5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2]
        self.last_dice = []
        self.white_pips, self.black_pips = 0, 0
        self.calc_pips()
        self.next_states = []


        self.init = True
        self.roll = None


    def roll_dice(self):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        if d1 != d2:
            self.last_dice = [d1, d2]
        else:
            self.last_dice = [d1, d2] #, d1, d2] # for the moment do not count doubles
        print 'dice rolled as ', d1, d2

    def get_valid_and_state(self, state, colour, counter_posn, dice_roll, in_last_quarter):
        opp_colour = {'white': 'black', 'black': 'white'}[colour]
        start_posn = {'white': 0, 'black': 25}[colour]
        end_posn = {'white': 25, 'black': 0}[colour]
        opp_start_posn, opp_end_posn = end_posn, start_posn
        direction = {'white': 1, 'black': -1}[colour]

        if state[colour][counter_posn] <= 0:
            return False, state  # cannot move a counter from a point with no counters

        if counter_posn == end_posn:
            return False, state  # cannot move a counter that is already at the end position

        if state[colour][start_posn] > 0 and counter_posn != start_posn:
            return False, state  # if there is a counter off the board you need to move it first

        new_counter_posn = counter_posn + (direction * dice_roll)
        if 1 <= new_counter_posn <= 24 and state[opp_colour][new_counter_posn] > 1:
            return False, state  # cannot move to a point with 2 or more opposing counters

        if not in_last_quarter and (counter_posn + (direction * dice_roll) > 24 or counter_posn + (direction * dice_roll) < 1):
            return False, state  # cannot move a counter off the board unless all your counters in the last quarter

        # in theory a legal move so create a new state to update
        new_state = {'white': copy.copy(state['white']),
                     'black': copy.copy(state['black'])}
        if state[opp_colour][new_counter_posn] == 1:
            new_state[opp_colour][new_counter_posn] = 0
            new_state[opp_colour][opp_start_posn] += 1  # if opponents pieces jumped on send to start
        if new_counter_posn < 1 or new_counter_posn > 24:
            new_state[colour][end_posn] += 1
        else:
            new_state[colour][new_counter_posn] += 1
        new_state[colour][counter_posn] -= 1
        return True, new_state

    def calc_legal_next_states(self, colour):
        lowest_pips = {'white': self.white_pips, 'black': self.black_pips}[colour]
        final_states = []
        if len(self.last_dice) == 2:
            in_last_quarter_start = self.all_counters_in_last_quarter(self.state[colour][:], colour)
            for move_order in [[0, 1], [1, 0]]:
                first_dice, second_dice = self.last_dice[move_order[0]], self.last_dice[move_order[1]]
                for first_counter_posn in range(25):  # this means move counter in position first_counter_posn
                    valid_move, new_state = self.get_valid_and_state(self.state, colour, first_counter_posn, first_dice,
                                                                     in_last_quarter_start)
                    if not valid_move:
                        continue
                    in_last_quarter_next = self.all_counters_in_last_quarter(new_state[colour][:], colour)
                    for second_counter_posn in range(26):
                        valid_move, final_state = self.get_valid_and_state(new_state, colour, second_counter_posn,
                                                                           second_dice, in_last_quarter_next)
                        if not valid_move:
                            continue
                        white_pips, black_pips = self.return_pips(final_state)
                        final_pips = {'white': white_pips, 'black': black_pips}[colour]
                        print '\n\nfinal state option after ', colour, ' move, display below, pips = ', final_pips
                        print 'move posn ', first_counter_posn, ' counter ', first_dice, ' places, move posn ', \
                            second_counter_posn, ' counter ', second_dice, ' places'
                        self.print_temp_board(final_state)
                        print 'final_pips, lowest_pips = ', final_pips, lowest_pips
                        if final_pips <= lowest_pips:
                            if final_pips < lowest_pips:
                                final_states = [final_state]
                                lowest_pips = final_pips
                                print 'new low in pips, starting final states from scratch'
                            else:
                                # in this part compare the final state to previous states to check for duplicates
                                is_duplicate_state = False
                                for state in final_states:
                                    if final_state == state:
                                        is_duplicate_state = True
                                if not is_duplicate_state:
                                    print 'not a duplicate state adding to final_states'
                                    final_states.append(final_state)
                                else:
                                    print 'this is a duplicate state, ignoring'
        print 'final_states = ', final_states

    def all_counters_in_last_quarter(self, counter_list, side):
        if side == 'white':
            for i in range(19):
                if counter_list[i] > 0:
                    return False
            return True
        if side == 'black':
            for i in range(7, 26):
                if counter_list[i] > 0:
                    return False
            return True

    def return_pips(self, state):
        white_pips, black_pips = 0, 0
        for steps_to_go in range(0, 26):
            white_pips += steps_to_go * state['white'][-1 - steps_to_go]
        for steps_to_go in range(0, 26):
            black_pips += steps_to_go * state['black'][steps_to_go]
        return white_pips, black_pips

    def calc_pips(self):
        self.white_pips, self.black_pips = self.return_pips(self.state)

    def print_temp_board(self, state):
        print 'top    white : ->', state['white'][13:19], state['white'][19:25], '->', state['white'][25]
        print 'top    black : <-', state['black'][13:19], state['black'][19:25], '<-', state['black'][25]
        print ''
        print 'bottom white : <-', state['white'][7:13][::-1], state['white'][1:7][::-1], '<-', state['white'][0]
        print 'bottom black : ->', state['black'][7:13][::-1], state['black'][1:7][::-1], '->', state['black'][0]

    def print_board(self):
        self.print_temp_board(self.state)

    ### code taken from someone elses github, work out what it does



    def draw(self, roll=None):
        if roll is None:
            roll = self.roll
        else:
            self.roll = roll

        self.drawGui(roll)

    def initGui(self):
        pygame.init()
        WIDTH, HEIGHT = 800, 425
        size = WIDTH, HEIGHT

        WOFFSET_TOP, HOFFSET_TOP, HOFFSET_BOT = 57, 12, 370
        WSKIP, WMID, HSKIP, BAR_SKIP, WBAR = 55, 32, 30, 32, 376

        self.grid_locs = []
        for i in range(24):
            mid = 0
            hoff = HOFFSET_TOP
            hskip = HSKIP
            k = 11 - i
            if i < 6 or i > 17:
                mid = WMID
            if i > 11:
                hoff = HOFFSET_BOT
                hskip = -hskip
                k = i - 12
            self.grid_locs.append([(WOFFSET_TOP + k * WSKIP + mid, hoff + j * hskip) for j in range(6)])
        # self.bar_locs = {'black': [(376, 142), (376, 110)], 'white': [(376, 243), (376, 275)]}
        self.bar_locs = {'black': [(WBAR, 142 - i * BAR_SKIP) for i in range(6)],
                         'white': [(WBAR, 243 + i * BAR_SKIP) for i in range(6)]}
        self.board_img = pygame.transform.scale(pygame.image.load('images/board.png'), size)
        self.screen = pygame.display.set_mode(self.board_img.get_rect().size)
        self.token_images = {'black': pygame.image.load('images/blackPiece.png'), \
                       'white': pygame.image.load('images/whitePiece.png')}
        self.dies = [pygame.transform.scale(pygame.image.load('images/die%d.png' % i), (35, 35)) \
                     for i in range(1, 7)]
        self.off_images = {'black': pygame.transform.scale(pygame.image.load('images/blackOff.png'), (40, 18)), \
                           'white': pygame.transform.scale(pygame.image.load('images/whiteOff.png'), (40, 18))}

        outOff, bOffH, wOffH, offSkip = 748, 391, 11, 9
        self.off_locs = {'black': [(outOff, bOffH - i * offSkip) for i in range(19)],
                         'white': [(outOff, wOffH + i * offSkip) for i in range(19)]}


    def drawGui(self, roll):
        if self.init:
            self.initGui()
        self.screen.blit(self.board_img, self.board_img.get_rect())
        self.screen.blit(self.dies[roll[0] - 1], (180, 190))
        self.screen.blit(self.dies[roll[1] - 1], (220, 190))
        for colour in ['white', 'black']:
            for posn, counters in enumerate(self.state[colour]):
                if counters == 0 or posn in [0, 25]:
                    continue
                for i in range(min(counters, 6)):
                    self.screen.blit(self.token_images[colour], self.grid_locs[24 - posn][i])

        if self.state['white'][0] > 0:
            for i in range(self.state['white'][0]):
                self.screen.blit(self.token_images['white'], self.bar_locs['white'][i])
        if self.state['black'][25] > 0:
            for i in range(self.state['black'][25]):
                self.screen.blit(self.token_images['black'], self.bar_locs['black'][i])
        if self.state['white'][25] > 0:
            for i in range(self.state['white'][25]):
                self.screen.blit(self.off_images['white'], self.off_locs['white'][i])
        if self.state['black'][0] > 0:
            for i in range(self.state['black'][0]):
                self.screen.blit(self.off_images['black'], self.off_locs['black'][i])

        pygame.display.flip()

    def gridLocFromPos(self, pos, player):
        tx, ty = self.token_images['black'].get_rect().size

        def on_piece(pieceLoc, pos, sizex, sizey):
            px, py = pieceLoc
            tx, ty = pos
            if px < tx < px + sizex:
                if py < ty < py + sizey:
                    return True
            return False

        # find out if we are on the grid
        for i, col in enumerate(self.grid):
            for loc in self.grid_locs[23 - i]:
                if on_piece(loc, pos, tx, ty):
                    return i

        # find out if we are on the bar
        for i, bp in enumerate(self.bar_pieces[player]):
            if on_piece(self.bar_locs[player][i], pos, tx, ty):
                return ON

        # find out if we are removing pieces
        off_base = self.off_locs['white'][0] if player == 'white' else self.off_locs['black'][-1]
        off_height = 200
        off_width, _ = self.off_images['black'].get_rect().size
        if on_piece(off_base, pos, off_width, off_height):
            return OFF

        return None




if __name__ == '__main__':
    run()


## todo
# 1 connect up human player
# 2 connect up computer player
# 3 work out end of game
# 4 make 1 ply cpu
# 5 make 2 ply cpu