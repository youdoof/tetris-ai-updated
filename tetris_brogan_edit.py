# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

################################################################################
# Tetris AI
# The original tetris game with an added AI player
# Editted by: William Johnson, Brandon Merkel, Andrew Brogan, and Jordan Duncan
# Each section that was editted or added by us is marked with 3 pound symbols,
# which looks like: ###
# Date: 1 December 2016
# Class: CS 480 Artificial Intelligence
################################################################################

################################################################################
# Edited by Andrew Brogan on 7/3/2018
#
# Major Changes:
# - heuristic for calculating the height penalty (calcRealHeightPenalty)
# - how the next pieces are generated (bagGenerator)
#
# Minor Changes:
# - removed need for music to play the game (midi files)
# - changed FPS to 60, makes game run quicker
# - changed fall frequency to be fixed rate
################################################################################

import random, time, pygame, sys, copy
from pygame.locals import *

FPS = 60
# The width and height were changed to allow for a bigger game and to allow
# for showing more pieces
WINDOWWIDTH = 1024 ###
WINDOWHEIGHT = 640 ###
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)
# These colors were added by our group to standardize block color
ORANGE      = (255, 128,   0) ###
LIGHTORANGE = (255, 178, 102) ###
PURPLE      = (128,   0, 128) ###
LIGHTPURPLE = (186,  85, 211) ###
GRAY        = (128, 128, 128) ###
LIGHTGRAY   = (211, 211, 211) ###

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
# The color dictionaries were editted to include the new colors above
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW,      ORANGE,      PURPLE,      GRAY) ###
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW, LIGHTORANGE, LIGHTPURPLE, LIGHTGRAY) ###
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

PIECESLIST = list(PIECES.keys())
RUNNINGLIST = PIECESLIST[:]
random.shuffle(RUNNINGLIST)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    showTextScreen('Tetromino')
    while True: # game loop
        runGame()
        showTextScreen('Game Over')

'''
ORIGINAL
Runs the game
return: when game over
'''
def runGame():
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    # Initialize pieces.
    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()
    nextPiece2 = getNewPiece()
    nextPiece3 = getNewPiece()

    # Sets heldPiece and tempPiece to False, used in holding a piece.
    heldPiece = False ###
    tempPiece = False ###
    aiBoolean = False ###

    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            # When a piece is placed, it sets the fallingPiece equal to the
            # nextPiece and nextPiece equal to the piece after until it reaches
            # the 3rd piece after the fallingPiece, which it creates a new piece,
            # this allows for the current piece and next three pieces to be known
            # to the program and user.
            fallingPiece = nextPiece  ###
            nextPiece = nextPiece2 ###
            nextPiece2 = nextPiece3 ###
            # BROGAN EDIT 
            nextPiece3 = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime

            if aiBoolean == True:
                bestMove = findBestMove(board, fallingPiece)
                findNewLocationForPiece(bestMove[0], fallingPiece, bestMove[1], board)

            if not isValidPosition(board, fallingPiece):
                return # can't fit a new piece on the board, so game over

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == KEYUP:
                if (event.key == K_p):
                    # Pausing the game
                    #DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    showTextScreen('Paused') # pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_LEFT or event.key == K_a):
                    movingLeft = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    movingRight = False
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = False
                # This allows for a block to be held if c or h is pressed
                # it will store the held piece in the heldPiece variable and
                # make the fallingPiece the nextPiece and so on if there is no
                # current heldPiece. If there is a piece in heldPiece it will
                # swap it with the fallingPiece.
                elif (event.key == K_c or event.key == K_h): ###
                    if (heldPiece == False): ###
                        heldPiece = fallingPiece ###
                        fallingPiece = nextPiece  ###
                        nextPiece = nextPiece2 ###
                        nextPiece2 = nextPiece3 ###
                        # BROGAN EDIT
                        nextPiece3 = getNewPiece() ###
                        fallingPiece['y'] = -2 ###
                    else:
                        tempPiece = heldPiece ###
                        heldPiece = fallingPiece ###
                        fallingPiece = tempPiece ###
                        fallingPiece['y'] = -2 ###

            elif event.type == KEYDOWN:
                # moving the piece sideways
                if (event.key == K_LEFT or event.key == K_a) and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSidewaysTime = time.time()

                elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSidewaysTime = time.time()

                # rotating the piece (if there is room to rotate)
                elif (event.key == K_UP or event.key == K_w):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                elif (event.key == K_q): # rotate the other direction
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])

                # making the piece fall faster with the down key
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = True
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()

                # Runs the AI code, can be toggled on and off
                elif event.key == K_i: ###
                    aiBoolean = not(aiBoolean) ###
                    bestMove = findBestMove(board, fallingPiece) ###
                    findNewLocationForPiece(bestMove[0], fallingPiece, bestMove[1], board) ###

                # move the current piece all the way down
                elif event.key == K_SPACE:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    fallingPiece['y'] += i - 1

        # handle moving the piece because of user input
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
            lastMoveSidewaysTime = time.time()

        if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1
            lastMoveDownTime = time.time()

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            # see if the piece has landed
            if not isValidPosition(board, fallingPiece, adjY=1):
                # falling piece has landed, set it on the board
                addToBoard(board, fallingPiece)
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None
            else:
                # piece did not land, just move the piece down
                fallingPiece['y'] += 1
                lastFallTime = time.time()

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        # The draw nextPiece1-3 draw the next three piece to the board so the
        # user can see them
        drawNextPiece(nextPiece) ###
        drawNextPiece2(nextPiece2) ###
        drawNextPiece3(nextPiece3) ###
        # The drawHeight, drawHole, and drawPenalty draw the number associated with
        # the current height, hole, and total penalty to the board for the user
        # to see
        drawHeight(board) ###
        drawHole(board) ###
        drawPenalty(board) ###
        drawArtificialIntelligenceInstruct(board) ###
        # If there is a piece held, then it draws it to the board
        if heldPiece != False: ###
            drawHeldPiece(heldPiece) ###
        # If there is a fallingPiece, then it draws it to the board
        if fallingPiece != None: ###
            drawPiece(fallingPiece) ###

        pygame.display.update()
        FPSCLOCK.tick(FPS)

