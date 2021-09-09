# -*- coding: utf-8 -*-
"""RetoTest.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gCoKGpaMXEG5P94XDWxiqWovzcLikCXS
"""


# -*- coding: utf-8 -*-
"""Reto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r5GwnHmrFHmG1A6Hu2Wr9asofWhPc7_w
"""


# mathplotlib lo usamos para graficar/visualizar como evoluciona el autómata celular.
# %matplotlib inline
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Definimos los siguientes paquetes para manejar valores númericos.


class Move(Agent):
    # Inicializacion
    grid = None
    x = None
    y = None
    moore = False
    include_center = False

    def __init__(self, unique_id, pos, model, moore=False):

        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    def move(self):
        next_moves = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False)
        posicion_azar = np.random.choice(next_moves)
        if self.model.grid.is_cell_empty(posicion_azar):
            self.movimientos += 1


Lights = []
light_state = []
carCounter = 0
CarsA = []
CarsB = []
CarsC = []
CarsD = []
gen = 0
carsDone = 0


def get_grid(model):

    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        for agent in cell_content:
            grid[x][y] = agent.height
    return grid


class UC(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.contador = 0
        self.height = 0
        self.step_count = 0
        self.inBetween = 0
        self.isStart = True

    def allEmpty(self):
        global carCounter
        carCounter = 0
        for i in range(4):
            if light_state[i].check_car():
                carCounter += 1
        if carCounter == 0:
            carCounter = 0
            return True
        return False

    def oneYellow(self):
        global carCounter
        carCounter = 0
        index = ''
        for i in range(4):
            if light_state[i].check_car():
                carCounter += 1
                index = i
        if carCounter == 1:
            carCounter = 0
            return index
        return -1

    def setAllRed(self):
        light_state[self.contador].state = 6
        light_state[self.contador-1].state = 6
        light_state[self.contador-2].state = 6
        light_state[self.contador-3].state = 6

    def change_light(self):
        if self.allEmpty():
            light_state[self.contador].state = 7
            light_state[self.contador-1].state = 7
            light_state[self.contador-2].state = 7
            light_state[self.contador-3].state = 7
            return
        yellowIndex = self.oneYellow()
        if yellowIndex != -1:
            print('entro yellow')
            light_state[yellowIndex].state = 8
            light_state[yellowIndex-1].state = 6
            light_state[yellowIndex-2].state = 6
            light_state[yellowIndex-3].state = 6
            return
        if self.contador == 3:
            if light_state[self.contador].check_car():
                light_state[self.contador-1].state = 6
                light_state[self.contador-2].state = 6
                light_state[self.contador-3].state = 6
                light_state[self.contador].state = 8
                self.contador = 0
            else:
                self.contador = 0
                self.change_light()
        else:
            if light_state[self.contador].check_car():
                light_state[self.contador-1].state = 6
                light_state[self.contador-2].state = 6
                light_state[self.contador-3].state = 6
                light_state[self.contador].state = 8
                self.contador += 1
            else:
                self.contador += 1
                self.change_light()

    def step(self):
        if self.step_count == 5:
            self.inBetween += 1
        else:
            self.step_count += 1

    def advance(self):
        if self.isStart:
            self.change_light()
            self.isStart = False
        if self.step_count == 5:
            self.setAllRed()
        if self.inBetween > 6:
            self.change_light()
            self.step_count = 0
            self.inBetween = 0


class Light(Agent):
    # global Lights=list(((8,5),(8,8),(5,8),(5,5)))
    def __init__(self, unique_id, model, direction):
        super().__init__(unique_id, model)
        self.state = 7  # rojo = 6, amarillo=7, verde =8
        self.height = self.state
        self.direction = direction

    def check_car(self):
        neighbours = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False,)
        for neighbor in neighbours:
            if isinstance(neighbor, Car) and neighbor.direction == self.direction:
                return True
        return False

    def step(self):
        self.check_car()
        self.height = self.state


