import tkinter as tk
from tkinter import messagebox
import random

class MinesweeperCell(tk.Label):
    def __init__(self, master, coord):
        '''MinesweeperCell(master,coord) -> MinesweeperCell
        creates a new blank MinesweeperCell with (row,column) coord'''
        tk.Label.__init__(self, master, height=1, width=2, text='', \
                       bg='white', font=('Arial', 24), relief='raised')
        self.coord = coord  # (row,column) coordinate tuple
        self.number = 0  # 0 represents an empty cell
        self.readOnly = False  # starts as changeable
        self.exposed = False  # starts unexposed
        self.hasBomb = False
        self.hasFlag = False
        self.adjBombs = 0
        # set up listeners
        self.bind('<Button-1>', self.expose)
        self.bind('<Button-3>', self.flag)

    def __str__(self):
        '''String representation of a minesweeper cell'''
        output = str(self.coord)
        if (self.hasBomb):
            output += ", hasBomb"
        return output

    def expose (self, event):
        '''MinesweeperCell.expose(event) 
        exposes the minesweeper cell, updates it, and calls auto_expose'''
        colormap = ['', 'blue', 'darkgreen', 'red', 'purple', 'maroon', 'cyan', 'black', 'dim gray']
        self.exposed = True
        self.unbind('<Button-1>')
        self.unbind('<Button-3>')
        if self.hasBomb:
            self.master.lose_game()
        else:
            self.update()
            if self.adjBombs == 0:
                self.master.auto_expose(self)
        self.master.check_win()

    def flag (self, event):
        '''MinesweeperCell.flag(event) 
        flags the minesweeper cell and updates the flag counter'''
        if self.master.get_flagsLeft()>0 and not self.hasFlag:
            self['text'] = '*'
            self.hasFlag = True
            self.master.update_counter(-1)
            self.unbind('<Button-1>')
        elif self.hasFlag:
            self['text'] = ''
            self.hasFlag = False
            self.master.update_counter(1)
            self.bind('<Button-1>', self.expose)

    def add_bomb (self):
        '''MinesweeperCell.add_bomb() 
        sets hasBomb to True'''
        self.hasBomb = True

    def set_adjBombs(self,i):
        '''MinesweeperCell.set_adjBombs(event)
        sets the number of adjacent cells with bombs'''
        self.adjBombs = i

    def update(self):
        '''MinesweeperCell.update()
        updates the cell based on the bumber of adjacent bombs'''
        colormap = ['', 'blue', 'darkgreen', 'red', 'purple', 'maroon', 'cyan', 'black', 'dim gray']
        self.exposed = True
        self.unbind('<Button-1>')
        self.unbind('<Button-3>')

        if self.adjBombs == 0:
            self['text'] = ''
            self['bg'] = 'grey75'
            self['relief'] = 'sunken'
        else:
            self['bg'] = 'grey75'
            self['text'] = self.adjBombs
            if self.adjBombs != 0:
                self['fg'] = colormap[self.adjBombs]
            self['relief'] = 'sunken'

    def show_bomb(self):
        '''MinesweeperCell.show_bomb()
        adds an asterisk and makes cell red to show a bomb'''
        self['text'] = '*'
        self['bg'] = 'red'

    def get_coord(self):
        '''MinesweeperCell.get_coord() -> tuple
        returns coordinate tuple of the cell'''
        return self.coord

    def get_exposed(self):
        '''MinesweeperCell.get_exposed() -> boolean
        returns True if the cell is exposed, False if not'''
        return self.exposed

    def get_hasBomb(self):
        '''MinesweeperCell.get_hasBomb() -> boolean
        returns True if the cell has a bomb, False if not'''
        return self.hasBomb

    def get_adjBombs(self):
        '''MinesweeperCell.get_adjBombs() -> int
        returns number of bombs adjacent to the cell'''
        return self.adjBombs