'''
ORIGINAL
Makes text that can be placed over game
text: text to display
font: font the text will be displayed in
color: color of text
return: text object
'''
def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

'''
ORIGINAL
Ends game
'''
def terminate():
    pygame.quit()
    sys.exit()

'''
ORIGINAL
Go through event queue looking for a KEYUP event.
Grab KEYDOWN events to remove them from the event queue.
'''
def checkForKeyPress():
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

'''
ORIGINAL
Displays large text in the center of the screen until a key is pressed.
text: text to display
'''
def showTextScreen(text):
    
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()

'''
ORIGINAL
Ends game if a quit event is found
'''
def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back

'''
ORIGINAL
Based on the score, return the level the player is on and how many seconds 
pass until a falling piece falls one space.
score: current score
return: the current level and fall frequency
'''
def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.005 # ORIGINAL = 0.25 - (LEVEL * 0.02) ### BROGAN EDIT
    return level, fallFreq
'''
ADDED BROGAN EDIT
Checks if the current running list has less than 3 pieces in it, if so
calls bagGenerator to add more pieces to the running list.
Pops the next shape from the running list and returns it as the next
piece.
return: new piece object
'''
def getNewPiece():

    if (len(RUNNINGLIST) < 3):
        bagGenerator(RUNNINGLIST)
    shape = RUNNINGLIST.pop(0)

    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) -1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2,
                'color': getPieceColor(shape)}
    return newPiece
'''
ADDED BROGAN EDIT
Creates a "bag" of the 7 tetrominoes as defined here:
http://tetris.wikia.com/wiki/Random_Generator
lis: RUNNINGLIST passed
'''
def bagGenerator(lis):
    temp = PIECESLIST[:]
    random.shuffle(temp)
    for index in temp:
        lis.append(index)
    return