class Car(Agent):
    def __init__(self, unique_id, model, direction, vuelta):
        super().__init__(unique_id, model)
        self.height = .05
        self.vuelta = vuelta  # 0 = izquierda, 1=recto, 2=derecha
        self.is_moving = True
        self.direction = direction
        self.once_light = False  # ver si ya paso un semaforo

    def canIMoveThere(self, pos):
        neighbours = self.model.grid.get_neighbors(
            self.pos,
            moore=False,
            include_center=False)
        for neighbour in neighbours:
            if (isinstance(neighbour, Car) and neighbour.pos == pos and neighbour.height > 1):
                return False
        return True

    def checkBoundaries(self, pos, posNext):
        global carsDone, CarsA, CarsB, CarsC, CarsD
        randomList = np.random.randint(1, 4)
        newDirection = ''
        newList = []
        randomPos = np.random.randint(0, 1)
        newVuelta = 0
        if randomList == 1:
            newDirection = 'A'
            newList = CarsA
            newPos = newList[randomPos]
            if (newPos[0] == 7):
                newVuelta = np.random.choice([0, 1])
            elif (newPos[0] == 8):
                newVuelta = np.random.choice([1, 2])
        if randomList == 2:
            newDirection = 'B'
            newList = CarsB
            newPos = newList[randomPos]
            if (newPos[1] == 7):
                newVuelta = np.random.choice([0, 1])
            elif (newPos[1] == 8):
                newVuelta = np.random.choice([1, 2])
        if randomList == 3:
            newDirection = 'C'
            newList = CarsC
            newPos = newList[randomPos]
            if (newPos[0] == 6):
                newVuelta = np.random.choice([0, 1])
            elif (newPos[0] == 5):
                newVuelta = np.random.choice([1, 2])
        if randomList == 4:
            newDirection = 'D'
            newList = CarsD
            newPos = newList[randomPos]
            if (newPos[1] == 6):
                newVuelta = np.random.choice([0, 1])
            elif (newPos[1] == 5):
                newVuelta = np.random.choice([1, 2])

        x, y = pos
        xNext, yNext = posNext
        if self.model.grid.out_of_bounds(posNext):
            self.model.grid.move_agent(self, (newPos))
            self.direction = newDirection
            self.is_moving = True
            self.once_light = False
            self.vuelta = newVuelta
            return False
        # if (x == 0 and xNext == -1):
        #     self.model.grid.move_agent(self, (newPos))
        #     self.direction = newDirection
        #     self.is_moving = True
        #     self.once_light = False
        #     self.vuelta = newVuelta
        #     return False
        # if (y == 0 and yNext == -1):
        #     self.model.grid.move_agent(self, (newPos))
        #     self.direction = newDirection
        #     self.is_moving = True
        #     self.once_light = False
        #     self.vuelta = newVuelta
        #     return False
        # if (x == self.model.height - 1 and xNext == self.model.height):
        #     self.model.grid.move_agent(self, (newPos))
        #     self.direction = newDirection
        #     self.is_moving = True
        #     self.once_light = False
        #     self.vuelta = newVuelta
        #     return False
        # if (y == self.model.width - 1 and yNext == self.model.width):
        #     self.model.grid.move_agent(self, (newPos))
        #     self.direction = newDirection
        #     self.is_moving = True
        #     self.once_light = False
        #     self.vuelta = newVuelta
        #     return False
        return True

    def turnLeft(self):
        x, y = self.pos
        if (self.direction == 'A'):
            if (y != 7):
                if self.checkBoundaries(self.pos, (x, y+1)) and self.canIMoveThere((x, y+1)):
                    self.model.grid.move_agent(self, (x, y+1))
            elif self.checkBoundaries(self.pos, (x-1, y)) and self.canIMoveThere((x-1, y)):
                self.model.grid.move_agent(self, (x-1, y))

        if (self.direction == 'B'):
            if (x != 6):
                if self.checkBoundaries(self.pos, (x-1, y)) and self.canIMoveThere((x-1, y)):
                    self.model.grid.move_agent(self, (x-1, y))
            elif self.checkBoundaries(self.pos, (x, y-1)) and self.canIMoveThere((x, y-1)):
                self.model.grid.move_agent(self, (x, y-1))

        if (self.direction == 'C'):
            if (y != 6):
                if self.checkBoundaries(self.pos, (x, y-1)) and self.canIMoveThere((x, y-1)):
                    self.model.grid.move_agent(self, (x, y-1))
            elif self.checkBoundaries(self.pos, (x+1, y)) and self.canIMoveThere((x+1, y)):
                self.model.grid.move_agent(self, (x+1, y))

        if (self.direction == 'D'):
            if (x != 7):
                if self.checkBoundaries(self.pos, (x+1, y)) and self.canIMoveThere((x+1, y)):
                    self.model.grid.move_agent(self, (x+1, y))
            elif self.checkBoundaries(self.pos, (x, y+1)) and self.canIMoveThere((x, y+1)):
                self.model.grid.move_agent(self, (x, y+1))

    def turnRight(self):
        x, y = self.pos

        if (self.direction == 'A'):
            if (y != 5):
                if self.checkBoundaries(self.pos, (x, y+1)) and self.canIMoveThere((x, y+1)):
                    self.model.grid.move_agent(self, (x, y+1))
            elif self.checkBoundaries(self.pos, (x+1, y)) and self.canIMoveThere((x+1, y)):
                self.model.grid.move_agent(self, (x+1, y))

        if (self.direction == 'B'):
            if (x != 8):
                if self.checkBoundaries(self.pos, (x-1, y)) and self.canIMoveThere((x-1, y)):
                    self.model.grid.move_agent(self, (x-1, y))
            elif self.checkBoundaries(self.pos, (x, y+1)) and self.canIMoveThere((x, y+1)):
                self.model.grid.move_agent(self, (x, y+1))

        if (self.direction == 'C'):
            if (y != 8):
                if self.checkBoundaries(self.pos, (x, y-1)) and self.canIMoveThere((x, y-1)):
                    self.model.grid.move_agent(self, (x, y-1))
            elif self.checkBoundaries(self.pos, (x-1, y)) and self.canIMoveThere((x-1, y)):
                self.model.grid.move_agent(self, (x-1, y))

        if (self.direction == 'D'):
            if (x != 5):
                if self.checkBoundaries(self.pos, (x+1, y)) and self.canIMoveThere((x+1, y)):
                    self.model.grid.move_agent(self, (x+1, y))
            elif self.checkBoundaries(self.pos, (x, y-1)) and self.canIMoveThere((x, y-1)):
                self.model.grid.move_agent(self, (x, y-1))

    def turnStraight(self):
        x, y = self.pos
        if (self.direction == 'A'):
            if self.checkBoundaries(self.pos, (x, y+1)) and self.canIMoveThere((x, y+1)):
                self.model.grid.move_agent(self, (x, y+1))
        if (self.direction == 'B'):
            if self.checkBoundaries(self.pos, (x-1, y)) and self.canIMoveThere((x-1, y)):
                self.model.grid.move_agent(self, (x-1, y))
        if (self.direction == 'C'):
            if self.checkBoundaries(self.pos, (x, y-1)) and self.canIMoveThere((x, y-1)):
                self.model.grid.move_agent(self, (x, y-1))
        if (self.direction == 'D'):
            if self.checkBoundaries(self.pos, (x+1, y)) and self.canIMoveThere((x+1, y)):
                self.model.grid.move_agent(self, (x+1, y))

    def brakeLight(self):
        global carCounter
        neighbours = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False,)
        for neighbor in neighbours:
            if isinstance(neighbor, Light) and neighbor.direction == self.direction and self.once_light == False:
                if neighbor.state == 7 and carCounter == 1:  # Yellow Light
                    self.is_moving = False
                elif neighbor.state != 8:  # Green light
                    self.is_moving = False
                else:  # Red Light
                    self.is_moving = True
                    self.once_light = True

    def move(self):
        if self.vuelta == 0:
            self.turnLeft()
        if self.vuelta == 1:
            self.turnStraight()
        if self.vuelta == 2:
            self.turnRight()

    def step(self):
        self.brakeLight()

    def advance(self):
        if self.is_moving:
            self.move()


