'''
the main game
author:@techwithtim
requirements:see requirements.txt
'''

import subprocess
import sys
import get_pip

def install(package):
    """
    Installs a given package using pip.
    
    :param package: The name of the package to install.
    """
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    print("[GAME] Trying to import pygame")
    import pygame
except:
    print("[EXCEPTION] Pygame not installed")

    try:
        print("[GAME] Trying to install pygame via pip")
        import pip
        install("pygame")
        print("[GAME] Pygame has been installed")
    except:
        print("[EXCEPTION] Pip not installed on system")
        print("[GAME] Trying to install pip")
        get_pip.main()
        print("[GAME] Pip has been installed")
        try:
            print("[GAME] Trying to install pygame")
            import pip
            install("pygame")
            print("[GAME] Pygame has been installed")
        except:
            print("[ERROR 1] Pygame could not be installed")


import pygame
import os
import time
from client import Network
import pickle

HEIGHT = 750
WIDTH = 750
X_COORDINATE = 113
Y_COORDINATE = 113
BOARD_WIDTH = 525
BOARD_HEIGHT = 525

pygame.font.init()

board = pygame.transform.scale(pygame.image.load(os.path.join("img","board_alt.png")), (WIDTH, HEIGHT))
chessbg = pygame.image.load(os.path.join("img", "chessbg.png"))
rect = (X_COORDINATE,Y_COORDINATE,BOARD_WIDTH,BOARD_HEIGHT)

turn = "w"


def menu_screen(win, name):
    """
    Displays the main menu screen and attempts to connect to the server.
    
    :param win: The game window surface.
    :param name: The player's name.
    """
    
    global bo, chessbg
    run = True
    offline = False

    while run:
        win.blit(chessbg, (0,0))
        small_font = pygame.font.SysFont("comicsans", 50)
        
        if offline:
            off = small_font.render("Server Offline, Try Again Later...", 1, (255, 0, 0))
            win.blit(off, (width / 2 - off.get_width() / 2, 500))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                offline = False
                try:
                    bo = connect()
                    run = False
                    main()
                    break
                except:
                    print("Server Offline")
                    offline = True


    
def redraw_gameWindow(win, bo, p1, p2, color, ready):
    """
    Redraws the game window with the current board state, timers, and UI elements.
    
    :param win: The game window surface.
    :param bo: The board object representing the game state.
    :param p1: Time remaining for player 1 in seconds.
    :param p2: Time remaining for player 2 in seconds.
    :param color: The player's color ('w' for white, 'b' for black, 's' for spectator).
    :param ready: Whether both players are ready.
    """
    
    win.blit(board, (0, 0))
    bo.draw(win, color)

    formatTime1 = str(int(p1//60)) + ":" + str(int(p1%60))
    formatTime2 = str(int(p2 // 60)) + ":" + str(int(p2 % 60))
    if int(p1%60) < 10:
        formatTime1 = formatTime1[:-1] + "0" + formatTime1[-1]
    if int(p2%60) < 10:
        formatTime2 = formatTime2[:-1] + "0" + formatTime2[-1]

    font = pygame.font.SysFont("comicsans", 30)
    try:
        txt = font.render(bo.p1Name + "\'s Time: " + str(formatTime2), 1, (255, 255, 255))
        txt2 = font.render(bo.p2Name + "\'s Time: " + str(formatTime1), 1, (255,255,255))
    except Exception as e:
        print(e)
    win.blit(txt, (520,10))
    win.blit(txt2, (520, 700))

    txt = font.render("Press q to Quit", 1, (255, 255, 255))
    win.blit(txt, (10, 20))

    if color == "s":
        txt3 = font.render("SPECTATOR MODE", 1, (255, 0, 0))
        win.blit(txt3, (width/2-txt3.get_width()/2, 10))

    if not ready:
        show = "Waiting for Player"
        if color == "s":
            show = "Waiting for Players"
        font = pygame.font.SysFont("comicsans", 80)
        txt = font.render(show, 1, (255, 0, 0))
        win.blit(txt, (width/2 - txt.get_width()/2, 300))

    if not color == "s":
        font = pygame.font.SysFont("comicsans", 30)
        if color == "w":
            txt3 = font.render("YOU ARE WHITE", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 10))
        else:
            txt3 = font.render("YOU ARE BLACK", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 10))

        if bo.turn == color:
            txt3 = font.render("YOUR TURN", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 700))
        else:
            txt3 = font.render("THEIR TURN", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 700))

    pygame.display.update()


