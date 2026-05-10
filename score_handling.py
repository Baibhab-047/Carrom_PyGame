import numpy as np

class Score:
    def __init__(self):
        self.scores = [0, 0]
        self.point_white = 20
        self.point_black = 10
        self.point_red = 50

    def update_score(self, player, coin_type):
        p_idx = player - 1
        if coin_type == 'white':
            self.scores[p_idx] += self.point_white
        elif coin_type == 'black':
            self.scores[p_idx] += self.point_black
        elif coin_type == 'red':
            self.scores[p_idx] += self.point_red


    def get_score(self, player):
        return self.scores[player - 1]