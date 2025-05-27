'''
This project is my latest attempt at creating a boids simulation using pygame. I had pretty substantial issues with performance in 
my last attempt, so I decided to start from scratch and try to do things differently.
This time, I'm using a more object-oriented approach, where each boid is an object with its own properties and methods.
I'm putting much more effort into structuring the code in this one and making it more modular, 
along with trying to see if I can utilize the GPU for the more intensive calculations in the simulation to 
improve performance.

I've been using Mekire's cabbages-and-kings repository as a reference for the structure of the code, as I think it's a really nice example of how to
cleanly structure a large and complex pygame project that will give me a lot of flexibility when it comes to future development. 

- Clay, 5/11/2025
'''


import sys
import pygame as pg
from data.main import main 

if __name__ == "__main__":
    main()
    pg.quit()
    sys.exit()