class Street(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.height = 1


class IntersectionModel(Model):
    def __init__(self, width, height, maxCars):
        self.grid = MultiGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.width = width
        self.height = height
        self.carCounter = 0
        self.maxCars = maxCars
        global CarsA, CarsB, CarsC, CarsD, gen
        self.resetGlobalVariables()
        CarsA = list(((7, 0), (8, 0)))
        CarsB = list(((13, 7), (13, 8)))
        CarsC = list(((5, 13), (6, 13)))
        CarsD = list(((0, 5), (0, 6)))
        Lights = list(((8, 5), (8, 8), (5, 8), (5, 5)))

        Directions = list(('A', 'B', 'C', 'D'))

        # Lights
        for z in range(4):
            l = Light(Lights[z], self, Directions[z])
            global light_state
            light_state.append(l)
            self.grid.place_agent(l, Lights[z])
            self.schedule.add(l)

        # Aquí definimos con colector para obtener el grid completo.
        # self.datacollector = DataCollector(
        #     agent_reporters={
        #         "height": "height",
        #         "X": lambda a: a.pos[0],
        #         "Y": lambda a: a.pos[1]
        #     }
        # )

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid},
            agent_reporters={
                "X": lambda a: a.pos[0],
                "Y": "height",
                "Z": lambda a: a.pos[1]
            }
        )

        # self.datacollector = DataCollector(model_reporters={"Grid": get_grid})

        # UC
        uc = UC(1, self)
        self.grid.place_agent(uc, (0, 0))
        self.schedule.add(uc)
        # Cars
        for i in range(self.maxCars):
            print('placeCar')
            self.agentPlacer()

    def resetGlobalVariables(self):
        global Lights, light_state, carCounter, CarsA, CarsB, CarsC, CarsD, gen, carsDone
        Lights = []
        light_state = []
        carCounter = 0
        CarsA = []
        CarsB = []
        CarsC = []
        CarsD = []
        gen = 0
        carsDone = 0

    def placeCarA(self):
        global CarsA, gen
        gen += 1
        z = np.random.choice([0, 1])
        x, y = CarsA[z]
        if (x == 7):
            vuelta = np.random.choice([0, 1])
        elif (x == 8):
            vuelta = np.random.choice([1, 2])
        c = Car((CarsA[z], gen), self, 'A', vuelta)
        self.grid.place_agent(c, CarsA[z])
        self.schedule.add(c)

    def placeCarB(self):
        global CarsB, gen
        gen += 1
        z = np.random.choice([0, 1])
        x, y = CarsB[z]
        if (y == 7):
            vuelta = np.random.choice([0, 1])
        elif (y == 8):
            vuelta = np.random.choice([1, 2])
        c = Car((CarsB[z], gen), self, 'B', vuelta)
        self.grid.place_agent(c, CarsB[z])
        self.schedule.add(c)

    def placeCarC(self):
        global CarsC, gen
        gen += 1
        z = np.random.choice([0, 1])
        x, y = CarsC[z]
        if (x == 6):
            vuelta = np.random.choice([0, 1])
        elif (x == 5):
            vuelta = np.random.choice([1, 2])
        c = Car((CarsC[z], gen), self, 'C', vuelta)
        self.grid.place_agent(c, CarsC[z])
        self.schedule.add(c)

    def placeCarD(self):
        global CarsD, gen
        gen += 1
        z = np.random.choice([0, 1])
        x, y = CarsD[z]
        if (y == 6):
            vuelta = np.random.choice([0, 1])
        elif (y == 5):
            vuelta = np.random.choice([1, 2])
        c = Car((CarsD[z], gen), self, 'D', vuelta)
        self.grid.place_agent(c, CarsD[z])
        self.schedule.add(c)

    def agentPlacer(self):
        print('ran agent placer')
        # Cars
        global CarsA, CarsB, CarsC, CarsD
        randomList = np.random.randint(1, 4)
        if randomList == 1:
            self.placeCarA()
        if randomList == 2:
            self.placeCarB()
        if randomList == 3:
            self.placeCarC()
        if randomList == 4:
            self.placeCarD()

    def allCarsDone(self):
        global carsDone
        if carsDone == self.maxCars:
            return True
        return False

    def getPosition(self):
        all_grid = self.datacollector.get_agent_vars_dataframe()
        tail = all_grid.tail(self.maxCars + 5)

        posList = tail.values.tolist()
        return posList

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


# Max RunTime
# Amount of Cars
maxCars = 5

frameCounter = 0
i = 100

model = IntersectionModel(14, 14, maxCars)
while (i >= 0):
    frameCounter += 1
    model.step()
    print(model.getPosition())
    i -= 1

# all_grid = model.datacollector.get_agent_vars_dataframe()
# # print(all_grid.values.tolist()[0][1])
# all_grid = model.datacollector.get_model_vars_dataframe()


# # % % capture

# fig, axs = plt.subplots(figsize=(7, 7))
# axs.set_xticks([])
# axs.set_yticks([])
# patch = plt.imshow(all_grid.iloc[0][0], cmap=plt.cm.Greens)
# plt.colorbar()


# def animate(i):
#     patch.set_data(all_grid.iloc[i][0])


# anim = animation.FuncAnimation(fig, animate, frames=frameCounter-1)
# anim

# # # Numero de Movimientos Realizados por los Agentes
# # print('Numero de Movimientos Realizados: ', frameCounter)
