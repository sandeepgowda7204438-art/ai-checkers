# -*- coding: utf-8 -*-

import pygame
import numpy
import math
import os

from game import *

black, white, red, blue = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)
size = 50 # size of the tiles on the board in pixels 
surface_sz = 400 # surface size in pixels

# the board holds a matrix representation of the positions of our game pieces 
board = numpy.zeros((8,8))

class Piece(pygame.sprite.Sprite):
    def __init__(self, x_position, y_position, player):
        pygame.sprite.Sprite.__init__(self)
        
        self.player = player # a colour
        self.radius = 20
        (self.x_pixel, self.y_pixel) = (x_position, y_position) # the location at which the piece is initialized

    def get_colour(num):
        if num == 1 or num == 3:
            return red
        elif num == 2 or num == 4:
            return blue
        else:
            return None

    def capture(x_coord, y_coord, colour):
        """
        Removes a piece from the matrix.
        """
        board[y_coord][x_coord] = 0
        pieces.remove(*getPixels(x_coord, y_coord), colour) # remove piece from group

class Space(pygame.sprite.Sprite):
    def __init__(self, shape, color, x_pos, y_pos):
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()
        self.rect = pygame.draw.rect(screen, color, shape)
        self.color = color
        self.x_pos = x_pos
        self.y_pos = y_pos

def draw_board(board):
    '''
    Updates the position of the pieces on the board after every move, by copying the board array 
    '''
    draw_background() # we must make the board blank before drawing the pieces again, or else the old positions will remain drawn 
    screen = pygame.display.get_surface()
    radius = 20
    i = 0
    for row in board:
        j = 0
        for space in row:
            if space == 1: # red non-king
                pygame.draw.circle(screen, red, getPixels(j,i), radius)
            elif space == 2:# blue non-king
                pygame.draw.circle(screen, blue, getPixels(j,i), radius)
            elif space == 3: # red king
                pygame.draw.circle(screen, (255, 153, 153), getPixels(j,i), radius)
            elif space == 4: # blue king 
                pygame.draw.circle(screen, (153, 153, 255), getPixels(j,i), radius)
            j+=1
        i+=1
    
def draw_background():
    '''
    Used to reset the board by making it blank without any pieces
    It is only used by draw_board after each move
    Note that it is not used when the board is initially set up in main() because we do not want to create new Space objects every time 
    '''
    screen = pygame.display.get_surface()
    # overpaint a smaller rectangle on the main surface
    for i in range(8): # x position
        for j in range(8): # y position
            small_rect = (size*i, size*j, size, size)
            if i % 2 != j % 2: # the inequality ensures that the bottom right corner is white for both players (part of the rules)
                # create a black square at alternating gridpoints
                pygame.draw.rect(screen, black, small_rect)
            else:
                pygame.draw.rect(screen, white, small_rect)

# Initialize game groups
pieces = pygame.sprite.RenderUpdates()
spaces = pygame.sprite.RenderUpdates()

