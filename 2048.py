import random
import math
import numpy


class Board():
    UP, DOWN, LEFT, RIGHT = 1, 2, 3, 4

    def __init__(self, azmode=False):
        self.__won = False
        self.__azmode = False
        self.score = 0
        self.max = 2
        self.__nummoves = 0
        self.choices = [2, 2, 2, 2, 2, 2, 2, 2, 2, 4]
        self.empty = [(x, y) for x in range(4) for y in range(4)]
        self.cells = [[0]*4 for _ in range(4)]
        self.addTile()
        self.addTile()

    def __str__(self):
        """
        return a string representation of the current board.
        """
        rg = range(4)
        s = '\n'.join([' '.join([self.getCellStr(x, y) for x in rg]) for y in rg])
        return s + '\n'

    def numMoves(self):
        """return the number of moves made so far"""
        return self.__nummoves

    def won(self):
        """
        return True if the board contains at least one tile equal to 2048 or greater, False otherwise
        """
        return self.__won

    def canMove(self):
        """
        return True if there are any possible moves, or False otherwise
        """
        if not self.filled():
            return True

        for y in xrange(0, 4):
            for x in xrange(0, 4):
                c = self.getCell(x, y)
                if (x < 3 and c == self.getCell(x+1, y)) or (y < 3 and c == self.getCell(x, y+1)):
                    return True

        return False

    def filled(self):
        """
        return True if the board is filled
        """
        return len(self.getEmptyCells()) == 0

    def addTile(self):
        """
        add a random tile in an empty cell
          choices: a list of possible choices for the value of the tile.
                   default is [2, 2, 2, 2, 2, 2, 2, 2, 2, 4].
        """
        v = random.choice(self.choices)
        if self.empty:
            x, y = random.choice(self.empty)
            self.setCell(x, y, v)
            self.empty = self.getEmptyCells()

    def getCell(self, x, y):
        """return the cell value at x,y"""
        return self.cells[y][x]

    def getCellStr(self, x, y):
        """
        return a string representation of the cell located at x,y.
        """
        c = self.getCell(x, y)

        az = {}
        for i in range(1, int(math.log(2048, 2))):
            az[2**i] = chr(i+96)

        if c == 0 and self.__azmode:
            return '.'
        elif c == 0:
            return '  .'

        elif self.__azmode:
            if c not in az:
                return '?'
            s = az[c]
        elif c >= 1024:
            s = ' ' + str(int(2**(math.log(c, 2)-10))) + 'k'
        else:
            s = '%3d' % c

        return s

    def setCell(self, x, y, v):
        """set the cell value at x,y"""
        self.cells[y][x] = v

    def getLine(self, y):
        """return the y-th line, starting at 0"""
        return [self.getCell(i, y) for i in range(4)]

    def getCol(self, x):
        """return the x-th column, starting at 0"""
        return [self.getCell(x, i) for i in range(4)]

    def setLine(self, y, l):
        """set the y-th line, starting at 0"""
        for i in range(4):
            self.setCell(i, y, l[i])

    def setCol(self, x, l):
        """set the x-th column, starting at 0"""
        for i in range(4):
            self.setCell(x, i, l[i])

    def getEmptyCells(self):
        """return a (x, y) pair for each cell"""
        return [(x, y) for x in range(4) for y in range(4) if self.getCell(x, y) == 0]

    def __collapseLineOrCol(self, line, d):
        """
        Merge tiles in a line or column according to a direction and return a
        tuple with the new line and the score for the move on this line
        """
        if (d == Board.LEFT or d == Board.UP):
            inc = 1
            rg = xrange(0, 3, inc)
        else:
            inc = -1
            rg = xrange(3, 0, inc)

        pts = 0
        for i in rg:
            if line[i] == 0:
                continue
            if line[i] == line[i+inc]:
                v = line[i]*2
                if v == 2048:
                    self.__won = True

                line[i] = v
                line[i+inc] = 0
                pts += v

        return (line, pts)

    def __moveLineOrCol(self, line, d):
        """
        Move a line or column to a given direction (d)
        """
        nl = [c for c in line if c != 0]
        if d == Board.UP or d == Board.LEFT:
            return nl + [0] * (4 - len(nl))
        return [0] * (4 - len(nl)) + nl

    def move(self, d, add_tile=True):
        """
        move and return the move score
        """
        if d == Board.LEFT or d == Board.RIGHT:
            chg, get = self.setLine, self.getLine
        elif d == Board.UP or d == Board.DOWN:
            chg, get = self.setCol, self.getCol
        else:
            return 0

        moved = False
        tempscore = 0

        for i in range(4):
            origin = get(i)
            line = self.__moveLineOrCol(origin, d)
            collapsed, pts = self.__collapseLineOrCol(line, d)
            new = self.__moveLineOrCol(collapsed, d)
            chg(i, new)
            if origin != new:
                moved = True
            tempscore += pts

        self.empty = self.getEmptyCells()
        for i in range(4):
            for j in range(4):
                if self.cells[i][j] > self.max:
                    self.max == self.cells[i][j]

        if moved and add_tile:
            self.addTile()

        self.score += tempscore
        self.__nummoves += 1

        return moved


