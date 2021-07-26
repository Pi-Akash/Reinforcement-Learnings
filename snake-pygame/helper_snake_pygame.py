# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 23:53:56 2021

@author: P Akash
"""

import matplotlib.pyplot as plt
from IPython import display


def plot(scores, mean_scores):
    # clear the output of the current cell receiving output
    display.clear_output(wait = True)
    
    # display a python object in all frontends
    # plt.gcf(), if no current figure exists, a new one is created using figure()
    display.display(plt.gcf())
    
    # plt.clf(), clear the current figure
    plt.clf()
    
    plt.title("Training...")
    plt.xlabel("Number of games")
    plt.ylabel("Score")
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin = 0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))