def main():
    pygame.init()

    # Main Game object with first player as red (human) and a maximum depth of 5 for the game tree traversal
    game = Game('red', 5) 
    
    # Create surface of (width, height) and its window
    main_surface = pygame.display.set_mode((surface_sz, surface_sz))
    pygame.display.set_caption('Checkers')

    # Fill background
    main_surface.fill(white)

    # Create the board
    for i in range(8): # x position
        for j in range(8): # y position
            small_rect = (size*i, size*j, size, size)
            if i % 2 != j % 2: # the inequality ensures that the bottom right corner is white for both players (part of the rules)
                # create a black square at alternating gridpoints 
                spaces.add(Space(small_rect, black, i, j))
            else:
                spaces.add(Space(small_rect, white, i, j))
                

    # add the pieces to the board matrix
    for i in range(8): # x position
        for j in range(8): # y position            
            if i % 2 != j % 2:
                if j < 3:
                    blue_piece = Piece(*getPixels(i,j),blue)
                    pieces.add(blue_piece)
                    board[j][i] = 2 # updating the matrix with "2" for blue pieces
                elif j > 4:
                    red_piece = Piece(*getPixels(i,j),red)
                    pieces.add(red_piece)
                    board[j][i] = 1 # updating the matrix with "1" for red pieces

    draw_board(board) # adding the pieces to the board now that they have been added to the board matrix 
    
    # display surface
    pygame.display.flip()

    piece_selected = pygame.sprite.GroupSingle()
    space_selected = pygame.sprite.GroupSingle()
    temp_selected = pygame.sprite.GroupSingle()
    second_click = False # this variable is used to differentiate the two click events (MOUSEBUTTONDOWN) 
    awaiting_red = True
    running = True
       
    while running:

        # human's turn
        if game.turn == 'red':
            awaiting_red = True
            while awaiting_red:
                jump_possible = False
                bad_move = False
                
                for event in pygame.event.get(): 
                    if event.type == pygame.QUIT: # if window close button clicked then leave game loop
                        running = False
                        break
                        
                    if event.type == pygame.MOUSEBUTTONDOWN and second_click == False: # click piece to move 
                        pos = pygame.mouse.get_pos()
                        temp_selected.add(space for space in spaces if space.rect.collidepoint(pos)) 
                        my_space = temp_selected.sprite
                        if board[my_space.y_pos][my_space.x_pos] != 0: # we are selecting a non-empty space
                            piece_selected.add(my_space)
                            second_click = True
                              
                    elif event.type == pygame.MOUSEBUTTONDOWN and second_click == True: # click new position for piece                      
                        pos = pygame.mouse.get_pos()
                        space_selected.add(space for space in spaces if space.rect.collidepoint(pos)) # position for piece to move

                        # ensuring that red non-kings cannot move backwards 
                        if board[piece_selected.sprite.y_pos][piece_selected.sprite.x_pos] == 1 and space_selected.sprite.y_pos>piece_selected.sprite.y_pos:
                            print("This piece cannot move backward. Make a different move.")
                            bad_move = True
                        
                        # if player chooses to move by one diagonal, allow move
                        elif dist(piece_selected.sprite.x_pos, space_selected.sprite.x_pos, piece_selected.sprite.y_pos, \
                                space_selected.sprite.y_pos) == math.sqrt(2):
                            # updating the board array 
                            my_color = board[piece_selected.sprite.y_pos][piece_selected.sprite.x_pos]
                            board[piece_selected.sprite.y_pos][piece_selected.sprite.x_pos] = 0

                            if space_selected.sprite.y_pos == 0:
                                board[space_selected.sprite.y_pos][space_selected.sprite.x_pos] = 3 # becomes a red king
                            else:
                                board[space_selected.sprite.y_pos][space_selected.sprite.x_pos] = my_color

                        # if player chooses to jump and capture a blue piece, allow move and check if a consecutive jump can occur 
                        elif dist(piece_selected.sprite.x_pos, space_selected.sprite.x_pos, piece_selected.sprite.y_pos, \
                                space_selected.sprite.y_pos) == 2 * math.sqrt(2):
                            x_jumped = int((space_selected.sprite.x_pos - piece_selected.sprite.x_pos)/2) + piece_selected.sprite.x_pos
                            y_jumped = int((space_selected.sprite.y_pos - piece_selected.sprite.y_pos)/2) + piece_selected.sprite.y_pos

                            # jumped a piece
                            if board[y_jumped][x_jumped] != 0 and Piece.get_colour(board[y_jumped][x_jumped]) != Piece.get_colour(my_color):

                                Piece.capture(x_jumped, y_jumped, Piece.get_colour(board[y_jumped][x_jumped]))
                                board[piece_selected.sprite.y_pos][piece_selected.sprite.x_pos] = 0
                                
                                if space_selected.sprite.y_pos == 0:
                                    board[space_selected.sprite.y_pos][space_selected.sprite.x_pos] = 3 # becomes a red king
                                else:
                                    board[space_selected.sprite.y_pos][space_selected.sprite.x_pos] = my_color

                                cur_x = space_selected.sprite.x_pos
                                cur_y = space_selected.sprite.y_pos
                                blue_nums = [2,4]

                                # checking if another jump is possible
                                if (cur_x > 1) and (cur_x < 6) and (cur_y > 1) and (cur_y < 6) \
                                      and ((board[cur_y+1][cur_x+1] in blue_nums and board[cur_y+2][cur_x+2] == 0) \
                                      or (board[cur_y+1][cur_x-1] in blue_nums and board[cur_y+2][cur_x-2] == 0) \
                                      or (board[cur_y-1][cur_x+1] in blue_nums and board[cur_y-2][cur_x+2] == 0) \
                                      or (board[cur_y-1][cur_x-1] in blue_nums and board[cur_y-2][cur_x-2] == 0)):

                                    jump_possible = True

                                    # promt user to move again
                                    print("You can jump again!")
                
                                    
                        second_click = False            

                        if jump_possible: # another jump can occur 
                            awaiting_red = True # red's turn will not end 
                            draw_board(board) # update the board with the first jump 
                            pygame.display.update()
                        elif bad_move: # move is not allowed and player needs to try again
                            awaiting_red = True
                        else:
                            awaiting_red = False
                        
                if not running:
                    pygame.quit()
                    
        # computer's turn
        elif game.turn == 'blue':
            move = game.get_move(board)

            # updating the board matrix 
            for i in range(8): # x position
                for j in range(8): # y position
                    new_space = move[0][j][i]
                    board[j][i] = new_space

        draw_board(board)
        pygame.display.update()

        if game.winner(game.turn, board) == 'red':
            print("Red wins!")
            running = False
        elif game.winner(game.turn, board) == 'blue':
            print("Blue wins!")
            running = False
            
        game.change_turn()
        
    pygame.quit()
    
def getPixels(x_pos, y_pos):
    """
    (int,int) -> (int,int)

    Takes an x and y position with respect to the board spaces - both values are between 0 and 7, with top left corner as (0,0) - 
    and returns the pixel position with respect to the screen size 
        
    """
    
    # dictionary with key as square on board and value as pixel position on screen (centre of the board square) 
    pos_to_pixel = {0:25, 1:75, 2:125, 3:175, 4:225, 5:275, 6:325, 7:375}  
    x_pixel = pos_to_pixel[x_pos]
    y_pixel = pos_to_pixel[y_pos]

    return (x_pixel, y_pixel)

def dist(x1, x2, y1, y2):
    """ Distance helper method """
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance
     
if __name__ == "__main__":
    main()
