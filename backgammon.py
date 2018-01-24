import random
import copy


def run():
    bg = Backgammon()
    bg.print_board()
    bg.roll_dice()
    bg.calc_legal_next_states_white_move()
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

    def calc_legal_next_states_white_move(self):
        lowest_pips = self.white_pips
        
        if len(self.last_dice) == 2:
            in_last_quarter_start = self.all_counters_in_last_quarter(self.state['white_counters'][:], 'white')
            for move_order in [[0, 1], [1, 0]]:
                first_dice = self.last_dice[move_order[0]]
                second_dice = self.last_dice[move_order[1]]
                for i in range(25):  # this means move counter in position i
                    if self.state['white_counters'][i] <= 0:
                        continue  # cannot move a counter from a point with no counters
                    if self.state['white_counters'][0] > 0 and i != 0:
                        continue  # if there is a counter off the board you need to move it first
                    if i + first_dice <= 24 and self.state['black_counters'][i + first_dice] > 1:
                        continue  # cannot move to a point with 2 or more opposing counters
                    if not in_last_quarter_start and i + first_dice > 24:
                        continue  # cannot move a counter off the board unless all your counters in the last quarter
                    # in theory a legal move so create a new state to update
                    new_state = {'white_counters': copy.copy(self.state['white_counters']),
                                   'black_counters': copy.copy(self.state['black_counters'])}
                    if self.state['black_counters'][i + first_dice] == 1:
                        new_state['black_counters'][i + first_dice] == 0
                        new_state['black_counters'][25] += 1  # if opponents pieces jumped on send to start
                    if i + first_dice > 24:
                        new_state['white_counters'][25] += 1
                    else:
                        new_state['white_counters'][i + first_dice] += 1
                    new_state['white_counters'][i] -= 1
                    for j in range(25):
                        if new_state['white_counters'][j] <= 0:
                            continue  # cannot move a counter from a point with no counters
                        if new_state['white_counters'][0] > 0 and j != 0:
                            continue  # if there is a counter off the board you need to move it first
                        if j + second_dice <= 24 and new_state['black_counters'][j + second_dice] > 1:
                            continue  # cannot move to a point with 2 or more opposing counters
                        if not in_last_quarter_start and j + second_dice > 24:
                            continue  # cannot move a counter off the board unless all your counters in the last quarter
                        # in theory a legal move so create a new state to update
                        final_state = {'white_counters': copy.copy(new_state['white_counters']),
                                       'black_counters': copy.copy(new_state['black_counters'])}
                        if new_state['black_counters'][j + second_dice] == 1:
                            final_state['black_counters'][j + second_dice] == 0
                            final_state['black_counters'][25] += 1  # if opponents pieces jumped on send to start
                        if j + second_dice > 24:
                            final_state['white_counters'][25] += 1
                        else:
                            final_state['white_counters'][j + second_dice] += 1
                        final_state['white_counters'][j] -= 1
                        print '\n\nfinal state option, display below, pips = ', self.return_pips(final_state)
                        print 'move posn ', i, ' counter ', first_dice, ' places, move posn ', j, ' counter ', second_dice, ' places'
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