def end_screen(win, text):
    """
    Displays the end screen with the given text message.
    
    :param win: The game window surface.
    :param text: The message to display (e.g., winner announcement).
    """
    
    pygame.font.init()
    font = pygame.font.SysFont("comicsans", 80)
    txt = font.render(text,1, (255,0,0))
    win.blit(txt, (width / 2 - txt.get_width() / 2, 300))
    pygame.display.update()

    pygame.time.set_timer(pygame.USEREVENT+1, 3000)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                run = False
            elif event.type == pygame.KEYDOWN:
                run = False
            elif event.type == pygame.USEREVENT+1:
                run = False


def click(pos):
    """
    Converts screen coordinates to board indices.
    
    :param pos: The (x, y) screen position of the mouse click.
    :return: A tuple (i, j) representing board indices (0-7) or (-1, -1) if outside the board.
    """
    
    x = pos[0]
    y = pos[1]
    if rect[0] < x < rect[0] + rect[2]:
        if rect[1] < y < rect[1] + rect[3]:
            divX = x - rect[0]
            divY = y - rect[1]
            i = int(divX / (rect[2]/8))
            j = int(divY / (rect[3]/8))
            return i, j

    return -1, -1


def connect():
    """
    Establishes a network connection and retrieves the game board.
    
    :return: The board object received from the server.
    """
    
    global n
    n = Network()
    return n.board

def send_winner(bo):
    """
    Sends winner to the board

    :param bo: board object"
    :return: updated board object
    """
    
    if p1Time <= 0:
        bo = n.send("winner b")
    elif p2Time <= 0:
        bo = n.send("winner w")

    if bo.check_mate("b"):
        bo = n.send("winner b")
    elif bo.check_mate("w"):
        bo = n.send("winner w")
    return bo

def main():
    """
    The main game loop that handles game state updates, user input, and rendering.
    """

    global turn, bo, name

    color = bo.start_user
    count = 0

    bo = n.send("update_moves")
    bo = n.send("name " + name)
    clock = pygame.time.Clock()
    run = True

    while run:
        if not color == "s":
            p1Time = bo.time1
            p2Time = bo.time2
            if count == 60:
                bo = n.send("get")
                count = 0
            else:
                count += 1
            clock.tick(30)

        try:
            redraw_gameWindow(win, bo, p1Time, p2Time, color, bo.ready)
        except Exception as e:
            print(e)
            end_screen(win, "Other player left")
            run = False
            break

        if not color == "s":
            bo = send_winner(bo)
        
        if bo.winner == "w":
            end_screen(win, "White is the Winner!")
            run = False
        elif bo.winner == "b":
            end_screen(win, "Black is the winner")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and color != "s":
                    # quit game
                    if color == "w":
                        bo = n.send("winner b")
                    else:
                        bo = n.send("winner w")

                if event.key == pygame.K_RIGHT:
                    bo = n.send("forward")

                if event.key == pygame.K_LEFT:
                    bo = n.send("back")


            if event.type == pygame.MOUSEBUTTONUP and color != "s":
                if color == bo.turn and bo.ready:
                    pos = pygame.mouse.get_pos()
                    bo = n.send("update moves")
                    i, j = click(pos)
                    bo = n.send("select " + str(i) + " " + str(j) + " " + color)
    
    n.disconnect()
    bo = 0
    menu_screen(win)


name = input("Please type your name: ")
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
menu_screen(win, name)
