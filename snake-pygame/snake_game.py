import pygame
import random
from enum import Enum
from collections import namedtuple

# needed to initialize the pygame modules
pygame.init()

# initialize a font to render score and other data in game screen
# font name is arial with size 25
font = pygame.font.SysFont("arial", 25)

# a block size for coordinate reference in game window
BLOCK_SIZE = 20

# clock framerate parameters, fps rate
SPEED = 10

# constant color rbg values
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

# class Directions to set unique directions values to reduce ambiguity
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Point is an object of named tuple, which can be used to access x and y names or values
Point = namedtuple("Point", ["x", "y"])

class SnakeGame():
    
    # initialization of values
    def __init__(self, width = 640, height = 480):
        """
        width : game window width
        height : game window height
        """
        self.width = width
        self.height = height
        
        # initialize the game window
        
        # pygame.display.set_mode(size = (width, height)) : Initialize a window or screen for display
        self.display = pygame.display.set_mode((self.width, self.height))
        
        # pygame.display.set_caption("title") : set the current window caption
        pygame.display.set_caption("Snake Game")
        
        # pygame.time.Clock() : create an object to help track time.
        self.clock = pygame.time.Clock()
        
        # initialize game start state
        # initialize snake
        # initialize food
        
        # initialize snake direction
        self.direction = Direction.RIGHT
        
        # initialize snake head
        self.head = Point(self.width/2, self.height/2)
        
        # creating snake uses 3 coordinate points
        # very first snake is of 3 block sizes, thats why there are 3 coordinate points for the snake
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        
        # score points
        self.score = 0
        
        # Food position initialization
        self.food = None
        # a helper function to set food at random positions
        self._place_food()
        
    def _place_food(self):
        """
        Gives a random coordinate point in terms of block size within the game window
        and, calls itself recursively if the random point is generated inside the body of snake
        """
        x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self):
        """
        1. collect user input
        2. move our snake based on user input
        3. check if game is over due to action
            - quit if game is over
        4. place new food or just move the snake based on last action
        5. update the pygame UI and clock
        6. return game over and score
        """
        
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        # 2. move
        # _move() function updates the snake head
        self._move(self.direction)
        self.snake.insert(0, self.head)
        
        # 3. check if the game is over
        # game over conditions:
        # - Snake eats itself.
        # - Snake hits the boundary
        
        # current game over flag
        game_over = False
        
        if self._is_collision():
            game_over = True
            return game_over, self.score
        
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        
        else:
            self.snake.pop()
        
        # 5. update the pygame UI and clock
        self._update_ui()
        
        # incrementing the pygame clock object created above by a certain unit defined
        # SPEED set at 40 fps means the program will never run at more than 40 frames per second.
        self.clock.tick(SPEED)
        
        
        
        return game_over, self.score
    
    def _is_collision(self):
        # hits the boundary
        if self.head.x > self.width - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.height - BLOCK_SIZE or self.head.y < 0:
            return True
            
        # hits itself
        if self.head in self.snake[1:]:
            return True
        
        return False
    
    def _move(self, direction):
        # current coordinates for head of the snake
        x = self.head.x
        y = self.head.y
        
        # check current direction of snake
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        
        self.head = Point(x,y)
    
    def _update_ui(self):
        # order is important for UI 
        
        # 1. fill the game window with a solid color
        self.display.fill(BLACK)
        
        # 2. drawing the snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
            
        # 3. drawing the  food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
                
        # 4. drawing score in the game screen
        # font.render(text, antialias, color, background = None)
        # antialias is a boolean argumant, if true the character will have smooth edges
        text = font.render("Score: " + str(self.score), True, WHITE)
        
        # blit or overlap the surface on the canvas at the given position
        # for more information on blit, please go through the below link:
        # https://stackoverflow.com/questions/37800894/what-is-the-surface-blit-function-in-pygame-what-does-it-do-how-does-it-work
        # Inshort we are trying to draw whatever is there in text object in the (0,0) position
        self.display.blit(text, [0,0])
        
        # updates the screen regulary
        pygame.display.flip()

if __name__ == "__main__":
    
    # creating object of our SnakeGame class
    game = SnakeGame()
    
    # game loop
    while True:
        
        # function defining an action at each step
        game_over, score = game.play_step()
        
        # break condition
        # break if game over
        if game_over == True:
            break
    
    print("Current score : ", score)
    
    # closing all the pygame modules
    pygame.quit()