'''
### This entire function was added 
Added this function to make sure that different shaped pieces don't generate 
with the same color.
shape: the shape
return: the corresponding color value
'''
def getPieceColor(shape):
    # The integer values 0..6 represent the position of each color in the COLOR list.
    if shape == 'S':
        # Red
        return 2
    elif shape == 'Z':
        # Green
        return 1
    elif shape == 'L':
        # Blue
        return 0
    elif shape == 'J':
        # Yellow
        return 3
    elif shape == 'I':
        # Purple
        return 5
    elif shape == 'O':
        # Orange
        return 4
    elif shape == 'T':
        # Gray
        return 6
'''
ORIGINAL
fill in the board based on piece's location, shape, and rotation
board: the board
piece: the piece to be added
'''
def addToBoard(board, piece):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if y + piece['y'] >= 0:
                if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                    board[x + piece['x']][y + piece['y']] = piece['color']

'''
ORIGINAL
create and return a new blank board data structure
return: a blank board
'''
def getBlankBoard():
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board
'''
### This entire function was added
This function calculates the height penalty. The height penalty is a number
that is given for how high the blocks are on the board and for each space up
to that given height.
board: the current board
return: the height penalty
'''
def calcHeightPenalty(board):
    # Declare variables and set equal to 0
    blockCount = 0
    block = 0
    periodCount = 0
    height = 0
    heightCount = []
    newPeriodCount = 0
    penalty = 0
    curPenalty = 0
    tempPenalty = 0
    # Runs through the board and counts the number of blank spaces
    for x in range (0,20):
        for y in range (0,10):
            if board[y][x] == '.':
                periodCount = periodCount + 1
            blockCount = 200 - periodCount
        if blockCount != 0:
            heightCount.insert(0,x)
    # If the board is not blank then it runs through the board to find a block,
    # if a block is found then it adds the height of that block to a list.
    if periodCount != 200:
        for x in range (0,20):
            for y in range (0,10):
                if board[y][x] != '.':
                    block = block + 1
            if block != 0:
                heightCount.insert(0,x)
                block = 0

    # Removes the height input when the board is blank or has a height less than
    # the two bottom rows, this allows for a basic height penalty to be established
    # with the lowest height being the second row from the bottom.
    for z in range (0,18):
        heightCount.remove(z)

    # The height is determined by the lowest number in the list because the highest,
    # value is the bottom of the board. This occurs because the board is generated
    # top down.
    height = min(heightCount)
    # Runs through the board starting at the heighest point from the bottom of the
    # board and counts the number of blank spots in a row
    for a in range(height,20):
        for b in range (0,10):
            if board[b][a] == '.':
                newPeriodCount = newPeriodCount + 1
        # The penalty is the number of blank spots in that row multiplied by
        # the column value. This allows for the blanks spots at the bottom of
        # to have the highest value (19) and a blank spot on the second from bottom
        # ro to have 18 and so on up the board. This will allow for the search
        # function to find the best place to place a block by selecting the
        # placement that reduces the penalty the most (The spot lowest on the board).
        penalty = newPeriodCount * a
        # Each row penalty is added together to find the total height penalty.
        curPenalty = curPenalty + penalty
        newPeriodCount = 0
        tempPenalty = curPenalty

    # Returns the total height penalty
    return tempPenalty
'''
### 
BROGAN EDIT 7/3/2018
Replaced calcHeightPenalty.
The higher the block, the worse of a # should be returned.

board: the current board
return: the height penalty
'''
def calcRealHeightPenalty(board):
    heightMultipliers = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 0]
    hPenalty = 0
    for y in range (0,20):
        for x in range (0,10):
            if board[x][y] != ".":
                hPenalty += (20 - y) * heightMultipliers[y]
    return hPenalty
'''
### This entire function was added
This function calculates the hole penalty. The hole penalty is a value that
is associated with each hole in the board. A hole is a empty space that has
a block somewhere in the column above it.
board: the current board
return: the hole penalty
'''
def calcHolePenalty(board):
    # Declare variables
    holeCount = 0
    holePenalty = 0
    tempY = 0
    # Runs through the board to find blank spaces
    for y in range (0,20):
        for x in range (0,10):
            # If the space is blank it runs through a while loop checking to
            # see if there is block somewhere in the current column above the
            # blank space.
            if board[x][y] == '.':
                tempY = y
                while (tempY != 0):
                    tempY = tempY - 1
                    # If there is a block in the column above the blank space,
                    # then it adds 1 to the hole counter.
                    if board[x][tempY] != '.':
                        holeCount = holeCount + 1
                        tempY = 0

    # The total hole penalty is the number of holes multiplied by 150, this gives
    # each hole a penalty value of 150.
    holePenalty = holeCount * 350

    # Returns the total hole penalty
    return holePenalty
    
