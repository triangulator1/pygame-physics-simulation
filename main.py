import os
from turtle import width
import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 800, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elevator Simulation")

WHITE = (255,255,255)
GRAY = (102, 92, 92)
LIGHT_BLUE = (203,228,242)
DARK_GRAY = (36,33,35)
RED = (200, 50, 25)

# all quantities are in their respective SI units (e.g. speed is in ms-1 and distance is in meters) 

GRAVITY = 10 #defines magnitude of acceleration due to gravity
DRAG = 0.9 #lower number increase deceleration of object
ELASTICITY = 0.75 #defines the decrease in speed after object collisions

FPS = 60


def binary_search(arr, low, high, x): #recursive searching algorithm to find values
    if high >= low:
        mid = (high + low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)
        else:
            return binary_search(arr, mid + 1, high, x)
    else:
        return -1

def pointInRectangle(px, py, rw, rh, rx, ry): #finds if mouse click is inside a given area
    if px > rx and px < rx  + rw:
        if py > ry and py < ry + rh:
            return True
    return False

class Slider:
    def __init__(self, position:tuple, upperValue:int=3, sliderWidth:int = 30, text:str="Magnetic force: ",
                 outlineSize:tuple=(300, 100))->None:
        self.position = position
        self.outlineSize = outlineSize
        self.text = text
        self.sliderWidth = sliderWidth
        self.upperValue = upperValue
        
    #returns the current value of the slider
    def getValue(self)->float:
        return self.sliderWidth / (self.outlineSize[0] / self.upperValue)

    #displays slider and the text showing the value of the slider
    def display(self, display:pygame.display)->None:
        #draw outline and slider rectangles
        pygame.draw.rect(display, (0, 0, 0), (self.position[0], self.position[1], 
                                              self.outlineSize[0], self.outlineSize[1]), 3)
        
        pygame.draw.rect(display, (0, 0, 0), (self.position[0], self.position[1], 
                                              self.sliderWidth, self.outlineSize[1] - 10))

        self.font = pygame.font.Font(pygame.font.get_default_font(), int((15/100)*self.outlineSize[1]))

        #create text surface with value
        valueSurf = self.font.render(f"{self.text}: {round(self.getValue(), 2)}", True, (200, 50, 100))
        
        #centre text
        textx = self.position[0] + (self.outlineSize[0]/2) - (valueSurf.get_rect().width/2)
        texty = self.position[1] + (self.outlineSize[1]/2) - (valueSurf.get_rect().height/2)

        display.blit(valueSurf, (textx, texty))

    #allows users to change value of the slider by dragging it.
    def changeValue(self)->None:
        #If mouse is pressed and mouse is inside the slider
        mousePos = pygame.mouse.get_pos()
        if pointInRectangle(mousePos[0], mousePos[1]
                            , self.outlineSize[0], self.outlineSize[1], self.position[0], self.position[1]):
            if pygame.mouse.get_pressed()[0]:
                #the size of the slider
                self.sliderWidth = mousePos[0] - self.position[0]

                #limit the size of the slider
                if self.sliderWidth < 1:
                    self.sliderWidth = 0
                if self.sliderWidth > self.outlineSize[0]:
                    self.sliderWidth = self.outlineSize[0]
    

class Elevator:
    def __init__(self, x, y, image):
        self.x = x 
        self.y = y 
        self.height = 120
        self.width = 98
        self.mass = 500
        self.image = image
        self.speed = 0
        self.time_taken = 0
        self.collision = False
    def display(self): 
        WIN.blit(self.image, (self.x, self.y))
    def move(self): #note - height between two magnets is 351-16-16 = 319 meters, accel = 10 ms-2
        #first get direction and check for any collisions 
        self.time_taken += 1
        if self.y < MAGNET1.y + MAGNET1.height:
            if not self.collision:
                self.collision = True
                self.speed = 0
                MAGNET1.angle = 0
        elif self.y + self.height > MAGNET2.y:
            if not self.collision:
                self.collision = True
                self.speed = 0
                MAGNET2.angle = math.pi
        else:
            self.collision = False
            MAGNET1.angle = math.pi
            MAGNET2.angle = 0
        #evaluating all forces
        STRENGTH1 = math.cos(MAGNET1.angle) * MAGNET1.strength / 6 #vector acceleration of magnet1
        STRENGTH2 = math.cos(MAGNET2.angle) * MAGNET2.strength / 6 #vector acceleration of magnet2
        self.speed += (GRAVITY + STRENGTH1 + STRENGTH2)*(1/60) #first equation of motion
        self.y += self.speed*(1/60) + (1/2)*(GRAVITY + STRENGTH1 + STRENGTH2)*(1/60**2) #second equation of motion
        if self.time_taken % 15 == 0:
            print("Time: ", self.time_taken / 60, " seconds")
    def automate_movement(self, lvl): #makes movement to floors (levels) automatic 
        #algo:
        # take user input for level
        # magnets increase/decrease their strength to bring the lift up or down
        # once the lift is near the floor, the magnets try to bring the lift to a stop
        # lift should stop exactly at lvl_y 
        lvl_y = HEIGHT - (lvl * 117) #greater lvl_y value means a lower level
        #lvl = 2, lvl_y = 266
        if lvl_y + 50 > self.y and lvl_y - 50 < self.y:
            if MAGNET1.strength > MAGNET2.strength:
                MAGNET1.strength
        if self.y > lvl_y: #lift is below the required level
            MAGNET1.strength += 0.05
            MAGNET2.strength -= 0.01
        elif self.y < lvl_y:
            MAGNET1.strength -= 0.01
            MAGNET2.strength += 0.05
                
            STRENGTH1 = math.cos(MAGNET1.angle) * MAGNET1.strength / 6 #vector acceleration of magnet1
            STRENGTH2 = math.cos(MAGNET2.angle) * MAGNET2.strength / 6 #vector acceleration of magnet2
        self.speed += (GRAVITY + STRENGTH1 + STRENGTH2)*(1/60) #first equation of motion
        self.y += self.speed*(1/60) + (1/2)*(GRAVITY + STRENGTH1 + STRENGTH2)*(1/60**2) #second equation of motion

            