def possibleNewTiles(board):
    result = []
    for cell in board.empty:
        for v in [2,4]:
            newboard = Board()
            for x in range(4):
                for y in range(4):
                    newboard.cells[x][y] = board.cells[x][y]
            newboard.setCell(cell[0], cell[1], v)
            result.append(newboard)
    return result


def generateDepthOne(board):
    result = []
    for i in availableMoves(board):
        newboard = Board()
        for x in range(4):
            for y in range(4):
                newboard.cells[x][y] = board.cells[x][y]
        newboard.move(i, False)
        result.append(newboard)
    return result


def availableMoves(board):
    moves = []
    newboard = Board()
    for i in range(1, 5):
        for x in range(4):
            for y in range(4):
                newboard.cells[x][y] = board.cells[x][y]
        if newboard.move(i):
            moves.append(i)
    return moves


def smoothness(board, free=2, punishment=2):
    result = 0
    for i in range(4):
        result += math.fabs(board.cells[0][i] - board.cells[1][i])
        result += math.fabs(board.cells[1][i] - board.cells[2][i])
        result += math.fabs(board.cells[2][i] - board.cells[3][i])
        if board.cells[i][0] == board.cells[i][1]:
            result -= board.cells[i][0] * 2
        if board.cells[i][1] == board.cells[i][2]:
            result -= board.cells[i][1] * 2
        if board.cells[i][2] == board.cells[i][3]:
            result -= board.cells[i][2] * 2
        result += math.fabs(board.cells[i][0] - board.cells[i][1])
        result += math.fabs(board.cells[i][1] - board.cells[i][2])
        result += math.fabs(board.cells[i][2] - board.cells[i][3])
        if board.cells[0][i] == board.cells[1][i]:
            result -= board.cells[0][i] * 2
        if board.cells[1][i] == board.cells[2][i]:
            result -= board.cells[1][i] * 2
        if board.cells[2][i] == board.cells[3][i]:
            result -= board.cells[2][i] * 2
    if len(board.empty) < free:
        result = result * punishment
    result = result / board.max
    return result


def AIRandomAvailableMove(board, available, free):
    return random.choice(available)


def AIPreferenceMove(board, available, free):
    if 4 in available:
        return 4
    if 1 in available:
        return 1
    if 3 in available:
        return 3
    if 2 in available:
        return 2


def AIHighScoreMove(board, available, free):
    move = 0
    best = -1
    newboard = Board()
    newboard.score = board.score
    for i in available:
        for x in range(4):
            for y in range(4):
                newboard.cells[x][y] = board.cells[x][y]
        newboard.move(i)
        if newboard.score > best:
            best = newboard.score
            move = i
    return move


def AIFreeSpaceMove(board, available, free):
    move = 0
    best = -1
    newboard = Board()
    newboard.empty = board.empty
    for i in available:
        for x in range(4):
            for y in range(4):
                newboard.cells[x][y] = board.cells[x][y]
        newboard.move(i)
        if len(newboard.empty) > best:
            best = len(newboard.empty)
            move = i
    return move


def AISmoothBoard(board, available, free=2, punishment=2):
    move = 0
    best = 999999
    newboard = Board()
    for i in available:
        for x in range(4):
            for y in range(4):
                newboard.cells[x][y] = board.cells[x][y]
        newboard.move(i, False)
        # boards = generateDepthOne(newboard)
        # boards = possibleNewTiles(newboard)
        # smooth = []
        # for b in boards:
            # smooth = smoothness(b, free, punishment)
        # smooth = sum(smooth) / len(smooth)
        smooth = smoothness(newboard, free, punishment)
        if smooth < best:
            best = smooth
            move = i
    return move


def AITest(repeats=10, rounds=1000):
    scores = []
    moves = []
    best = 0
    worst = 99999
    bestboard = []
    worstboard = []
    wins = 0
    for _ in range(repeats):
        for _ in range(rounds):
            a = Board()
            available = availableMoves(a)
            while available:
                movetomake = AISmoothBoard(a, available)
                a.move(movetomake)
                available = availableMoves(a)
            if a.won():
                wins += 1
            if a.score > best:
                best = a.score
                bestboard = a
            if a.score < worst:
                worst = a.score
                worstboard = a
            scores.append(a.score)
            moves.append(a.numMoves())

        print 'average score: ' + str(sum(scores)/float(len(scores)))
        print 'score stdev: ' + str(numpy.std(scores))
        print 'average moves: ' + str(sum(moves)/float(len(moves)))
        print 'wins: ' + str(wins)
        print 'win percentage: ' + str(float(wins)/float(rounds)*100) + '%'
        print 'best score: ' + str(best)
        print bestboard
        print 'worst score: ' + str(worst)
        print worstboard
        print '\n'
        scores = []
        moves = []
        wins = 0
        best = 0
        worst = 99999

AITest(1, 1000)