'''
### This entire function was added
This function takes in the board and calculates the total penalty for the board
board: the current board
return: the total penalty
'''
def calcPenalty(board):
    # Sets height and hole equal to their respective penalties
    height = calcRealHeightPenalty(board)
    hole = calcHolePenalty(board)

    # The total penalty is the height penalty plus the hole penalty
    penalty = height + hole 

    return penalty

'''
ORIGINAL
is coordinate on the board
x: x coordinate
y: y coordinate
return: status
'''
def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT

'''
ORIGINAL
Return True if the piece is within the board and not colliding
board: current board
piece: the piece to be tested
adjX: x offset
adjY: y offset
return: status of piece on board
'''
def isValidPosition(board, piece, adjX=0, adjY=0):
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

'''
ORIGINAL
Return True if the line filled with boxes with no gaps.
board: current board
y: the line in question
return: status
'''
def isCompleteLine(board, y):
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True

'''
ORIGINAL
Remove any completed lines on the board, move everything above them down, 
and return the number of complete lines.
board: the current board
return: the number of lines removed
'''
def removeCompleteLines(board):
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved

'''
ORIGINAL
Convert the given xy coordinates of the board to xy coordinates 
of the location on the screen.
boxx: x coordinate on board
boxy: y coordinate on board
return: x coordinate on screen, y coordinate on screen
'''
def convertToPixelCoords(boxx, boxy):
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))

'''
ORIGINAL
draw a single box (each tetromino piece has four boxes)
at xy coordinates on the board. Or, if pixelx & pixely
are specified, draw to the pixel coordinates stored in
pixelx & pixely (this is used for the "Next" piece).
'''
def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))

'''
ORIGINAL
draw the border around the board
board: the board
'''
def drawBoard(board):
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])

'''
ORIGINAL
draw the current score and level
score: current score
level: current level
'''
def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)