class Magnet:
    def __init__(self, x, y, width, height, angle, teslas):
        self.x = x 
        self.y = y 
        self.width = width
        self.height = height
        self.angle = angle
        self.charge = 5
        self.teslas = teslas/1000
        #calculate magnitude of acceleration 
    def display(self):
        pygame.draw.rect(WIN, GRAY, pygame.Rect(self.x, self.y, self.width, self.height))
    def calculate(self):
        try:
            self.strength = ELEVATOR.mass * GRAVITY / self.teslas * self.charge #lorentz formula, strength is acceleration due to magnetic force
            self.strength /= 3600
        except: #teslas entered is 0
            self.strength = 0


class PlayButton:
    def __init__(self, x, y):
        self.x = x
        self.y = y 
        self.image = pygame.image.load(os.path.join('assets', 'play_button.png'))
        self.height = 256
        self.width = 256
        self.active = False #boolean flag, if true then simulation will run
    def display(self): #displays itself
        WIN.blit(self.image, (self.x, self.y))
    def handle_click(self, event): #runs when button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if mouseX > self.x and mouseX < self.width + self.x and mouseY > self.y and mouseY < self.height + self.y: #checks if clicked
                if self.active: 
                    self.active = False
                    self.image = pygame.image.load(os.path.join('assets', 'play_button.png'))
                else:
                    self.active = True
                    self.image =  pygame.image.load(os.path.join('assets', 'pause_button.png'))
                
                    

#defining all objects

BLOCK_IMAGE1 = pygame.image.load(os.path.join('assets', 'block_image.png'))
ELEVATOR = Elevator(200, 32, pygame.image.load(os.path.join('assets', 'elevator_image.png')))
MAGNET1 = Magnet(197, 16, 101, 16, math.pi, 0)
MAGNET2 = Magnet(197, 468, 101, 16, 0, 0)
SLIDER1 = Slider((450, 50))
SLIDER2 = Slider((450, 200))
PLAY = PlayButton(500, 400)


def simulate_physics(): #begins simulation 
    ELEVATOR.move()

def draw_window(): #drawing all objects
    WIN.fill(LIGHT_BLUE)
    PLAY.display()
    ELEVATOR.display()
    MAGNET1.display()
    MAGNET2.display()
    WIN.blit(BLOCK_IMAGE1, (180, 367))
    WIN.blit(BLOCK_IMAGE1, (297, 367))
    WIN.blit(BLOCK_IMAGE1, (180, 250))
    WIN.blit(BLOCK_IMAGE1, (297, 250))
    WIN.blit(BLOCK_IMAGE1, (180, 133))
    WIN.blit(BLOCK_IMAGE1, (297, 133))
    WIN.blit(BLOCK_IMAGE1, (180, 16))
    WIN.blit(BLOCK_IMAGE1, (297, 16))
    SLIDER1.display(WIN)
    SLIDER1.changeValue()
    SLIDER2.display(WIN)
    SLIDER2.changeValue()
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            PLAY.handle_click(event) #checks if play button has been clicked
        draw_window()
        if PLAY.active: #simulation begins
            MAGNET1.teslas = SLIDER1.getValue()
            MAGNET2.teslas = SLIDER2.getValue()
            MAGNET1.calculate()
            MAGNET2.calculate()
            simulate_physics()

    pygame.quit()

if __name__ == "__main__":
    main()