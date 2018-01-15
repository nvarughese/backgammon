


class Backgammon:
    def __init__(self):
        self.state = {}
        for i in range(26):
            self.state[i] = {'counters': 0, 'colour': ' '}





    def print_board(self):
        for i in range(13, 26):
            print self.state[i]['colour']

        for i in range(13, 26):
            print self.state[i]['counters']

        for i in range(12, -1, -1):
            print self.state[i]['counters']

        for i in range(12, -1, -1):
            print self.state[i]['colour']
