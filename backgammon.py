import random
import copy


def run():
    bg = Backgammon()
    bg.print_board()
    bg.roll_dice()
    bg.calc_legal_next_states('white')
    bg.calc_legal_next_states('black')
    print 'bg.white_pips, bg.black_pips = ', bg.white_pips, bg.black_pips


class Backgammon:
    def __init__(self):

        # old english rules mean you are limited to 5 counters on a single point
        self.use_old_english_rules = False
        self.state = {}
        self.state['white_counters'] = [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, \
                                           0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, 0, 0]
        self.state['black_counters'] = [0, 0, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, 0, \
                                           5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0]
        self.last_dice = []
        self.white_pips, self.black_pips = 0, 0
        self.calc_pips()
        self.next_states = []

    def roll_dice(self):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        if d1 != d2:
            self.last_dice = [d1, d2]
        else:
            self.last_dice = [d1, d2] #, d1, d2] # for the moment do not count doubles
        print 'dice rolled as ', d1, d2

    def get_valid_and_state(self, state, colour, counter_posn, dice_roll, in_last_quarter):
        ############## double check this function, didnt have time to finish
        colour_counter_str = {'white': 'white_counters', 'black': 'black_counters'}[colour]
        opp_colour_counter_str = {'white': 'black_counters', 'black': 'white_counters'}[colour]
        home_posn = {'white': 0, 'black': 25}[colour]
        end_posn = {'white': 25, 'black': 0}[colour]
        opp_home_posn, opp_end_posn = end_posn, home_posn
        direction = {'white': 1, 'black': -1}[colour]

        if state[colour_counter_str][counter_posn] <= 0:
            return False, state  # cannot move a counter from a point with no counters

        if state[colour_counter_str][home_posn] > 0 and counter_posn != home_posn:
            return False, state  # if there is a counter off the board you need to move it first

        new_counter_posn = counter_posn + (direction * dice_roll)
        if 1 <= new_counter_posn <= 24 and state[opp_colour_counter_str][new_counter_posn] > 1:
            return False, state  # cannot move to a point with 2 or more opposing counters

        if not in_last_quarter and counter_posn + dice_roll > 24:
            return False, state  # cannot move a counter off the board unless all your counters in the last quarter

        # in theory a legal move so create a new state to update
        new_state = {'white_counters': copy.copy(state['white_counters']),
                     'black_counters': copy.copy(state['black_counters'])}
        if state[opp_colour_counter_str][new_counter_posn] == 1:
            new_state[opp_colour_counter_str][new_counter_posn] = 0
            new_state[opp_colour_counter_str][opp_home_posn] += 1  # if opponents pieces jumped on send to start
        if new_counter_posn < 1 or new_counter_posn > 24:
            new_state[colour_counter_str][end_posn] += 1
        else:
            new_state[colour_counter_str][new_counter_posn] += 1
        new_state[colour_counter_str][counter_posn] -= 1
        return True, new_state

    def calc_legal_next_states(self, colour):
        lowest_pips = {'white': self.white_pips, 'black': self.black_pips}[colour]
        final_states = []
        if len(self.last_dice) == 2:
            in_last_quarter_start = self.all_counters_in_last_quarter(self.state[colour + '_counters'][:], colour)
            for move_order in [[0, 1], [1, 0]]:
                first_dice, second_dice = self.last_dice[move_order[0]], self.last_dice[move_order[1]]
                for first_counter_posn in range(25):  # this means move counter in position first_counter_posn
                    valid_move, new_state = self.get_valid_and_state(self.state, colour, first_counter_posn, first_dice,
                                                                     in_last_quarter_start)
                    if not valid_move:
                        continue
                    in_last_quarter_next = self.all_counters_in_last_quarter(new_state[colour + '_counters'][:], colour)
                    for second_counter_posn in range(25):
                        valid_move, final_state = self.get_valid_and_state(new_state, colour, second_counter_posn,
                                                                           second_dice, in_last_quarter_next)
                        if not valid_move:
                            continue
                        final_pips = self.return_pips(final_state)[colour]
                        print '\n\nfinal state option after ', colour, ' move, display below, pips = ', self.return_pips(final_state)
                        print 'move posn ', first_counter_posn, ' counter ', first_dice, ' places, move posn ', \
                            second_counter_posn, ' counter ', second_dice, ' places'
                        if final_pips <= lowest_pips:
                            if final_pips < lowest_pips:
                                final_states = [final_state]
                            else:
                                # in this part compare the final state to previous states to check for duplicates
                                for state in final_states:
                                    if final_state != state:
                        self.print_temp_board(final_state)



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
            white_pips += steps_to_go * state['white_counters'][-1 - steps_to_go]
        for steps_to_go in range(0, 26):
            black_pips += steps_to_go * state['black_counters'][steps_to_go]
        return white_pips, black_pips


    def calc_pips(self):
        self.white_pips, self.black_pips = 0, 0
        for steps_to_go in range(0, 26):
            self.white_pips += steps_to_go * self.state['white_counters'][-1 - steps_to_go]
        for steps_to_go in range(0, 26):
            self.black_pips += steps_to_go * self.state['black_counters'][steps_to_go]


    def print_temp_board(self, state):
        print 'top    white counters : ->', state['white_counters'][13:19], state['white_counters'][19:25], \
            '->', state['white_counters'][25]
        print 'top    black counters : <-', state['black_counters'][13:19], state['black_counters'][19:25], \
            '<-', state['black_counters'][25]
        print ''
        print 'bottom white counters : <-', state['white_counters'][7:13][::-1], state['white_counters'][1:7][::-1], \
            '<-', state['white_counters'][0]
        print 'bottom black counters : ->', state['black_counters'][7:13][::-1], state['black_counters'][1:7][::-1], \
            '->', state['black_counters'][0]

    def print_board(self):
        self.print_temp_board(self.state)


if __name__ == '__main__':
    run()