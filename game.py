import pygame
import numpy
from copy import deepcopy
from main import *

class Game(pygame.sprite.Sprite):
    def __init__(self, first_player, max_depth):
        '''
        Max depth indicates the maximum depth of the game tree traversal
        Player indicates the colour of the player on the current turn
        '''
        pygame.sprite.Sprite.__init__(self)
        self.turn = first_player # 'red' or 'blue' 
        self.max_depth = max_depth

    def change_turn(self):
        if self.turn == 'red':
            self.turn = 'blue'
        elif self.turn == 'blue':
            self.turn = 'red'
            
    def winner(self, player, board):
        '''
        Checks if the game has ended and returns the winner
        '''
        total_red = 0
        total_blue = 0
        
        for row in board:
            for space in row:
                if space == 1 or space == 3:
                    total_red += 1
                elif space == 2 or space == 4:
                    total_blue += 1
        
        if total_blue == 0 and total_red > 0: # red wins
            return 'red'

        if total_red == 0 and total_blue > 0: # blue wins
            return 'blue'

        if len(self.red_moves(board)) == 0 and player == 'red': # no possible red moves available, blue wins
            return 'blue'

        if len(self.blue_moves(board)) == 0 and player == 'blue': # no possible blue moves available, red wins
            return 'red'
        
        return False # game has not ended
        
    def game_evaluation(self, player, board):
        '''
        UTILITY FUNCTION
        Defines the final numeric value for the game when it's in its terminal state
        '''
        
        # if someone has won the game then return an infinite value
        if self.winner(player, board) == 'red': # human has won
            return float('-inf') 
        elif self.winner(player, board) == 'blue': # AI has won
            return float('inf')


        '''
        EVALUATION FUNCTION
        Defines an estimate of the expected utility numeric value from a given state
        Outputs a numeric value that represents the outcome and desirabiity of the board state
        Called when the game has not ended
        The human player is always striving for a more negative (minimum) value
        The AI is always striving for a more positive (maximum) value 
        A negative score indicates that the human player is in a disadvantaged position 
        '''
        
        # the numeric value of the board is determined by the number of the player's kings (+ 30) 
        # and the difference in number of pieces between the player and their opponent (+ 10 for each additional piece) 

        score = 0
        constant = 0
        red_kings = 0
        red_pieces = 0
        blue_kings = 0
        blue_pieces = 0

        for row in board:
            for space in row:
                if space == 1: # 1 represents a red piece (non-king)
                    red_pieces += 1
                elif space == 2: # 2 represents a blue piece (non-king) 
                    blue_pieces += 1
                elif space == 3: # 3 represents a red king
                    red_pieces += 1
                    red_kings += 1
                elif space == 4: # 4 represents a blue king 
                    blue_pieces += 1
                    blue_kings += 1
        
        if player == 'red':
            constant = -1
            score += 30 * red_kings
            difference = red_pieces - blue_pieces
            score += 10 * difference
        elif player == 'blue':
            constant = 1
            score += 30 * blue_kings
            difference = blue_pieces - red_pieces
            score += 10 * difference

        score = score*constant # the constant mediates the fact that the human wants a more negative score while AI wants more positive
        return score

    def get_move(self, board):
        '''
        Takes the board matrix as input and returns the best move
        '''
        best_board = None
        cur_depth = self.max_depth 
        (best_board, value) = self.max_move(board, cur_depth)

        return (best_board, value) 

    def max_move(self, max_board, cur_depth):
        '''
        Used to recursively traverse the tree, finds best move for blue player 
        '''
        return self.find_move(max_board, cur_depth-1, 'blue')

    def min_move(self, min_board, cur_depth):
        '''
        Used to recursively traverse the tree, finds best move for red player
        '''
        return self.find_move(min_board, cur_depth-1, 'red')

    def find_move(self, board, cur_depth, player):
        '''
        Finds the best move
        Returns the best board and its score 
        '''
        # checks if we are at a leaf
        if (self.winner(player, board) != False) or (cur_depth < 1):
            return (board, self.game_evaluation(player, board))

        # this executes if we are not at a leaf
        best_board = None
        
        if player == 'blue': # AI wants a board with inf score
            best_score = float('-inf')
            moves = self.blue_moves(board) # get board matrices of all possible red moves
            for move in moves:
                max_board = move
                value = self.min_move(max_board, cur_depth-1)[1]
                if value > best_score:
                    best_score = value
                    best_board = max_board
            
        
        elif player == 'red': # human wants a board with -inf score
            best_score = float('inf')
            moves = self.red_moves(board) # get board matrices of all possible blue moves
            for move in moves:
                min_board = board
                value = self.max_move(min_board, cur_depth-1)[1]
                if value < best_score:
                    best_score = value
                    best_board = min_board

        return (best_board, best_score)
            

    def blue_moves(self, board):
        '''
        Receives an input of the current board and returns an array of many board
        matrices representing all possible moves for the blue player
        '''
        possible_moves = []

        for i in range(len(board)):
            row = board[i]
            for j in range(len(row)):
                new_board = deepcopy(board)
                space = row[j]
                if space == 2 or space == 4: # 2 represents a blue piece (non-king) and 4 represents a blue king 
                    if j>0 and i<7 and board[i+1][j-1] == 0: # checks if the space diagnally left and forward is empty 
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        if i+1 == 7 and space == 2: # the piece has reached the opposite side and becomes a king 
                            new_board[i+1][j-1] = 4
                        else: 
                            new_board[i+1][j-1] = space
                        possible_moves.append(new_board)                   
                    
                    if j<7 and i<7 and board[i+1][j+1] == 0: # checks if the space diagnally right and forward is empty
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        if i+1 == 7 and space == 2: # the piece has reached the opposite side and becomes a king 
                            new_board[i+1][j+1] = 4
                        else:
                            new_board[i+1][j+1] = space
                        possible_moves.append(new_board)

                    if space == 4 and i>0 and j>0 and board[i-1][j-1] == 0: # checks if the space diagnally left and back is empty
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        new_board[i-1][j-1] = space
                        possible_moves.append(new_board)

                    if space == 4 and i>0 and j<7 and board[i-1][j+1] == 0: # checks if the space diagnally right and back is empty
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        new_board[i-1][j+1] = space
                        possible_moves.append(new_board)

                    '''
                    This nested function is used to find all possible captures of the red pieces by the blue pieces
                    It utilizes recursion to find all combinations of jumps when there are multiple options available 
                    '''
                    
                    def keep_jumping_blue(new_board, cur_i, cur_j, cur_piece):

                        # checks if we can jump a red piece diagonally forward and left 
                        if cur_j>1 and cur_i<6 and (new_board[cur_i+1][cur_j-1] == 1 or new_board[cur_i+1][cur_j-1] == 3):
                            if new_board[cur_i+2][cur_j-2] == 0:
                                this_piece = cur_piece
                                if cur_i+2 == 7 and this_piece == 2:
                                    this_piece = 4 # the piece has reached the opposite side and becomes a king
                                some_board = deepcopy(new_board)
                                some_board[cur_i+2][cur_j-2] = this_piece 
                                some_board[cur_i+1][cur_j-1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_blue(some_board, cur_i+2, cur_j-2, this_piece)
                        
                        # checks if we can jump a red piece diagonally forward and right
                        if cur_j<6 and cur_i<6 and (new_board[cur_i+1][cur_j+1] == 1 or new_board[cur_i+1][cur_j+1] == 3):
                            if new_board[cur_i+2][cur_j+2] == 0:
                                this_piece = cur_piece
                                if cur_i+2 == 7 and this_piece == 2:
                                    this_piece = 4 # the piece has reached the opposite side and becomes a king
                                some_board = deepcopy(new_board)
                                some_board[cur_i+2][cur_j+2] = this_piece 
                                some_board[cur_i+1][cur_j+1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_blue(some_board, cur_i+2, cur_j+2, this_piece)

                        # checks if we can jump a red piece diagonally back and left 
                        if cur_piece == 4 and cur_j>1 and cur_i>1 and (new_board[cur_i-1][cur_j-1] == 1 or new_board[cur_i-1][cur_j-1] == 3):
                            if new_board[cur_i-2][cur_j-2] == 0:
                                some_board = deepcopy(new_board)
                                some_board[cur_i-2][cur_j-2] = cur_piece 
                                some_board[cur_i-1][cur_j-1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_blue(some_board, cur_i-2, cur_j-2, cur_piece)

                        # checks if we can jump a red piece diagonally back and right 
                        if cur_piece == 4 and cur_j<6 and cur_i>1 and (new_board[cur_i-1][cur_j+1] == 1 or new_board[cur_i-1][cur_j+1] == 3):
                            if new_board[cur_i-2][cur_j+2] == 0:
                                some_board = deepcopy(new_board)
                                some_board[cur_i-2][cur_j+2] = cur_piece 
                                some_board[cur_i-1][cur_j+1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_blue(some_board, cur_i-2, cur_j+2, cur_piece)
                          
                        return new_board                                

                    new_board = deepcopy(board)
                    cur_i = i
                    cur_j = j
                    cur_piece = space
                    keep_jumping_blue(new_board, cur_i, cur_j, cur_piece)
       
        return possible_moves


    def red_moves(self, board):
        '''
        Receives an input of the current board and returns an array of many board
        matrices representing all possible moves for the red player
        '''
        possible_moves = []

        for i in range(len(board)):
            row = board[i]
            for j in range(len(row)):                
                space = row[j]
                if space == 1 or space == 3: # 1 represents a red piece (non-king) and 3 represents a red king 
                    if j>0 and i>0 and board[i-1][j-1] == 0: # checks if the space diagnally left and forward is empty 
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        if i-1 == 0 and space == 1: # the piece has reached the opposite side and becomes a king 
                            new_board[i-1][j-1] = 3
                        else: 
                            new_board[i-1][j-1] = space
                        possible_moves.append(new_board)                   
                    
                    if j<7 and i>0 and board[i-1][j+1] == 0: # checks if the space diagnally right and forward is empty
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        if i-1 == 0 and space == 1: # the piece has reached the opposite side and becomes a king 
                            new_board[i-1][j+1] = 3
                        else:
                            new_board[i-1][j+1] = space
                        possible_moves.append(new_board)

                    if space == 3 and i<7 and j>0 and board[i+1][j-1] == 0: # checks if the space diagnally left and back is empty
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        new_board[i+1][j-1] = space
                        possible_moves.append(new_board)

                    if space == 3 and i<7 and j<7 and board[i+1][j+1] == 0: # checks if the space diagnally right and back is empty
                        new_board = deepcopy(board)
                        new_board[i][j] = 0
                        new_board[i+1][j+1] = space
                        possible_moves.append(new_board)                        

                    
                    '''
                    This nested function is used to find all possible captures of the blue pieces by the red pieces
                    It utilizes recursion to find all combinations of jumps when there are multiple options available 
                    '''
                    
                    def keep_jumping_red(new_board, cur_i, cur_j, cur_piece):

                        # checks if we can jump a blue piece diagonally forward and left 
                        if cur_j>1 and cur_i>1 and (new_board[cur_i-1][cur_j-1] == 2 or new_board[cur_i-1][cur_j-1] == 4):
                            if new_board[cur_i-2][cur_j-2] == 0:
                                this_piece = cur_piece
                                if cur_i-2 == 0 and this_piece == 1:
                                    this_piece = 3 # the piece has reached the opposite side and becomes a king
                                some_board = deepcopy(new_board)
                                some_board[cur_i-2][cur_j-2] = this_piece 
                                some_board[cur_i-1][cur_j-1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_red(some_board, cur_i-2, cur_j-2, this_piece)
                        
                        # checks if we can jump a blue piece diagonally forward and right
                        if cur_j<6 and cur_i>1 and (new_board[cur_i-1][cur_j+1] == 2 or new_board[cur_i-1][cur_j+1] == 4):
                            if new_board[cur_i-2][cur_j+2] == 0:
                                this_piece = cur_piece
                                if cur_i-2 == 0 and this_piece == 1:
                                    this_piece = 3 # the piece has reached the opposite side and becomes a king
                                some_board = deepcopy(new_board)
                                some_board[cur_i-2][cur_j+2] = this_piece 
                                some_board[cur_i-1][cur_j+1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_red(some_board, cur_i-2, cur_j+2, this_piece)
                            
                        # checks if we can jump a blue piece diagonally back and left 
                        if cur_piece == 3 and cur_j>1 and cur_i<6 and (new_board[cur_i+1][cur_j-1] == 2 or new_board[cur_i+1][cur_j-1] == 4):
                            if new_board[cur_i+2][cur_j-2] == 0:
                                some_board = deepcopy(new_board)
                                some_board[cur_i+2][cur_j-2] = cur_piece 
                                some_board[cur_i+1][cur_j-1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_red(some_board, cur_i+2, cur_j-2, cur_piece)

                        # checks if we can jump a blue piece diagonally back and right 
                        if cur_piece == 3 and cur_j<6 and cur_i<6 and (new_board[cur_i+1][cur_j+1] == 2 or new_board[cur_i+1][cur_j+1] == 4):
                            if new_board[cur_i+2][cur_j+2] == 0:
                                some_board = deepcopy(new_board)
                                some_board[cur_i+2][cur_j+2] = cur_piece 
                                some_board[cur_i+1][cur_j+1] = 0 # jumped piece disappears
                                some_board[cur_i][cur_j] = 0 # original space is now empty
                                possible_moves.append(some_board)
                                keep_jumping_red(some_board, cur_i+2, cur_j+2, cur_piece)
                          
                        return new_board

                    new_board = deepcopy(board)
                    cur_i = i
                    cur_j = j
                    cur_piece = space
                    keep_jumping_red(new_board, cur_i, cur_j, cur_piece)
                    
        return possible_moves  