class MinesweeperGrid(tk.Frame):
    '''object for a Minesweeper grid'''
    def __init__(self,master,width,height,numBombs):
        '''MinesweeperGrid(master)
        creates a new blank Minesweeper grid'''
        # initialize a new Frame
        tk.Frame.__init__(self,master)
        self.grid()
        self.width = width
        self.height = height
        self.numBombs = numBombs
        self.flagsLeft = numBombs
        self['bg'] = 'white smoke'
        # (odd numbered rows and columns in the grid)
        for n in range(1,self.height*2,2):
            self.rowconfigure(n,minsize=2)
        for n in range(1, self.width*2, 2):
            self.columnconfigure(n,minsize=2)

        # create the cells
        self.cells = {} # set up dictionary for cells
        for row in range(self.height):
            for column in range(self.width):
                coord = (row,column)
                self.cells[coord] = MinesweeperCell(self,coord)
                # cells go in even-numbered rows/columns of the grid
                self.cells[coord].grid(row=row*2,column=column*2)

        self.flagCounter = tk.Label(master, text = self.flagsLeft)
        self.flagCounter.config(font = ("Arial", 30))
        self.flagCounter.grid(row=self.height*2, column=0)
        # randomly place the bombs
        bombsPlaced = 0
        while bombsPlaced < self.numBombs:
            bombRow = random.randint(0,self.height-1)
            bombWidth = random.randint(0,self.width-1)
            bombCoord = (bombRow, bombWidth)
            if not self.cells[bombCoord].get_hasBomb():
                self.cells[bombCoord].add_bomb()
                #self.cells[bombCoord].show_bomb()
                bombsPlaced += 1
        for cell in self.cells.values():
            cell.set_adjBombs(self.num_adjBombs(cell))

    def lose_game(self):
        '''MinesweeperGrid.lose_game()
        ends the game and reveals all the bombs'''
        for cell in self.cells.values():
            cell.unbind('<Button-1>')
            cell.unbind('<Button-3>')
            if cell.get_hasBomb():
                cell.show_bomb()
        messagebox.showerror('Minesweeper', 'KABOOM! You lose.', parent=self)

    def check_win(self):
        '''MinesweeperGrid.check_win()
        if the game has been won, end the game'''
        numExposed = 0
        for row in range(self.height):
            for column in range(self.width):
                coord = (row,column)
                if not self.cells[coord].get_hasBomb() and self.cells[coord].get_exposed():
                    numExposed += 1
        if numExposed == self.height*self.width-self.numBombs:
            messagebox.showinfo('Minesweeper', 'Congratulations -- you won!', parent=self)

    def num_adjBombs(self, cell):
        '''MinesweeperGrid.num_adjBombs(cell) --> int
        returns number of bombs adjacent to cell'''
        bombCounter = 0
        adjCells = self.get_adjacent(cell)
        for x in adjCells:
            if x.get_hasBomb():
                bombCounter += 1
        return bombCounter

    def auto_expose(self, cell):
        '''MinesweeperGrid.auto_expose()
        reveals a 3x3 area and calls expose_rest'''
        adjCells = self.get_adjacent(cell)
        for x in adjCells:
            x.update()
        self.expose_rest()

    def expose_rest(self):
        '''MinesweeperGrid.expose_rest()
        exposes a 3x3 area around all cells that are blank and adjacent to an unexposed cell'''
        for cell in self.cells.values():
            if cell.get_exposed() and cell.get_adjBombs() ==0 and self.is_edge(cell):
                cell.expose('')

    def is_adjacent (self,cell1,cell2):
        '''MinesweeperGrid.is_adjacent() --> boolean
        returns True if cell1 is adjacent to cell2, if not returns False'''
        coord1 = cell1.get_coord()
        coord2 = cell2.get_coord()
        if (coord1[0] - 1 == coord2[0]) or (coord1[0] + 1 == coord2[0]) or coord1[0] == coord2[0]:
            if (coord1[1] - 1 == coord2[1]) or (coord1[1] + 1 == coord2[1]) or coord1[1] == coord2[1]:
                return True
        return False

    def get_adjacent (self,cell):
        '''MinesweeperGrid.is_adjacent(cell) --> MinesweeperCell[]
        returns array of adjacent cells to cell'''
        adjacentCells = []
        cellList = self.cells.values()
        for x in cellList:
            if self.is_adjacent(cell, x):
                adjacentCells.append(x)
        return adjacentCells

    def update_counter(self, i):
        '''MinesweeperGrid.update_counter(i)
        adds i flags to flagsLeft and updates text in the flag counter label'''
        self.flagsLeft += i
        self.flagCounter['text'] = self.flagsLeft

    def get_flagsLeft(self):
        '''MinesweeperGrid.get_flagsLeft() --> int
        returns the number of flags that are left'''
        return self.flagsLeft

    def is_edge(self, cell):
        '''MinesweeperGrid.is_edge(cell) --> boolean
        returns True if cell is adjacent to an unexposed cell, if not returns False'''
        adjCells = self.get_adjacent(cell)
        for x in adjCells:
            if not x.get_exposed():
                return True
                break
        return False


def play_minesweeper(width,height,numBombs):
    root = tk.Tk()

    grid = MinesweeperGrid(root,width,height,numBombs)
    root.title('Minesweeper')
    root.mainloop()

play_minesweeper(20, 20, 70)