'''
ORIGINAL
Draws a piece on the board
piece: the piece to be drawn
pixelx: x location on the screen
pixely: y location on the screen 
'''
def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))
'''
### This entire function was added
This draws the next piece onto the screen, to the right of the board
piece: piece to draw
'''
def drawNextPiece(piece): 
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)
'''
### This entire function was added
This draws the next piece number 2 onto the screen, to the right of the board
and under the next piece
piece: piece to draw
'''
def drawNextPiece2(piece): 
    nextSurf = BASICFONT.render('Next 2:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 230)
    DISPLAYSURF.blit(nextSurf, nextRect)
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=250)
'''
### This entire function was added
This draws the next piece number 3 onto the screen, to the right of the board
and under the next piece number 2
piece: piece to draw
'''
def drawNextPiece3(piece):
    nextSurf = BASICFONT.render('Next 3:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 380)
    DISPLAYSURF.blit(nextSurf, nextRect)
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=400)
'''
### This entire function was added
This draws the held piece onto the screen, to the left of the board
piece: piece to draw
'''
def drawHeldPiece(piece):
    nextSurf = BASICFONT.render('Held:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 1000, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    drawPiece(piece, pixelx=WINDOWWIDTH-1000, pixely=100)
'''
### This entire function was added
This prints the height penalty to the left of the board, under the held piece
board: the current board
'''
def drawHeight(board): 
    height = calcRealHeightPenalty(board)
    nextSurf = BASICFONT.render("Height Penalty: " + str(height), True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 1000, 250)
    DISPLAYSURF.blit(nextSurf, nextRect)

'''
### This entire function was added
This prints the hole penalty to the left of the board, under the height penalty
board: the current board
'''
def drawHole(board): 
    hole = calcHolePenalty(board)
    nextSurf = BASICFONT.render("Hole Penalty: " + str(hole), True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 1000, 350)
    DISPLAYSURF.blit(nextSurf, nextRect)

'''
### This entire function was added
This prints the total penalty to the left of the board, under the hole penalty
board: the current board
'''
def drawPenalty(board): 
    penalty = calcPenalty(board)
    nextSurf = BASICFONT.render("Total Penalty: " + str(penalty), True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 1000, 450)
    DISPLAYSURF.blit(nextSurf, nextRect)

'''
### This entire function was added
This prints the total penalty to the left of the board, under the hole penalty
board: the current board
'''
def drawArtificialIntelligenceInstruct(board): 
    nextSurf = BASICFONT.render("Press i to toggle AI function. ", True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 600, 50)
    DISPLAYSURF.blit(nextSurf, nextRect)

"""
### This entire function was added
Finds the lowest location on the board a piece can be placed in a given column
and rotation
column: a number from 0 to 7, as if you were placing from the left of the board
piece: pass in "fallingPiece" -- it figures out what shape is given and reacts accordingly
rotation: a number from 0 to 3, representing rotations of the shape templates
board: pass in "board"

Example: findNewLocationForPiece(4, fallingPiece, 1, board)
^^ places the leftmost part of the shape in the 5th column
   of the board, in the 2nd rotation permutation.

    XXXX
0123456789
    ^
"""
def findNewLocationForPiece(column, piece, rotation, board):
    tempr = piece['rotation']
    tempx = piece['x']
    
    # Rotate the piece to given input rotation
    piece['rotation'] = rotation

    # if/elif statements to displace the given column so the pieces
    # fall to the correct column, based off the furthest left block
    # of the shape. This is done because the shape templates have
    # different amounts of space for each rotation and shape.
    if piece['shape'] == 'S':
        if piece['rotation'] == 0:
            piece['x'] = column - 1
        elif piece['rotation'] == 1:
            piece['x'] = column - 2

    elif piece['shape'] == 'Z':
        piece['x'] = column - 1

    elif piece['shape'] == 'I':
        if piece['rotation'] == 0:
            piece['x'] = column - 2
        elif piece['rotation'] == 1:
            piece['x'] = column

    elif piece['shape'] == 'O':
        piece['x'] = column - 1

    # Shapes J, L, and T behave the same way,
    # so they are contained in the same elif
    elif piece['shape'] == 'J' or piece['shape'] == 'L' or piece['shape'] == 'T':
        if piece['rotation'] == 0 or piece['rotation'] == 2 or piece['rotation'] == 3:
            piece['x'] = column - 1
        elif piece['rotation'] == 1:
            piece['x'] = column - 2

    # Checks if it is a valid placement, repairs changes
    # if it is invalid. Action is unresponsive if invalid
    if isValidPosition(board, piece, adjY=0, adjX=0):
        for i in range(1, BOARDHEIGHT):
            if not isValidPosition(board, piece, adjY=i):
                break
        piece['y'] += i - 1
    else:
        piece['rotation'] = tempr
        piece['x'] = tempx
        for i in range(1, BOARDHEIGHT):
            if not isValidPosition(board, piece, adjY=i):
                break
        piece['y'] += i - 1
'''
### This entire function was added
Evalutes every possible location a piece could be placed on the board and chooses
the best move
board: the current board
piece: the piece to be placed
return: the column and rotation that piece should be in to make the best move.
'''
def findBestMove(board, piece):
    minRotation = None
    minColumn = None
    minPenalty = sys.maxint

    for cRot in range(0, len(PIECES[piece['shape']])):
        for cCol in range(0, BOARDWIDTH):
            copyBoard = copy.deepcopy(board)
            findNewLocationForPiece(cCol, piece, cRot, copyBoard)
            addToBoard(copyBoard, piece)
            currentPenalty = calcPenalty(copyBoard)
            if currentPenalty < minPenalty:
                minPenalty = currentPenalty
                minColumn = cCol
                minRotation = cRot
    return [minColumn, minRotation]

if __name__ == '__main__':
    main()
