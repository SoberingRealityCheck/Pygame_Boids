'''
This is the main function for the boids simulation.

'''
import os
print(os.getcwd())

from . import tools, prepare

def main():
    print("Hello, world!")
    app = tools.Control(prepare.ORIGINAL_CAPTION)
    app.main()