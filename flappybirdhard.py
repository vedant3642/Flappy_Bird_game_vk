import random
import sys
import pygame
from pygame.locals import *

# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = int(SCREENHEIGHT * 0.8)
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'bird.png'
BACKGROUND_DAY = 'background.png'
BACKGROUND_NIGHT = 'night_background.png'
PIPE = 'pipe.png'

def safe_play(sound_key):
    if sound_key in GAME_SOUNDS:
        try:
            GAME_SOUNDS[sound_key].play()
        except:
            pass

def welcomeScreen():
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
        SCREEN.blit(GAME_SPRITES['background_day'], (0, 0))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)  # Fixed from SCREENWIDTH to SCREENHEIGHT
    basex = 0

    newPipe1 = getRandomPipe(score)
    newPipe2 = getRandomPipe(score)

    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    playerVelY = -9
    playerMaxVelY = 10
    playerFlapAccv = -8
    playerFlapped = False

    is_day = True
    fade_progress = 0
    fade_speed = 0.02
    transitioning = False

    while True:
        # Adjust pipe velocity and gravity with score but keep reasonable limits
        pipeVelX = -4 - (score // 10)
        gravity = 1 + (score // 20) * 0.2
        flapPower = playerFlapAccv + (score // 15) * 0.5

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = flapPower
                    playerFlapped = True
                    safe_play('wing')

        if isCollide(playerx, playery, upperPipes, lowerPipes):
            showGameOver()
            return

        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2

        # Scoring logic
        for i in range(len(upperPipes)):
            pipe = upperPipes[i]
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2

            if 'scored' not in pipe and playerMidPos > pipeMidPos:
                score += 1
                upperPipes[i]['scored'] = True
                safe_play('point')

                if score % 10 == 0:
                    is_day = not is_day
                    transitioning = True
                    fade_progress = 0

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += gravity

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # Move pipes to left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add new pipe only when the rightmost pipe is past a threshold to keep spacing constant
        # Instead of checking first pipe x near 0, check the last pipe's x to add new pipe
        last_pipe_x = upperPipes[-1]['x']
        pipe_gap = SCREENWIDTH / 2  # Constant horizontal gap between pipes

        if last_pipe_x < SCREENWIDTH - pipe_gap:
            newpipe = getRandomPipe(score)
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # Remove pipes that have gone off screen
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Handle day/night background fade
        if transitioning:
            fade_progress += fade_speed
            if fade_progress >= 1:
                fade_progress = 1
                transitioning = False

            from_bg = GAME_SPRITES['background_day'] if not is_day else GAME_SPRITES['background_night']
            to_bg = GAME_SPRITES['background_night'] if not is_day else GAME_SPRITES['background_day']

            SCREEN.blit(from_bg, (0, 0))
            overlay = to_bg.copy()
            overlay.set_alpha(int(fade_progress * 255))
            SCREEN.blit(overlay, (0, 0))
        else:
            background = GAME_SPRITES['background_day'] if is_day else GAME_SPRITES['background_night']
            SCREEN.blit(background, (0, 0))

        # Draw pipes
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        # Draw score
        myDigits = [int(x) for x in list(str(score))]
        width = sum(GAME_SPRITES['numbers'][digit].get_width() for digit in myDigits)
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showGameOver():
    SCREEN.blit(GAME_SPRITES['gameover'],
                ((SCREENWIDTH - GAME_SPRITES['gameover'].get_width()) // 2, int(SCREENHEIGHT * 0.25)))
    pygame.display.update()
    pygame.time.delay(1500)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        safe_play('hit')
        return True

    playerWidth = GAME_SPRITES['player'].get_width()
    playerHeight = GAME_SPRITES['player'].get_height()

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        pipeWidth = GAME_SPRITES['pipe'][0].get_width()
        if (playery < pipeHeight + pipe['y'] and
                playerx + playerWidth > pipe['x'] and playerx < pipe['x'] + pipeWidth):
            safe_play('hit')
            return True

    for pipe in lowerPipes:
        pipeWidth = GAME_SPRITES['pipe'][0].get_width()
        if (playery + playerHeight > pipe['y'] and
                playerx + playerWidth > pipe['x'] and playerx < pipe['x'] + pipeWidth):
            safe_play('hit')
            return True

    return False

def getRandomPipe(score=0):
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    baseHeight = GAME_SPRITES['base'].get_height()
    
    # Avoid too small offset to prevent pipe overlapping or crashes
    # Clamp offset between min and max values
    min_offset = 80
    max_offset = 150
    calculated_offset = SCREENHEIGHT / (3 + score // 20)
    offset = max(min(calculated_offset, max_offset), min_offset)
    
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - baseHeight - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    return [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]

if __name__ == "__main__":
    try:
        pygame.mixer.init()
    except:
        print("Warning: Audio device not found. Running without sound.")

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by Vedant Kadam')

    GAME_SPRITES['numbers'] = tuple(
        pygame.image.load(f'{i}.png').convert_alpha() for i in range(10)
    )

    GAME_SPRITES['message'] = pygame.image.load('message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )
    GAME_SPRITES['background_day'] = pygame.image.load(BACKGROUND_DAY).convert()
    GAME_SPRITES['background_night'] = pygame.image.load(BACKGROUND_NIGHT).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    GAME_SPRITES['gameover'] = pygame.image.load('gameover.png').convert_alpha()

    if pygame.mixer.get_init():
        GAME_SOUNDS['die'] = pygame.mixer.Sound('die.wav')
        GAME_SOUNDS['hit'] = pygame.mixer.Sound('hit.wav')
        GAME_SOUNDS['point'] = pygame.mixer.Sound('point.wav')
        GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('swoosh.wav')
        GAME_SOUNDS['wing'] = pygame.mixer.Sound('wing.wav')

    while True:
        welcomeScreen()
        mainGame()
