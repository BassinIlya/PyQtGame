import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame
from PyQt5 import QtGui, QtCore
from snakeUI import Ui_MainWindow
from enum import Enum
from random import randrange
from tkinter import *

top = []
CELL_SIZE = 16
BOARD_SIZE = 640


class Direction(Enum):
    RIGHT = 0,
    LEFT = 1,
    UP = 2,
    DOWN = 3


class Food:
    def __init__(self, cell):
        self.cell = cell


class Cell:
    def __init__(self, x, y):
        self.x = x % BOARD_SIZE
        self.y = y % BOARD_SIZE


class Snake:
    def __init__(self):
        self.length = 3
        self.isDead = False
        self.cellArray = []
        self.lastCell = 0
        self.x = self.length * CELL_SIZE
        self.y = 0
        for i in range(self.length):
            self.add_cell(self.x - i * CELL_SIZE, self.y)

    def add_cell(self, x, y):
        new_cell = Cell(x, y)
        self.lastCell = new_cell
        self.cellArray.append(new_cell)

    def moveRight(self):
        self.x += CELL_SIZE
        self.x %= BOARD_SIZE
        self.lastCell = self.cellArray[len(self.cellArray) - 1]
        new_cell = Cell(self.x, self.y)
        self.cellArray.remove(self.lastCell)
        self.cellArray.insert(0, new_cell)

    def moveLeft(self):
        self.x -= CELL_SIZE
        self.x %= BOARD_SIZE
        self.lastCell = self.cellArray[len(self.cellArray) - 1]
        new_cell = Cell(self.x, self.y)
        self.cellArray.remove(self.lastCell)
        self.cellArray.insert(0, new_cell)

    def moveUp(self):
        self.y -= CELL_SIZE
        self.y %= BOARD_SIZE
        self.lastCell = self.cellArray[len(self.cellArray) - 1]
        new_cell = Cell(self.x, self.y)
        self.cellArray.remove(self.lastCell)
        self.cellArray.insert(0, new_cell)

    def moveDown(self):
        self.y += CELL_SIZE
        self.y %= BOARD_SIZE
        self.lastCell = self.cellArray[len(self.cellArray) - 1]
        new_cell = Cell(self.x, self.y)
        self.cellArray.remove(self.lastCell)
        self.cellArray.insert(0, new_cell)

    def growSnake(self):
        self.length += 1
        self.cellArray.append(self.lastCell)


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.timer = QtCore.QBasicTimer()
        self.snake = Snake()
        self.direction = Direction.RIGHT
        self.resetButton.clicked.connect(self.resetClicked)
        self.startButton.clicked.connect(self.start)
        self.exitButton.clicked.connect(self.exit)
        self.food = 0
        self.speed = 100

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.moveSnake(self.direction)
            self.repaint()
            if not self.food:
                self.createFood()
        else:
            QFrame.timerEvent(event)

    def createFood(self):
        board_size = BOARD_SIZE / CELL_SIZE
        x = randrange(board_size) * CELL_SIZE
        y = randrange(board_size) * CELL_SIZE
        for snakeCell in self.snake.cellArray:
            if x == snakeCell.x and y == snakeCell.y:
                return
        cell_food = Cell(x, y)
        self.food = Food(cell_food)

    def moveSnake(self, direction):
        if direction == Direction.RIGHT:
            self.snake.moveRight()
        if direction == Direction.LEFT:
            self.snake.moveLeft()
        if direction == Direction.UP:
            self.snake.moveUp()
        if direction == Direction.DOWN:
            self.snake.moveDown()
        if self.food and self.snake.x == self.food.cell.x and self.snake.y == self.food.cell.y:
            self.snake.growSnake()
            self.food = 0
            self.increaseCount()
        for i in range(1, len(self.snake.cellArray) - 1):
            cell_snake = self.snake.cellArray[i]
            if self.snake.x == cell_snake.x and self.snake.y == cell_snake.y:
                self.timer.stop()
                self.snake.isDead = True
                top.append(self.scoreLcd.value())
                top.sort(reverse=True)
                try:
                    self.firstPlayer.setText(str(top[0]) or '')
                    self.secondPlayer.setText(str(top[1]) or '')
                    self.thirdPlayer.setText(str(top[2]) or '')
                    self.fourLabel.setText(str(top[3]) or '')
                    self.fifthPlayer.setText(str(top[4]) or '')
                except IndexError:
                    return

    def increaseCount(self):
        self.scoreLcd.display(self.scoreLcd.value() + 20)
        if self.speed > 30:
            self.speed -= 10
            self.timer.stop()
            self.timer.start(self.speed, self)

    def keyPressEvent(self, e):
        if not self.isPaused:
            if e.key() == QtCore.Qt.Key_W and self.direction != Direction.UP and self.direction != Direction.DOWN:
                self.direction = Direction.UP
            elif e.key() == QtCore.Qt.Key_S and self.direction != Direction.DOWN and self.direction != Direction.UP:
                self.direction = Direction.DOWN
            elif e.key() == QtCore.Qt.Key_A and self.direction != Direction.LEFT and self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            elif e.key() == QtCore.Qt.Key_D and self.direction != Direction.RIGHT and self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT
            elif e.key() == QtCore.Qt.Key_P:
                self.pause()
        elif e.key() == QtCore.Qt.Key_P:
            self.start()
        elif e.key() == QtCore.Qt.Key_Escape:
            self.exit()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if not self.snake.isDead:
            self.drawBoard(qp)
            self.drawSnake(qp)
            if self.food:
                self.drawFood(qp)
        else:
            qp.setBrush(QtGui.QColor(255, 0, 0))
            qp.drawRect(0, 0, self.painterWidget.width(), self.painterWidget.height())
            font = qp.font()
            font.setPointSize(36)
            qp.setFont(font)
            qp.drawText(200, 280, 'Game over')
        qp.end()

    def drawBoard(self, qp):
        qp.setBrush(QtGui.QColor(25, 80, 0, 160))
        qp.drawRect(0, 0, self.painterWidget.width(), self.painterWidget.height())

    def drawFood(self, qp):
        qp.setBrush(QtGui.QColor(255, 60, 0, 160))
        qp.drawRect(self.food.cell.x, self.food.cell.y, CELL_SIZE, CELL_SIZE)

    def drawSnake(self, qp):
        qp.setBrush(QtGui.QColor(0, 0, 0, 255))
        for snakeCell in self.snake.cellArray:
            qp.drawRect(snakeCell.x, snakeCell.y, CELL_SIZE, CELL_SIZE)

    def resetClicked(self):
        self.scoreLcd.display(0)
        self.update()
        self.new_game()

    def pause(self):
        self.isPaused = True
        self.timer.stop()
        self.statusbar.showMessage('Paused')
        self.update()

    def start(self):
        self.isPaused = False
        self.timer.start(self.speed, self)
        self.statusbar.showMessage('Playing')
        self.update()

    def new_game(self):
        self.timer = QtCore.QBasicTimer()
        self.snake = Snake()
        self.direction = Direction.RIGHT
        self.isPaused = False
        self.food = 0
        self.speed = 100

    def exit(self):
        self.close()


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())
