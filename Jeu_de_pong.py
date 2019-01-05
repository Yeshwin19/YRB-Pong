import pygame
import pygame.midi
import sys
from time import sleep
import random
import math

#CONSTANTS POUR LA FENETRE, LE JEU, LES RAQUETTES, LA BALLE, LE TYPE DE DIFFICULTEs ET LE DEROULEMENT DU JEU.
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_COLOR = (255, 228, 196)
BACKGROUND_COLOR = (184, 134, 11)
PAD_WIDTH = 16
PAD_HEIGHT = 64
PAD_SPEED = 8
BALL_SIZE = 16
BALL_SPEED = 8
FIRST_PLAYER = 0
SECOND_PLAYER = 1
AI_EASY = 0
AI_HARD = 1
SCORE_SIZE = 128
INITIAL_SCORE = 0
MAX_SCORE = 10
SCORE_SPACING = 64
MIDDLE_LINE_WIDTH = 4
MIDDLE_LINE_HEIGHT = 16


#CONSTANTS POUR LES JOUEURS.
MAIN_MENU = 0
SINGLE_PLAYER = 1
MULTIPLAYER = 2
DIFFICULTY = 3

#CONSTANTS POUR LES MENUS.
TITLE_FONT_SIZE = 64
MENU_FONT_SIZE = 32
NOM_FONT_SIZE = 12
MENU_SELECTOR_SIZE = 8
MENU_OPTION_SINGLE_PLAYER = 0
MENU_OPTION_MULTIPLAYER = 1
MENU_OPTION_EXIT = 2
MENU_OPTION_AI_EASY = 3
MENU_OPTION_AI_HARD = 4

#LA MUSIQUE POUR LES JOUEURS ET QUAND LES JOUEURS OBTIENNENT DES POINTS.
SOUND_FIRST_PLAYER = 0
SOUND_SECOND_PLAYER = 1
SOUND_HUMAN_SCORES = 2
SOUND_AI_SCORES = 3

#LES STYLES POUR LE MENU.

pygame.init ()

#APPLIQUER UN STYLE POUR LE SCORE.
score_font = pygame.font.SysFont ("verdana", SCORE_SIZE, True)

#APPLIQUER UN STYLE POUR LE TITLE.
title_font = pygame.font.SysFont ("verdana", TITLE_FONT_SIZE, True)

#APPLIQUER UN STYLE POUR LE MENU.
menu_font = pygame.font.SysFont ("verdana", MENU_FONT_SIZE, True)

#APPLIQUER UN STYLE POUR LE NOM.
nom_font = pygame.font.SysFont ("verdana", NOM_FONT_SIZE, True)

#CREER ET AJUSTER L'HAUTEUR ET LA LARGEUR DE LA FENETRE.
screen = pygame.display.set_mode ((WINDOW_WIDTH, WINDOW_HEIGHT))

#APPLIQUER LES SONS.
pygame.midi.init ()
midi_out = pygame.midi.Output (0)
midi_out.set_instrument (80)
running = True
clock = pygame.time.Clock ()

#DEFINIR LA VITESSE DU JEU.
FPS = 60


#LES LUTINS DU JEU.


#CREATION DES RAQUETTES.
class Pad:

    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.w = PAD_WIDTH
        self.h = PAD_HEIGHT
        self.up = False
        self.down = False
        self.player = player
        self.surface = pygame.Surface ((PAD_WIDTH, PAD_HEIGHT))

    def draw(self):
        pygame.draw.rect (screen, GAME_COLOR, pygame.Rect (self.x, self.y, self.w, self.h))

#CREATION DE LA BALLE.
class Ball:

    def __init__(self, x, y):
        self.x = x
        self.y = y

#LANCER UNE PIECE POUR DECIDER SI LA BALLE PARTIRA A DROITE OU A GAUCHE QUAND ON LANCE LA PARTIE.
        self.direction = (lambda: 180 if random.randint (-1, 1) else 360) ()
        self.speed = BALL_SPEED
        self.w = BALL_SIZE
        self.h = BALL_SIZE

#DEFINIR LA POSITION DE LA BALLE SUR LA FENETRE APRES LA BALLE A DEPASSER LES FRONTIERES.
    def reset(self):
        self.x = (WINDOW_WIDTH / 2) - (BALL_SIZE / 2)
        self.y = (WINDOW_HEIGHT / 2) - (BALL_SIZE / 2)
        self.direction = (lambda: 180 if random.randint (-1, 1) else 360) ()
        self.speed = BALL_SPEED

    def bounce(self, diff):
        self.direction = (180 - self.direction) % 360
        self.direction -= diff
        self.speed *= 1.1

    def draw(self):
        pygame.draw.rect (screen, GAME_COLOR, pygame.Rect (self.x, self.y, self.w, self.h))

#CREATIONS DES SCORES.
#MAINTENANCE DES SCORES.
#DEFINIR LA TAILLE.
class Score:

    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.w = SCORE_SIZE
        self.h = SCORE_SIZE
        self.value = INITIAL_SCORE
        self.player = player
        self.surface = pygame.Surface ((SCORE_SIZE, SCORE_SIZE))

    def draw(self):
        screen.blit (score_font.render (str (self.value), 1, GAME_COLOR, (self.w, self.h)), (self.x, self.y))

#DEFINIR LA TAILLE DES ECRITURES DANS LE MENU/ LA FENETRE
class MenuSelector:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = MENU_SELECTOR_SIZE * 4
        self.h = MENU_SELECTOR_SIZE

    def draw(self):
        pygame.draw.rect (screen, GAME_COLOR, pygame.Rect (self.x, self.y, self.w, self.h))

#LE JEU
#DEFINIR OU SE PLACERA LA BALLE.
#DEFINIR OU SE PLACERA LES RAQUETTES.
#DEFINIR LE NIVEAU DE DIFFICULTE DE L'INTELLIGENCE ARTIFICIELLE.
class Game:

    def __init__(self):
        self.reset_game ()

    def reset_game(self):
        self.player1 = Pad (PAD_WIDTH, (WINDOW_HEIGHT / 2) - (PAD_HEIGHT / 2), FIRST_PLAYER)
        self.player2 = Pad (WINDOW_WIDTH - (PAD_WIDTH * 2), (WINDOW_HEIGHT / 2) - (PAD_HEIGHT / 2), SECOND_PLAYER)
        self.ball = Ball ((WINDOW_WIDTH / 2) - (BALL_SIZE / 2), (WINDOW_HEIGHT / 2) - (BALL_SIZE / 2))
        self.score1 = Score (((WINDOW_WIDTH / 2) - (SCORE_SIZE / 2.8) - SCORE_SPACING * 2), SCORE_SPACING, 1)
        self.score2 = Score (((WINDOW_WIDTH / 2) - (SCORE_SIZE / 2.8) + SCORE_SPACING * 2), SCORE_SPACING, 2)
        self.current_screen = MAIN_MENU
        self.menu_option = MENU_OPTION_SINGLE_PLAYER
        self.difficulty_menu_option = MENU_OPTION_AI_EASY
        self.menu_selector = MenuSelector ((((WINDOW_WIDTH / 2) - ((MENU_FONT_SIZE / 2) * 6)) - (MENU_SELECTOR_SIZE * 8)), MENU_FONT_SIZE * 8.5)
        self.ai_difficulty = AI_EASY


#DETECTION DES COLLISIONS.
    def check_collision(self, a, b):
        h_overlaps = True
        v_overlaps = True
        if (a.x > (b.x + b.w)) or ((a.x + a.w) < b.x):
            h_overlaps = False
        if (a.y > (b.y + b.h)) or ((a.y + a.h) < b.y):
            v_overlaps = False
        return h_overlaps and v_overlaps

#CREATION DE LA LIGNE AU MILLIEU DE LA FENETRE OU LA BALLE S'APPARAITRA QUAND ON LANCERA LE JEU.
    def draw_middle_line(self):
        for n in range (0, WINDOW_HEIGHT, 38):
            pygame.draw.rect (screen, GAME_COLOR, pygame.Rect ((WINDOW_WIDTH / 2) - (MIDDLE_LINE_WIDTH / 2), n, MIDDLE_LINE_WIDTH, MIDDLE_LINE_HEIGHT))

#DEFINIR LA MUSIQUE QUAND LA BALLE TOUCHE LES RAQUETTES.
#DEFINIR LA MUSIQUE QUAND LA BALLE TOUCHE LA ZONE DE BUT.
    def play_sound(self, sound):
        velocity = 70
        if sound == SOUND_FIRST_PLAYER:
            midi_out.note_on (90, velocity)
            sleep (0.02)
            midi_out.note_off (90, velocity)
        elif sound == SOUND_SECOND_PLAYER:
            midi_out.note_on (96, velocity)
            sleep (0.02)
            midi_out.note_off (96, velocity)
        elif sound == SOUND_HUMAN_SCORES:
            midi_out.note_on (90, velocity)
            midi_out.note_on (93, velocity)
            sleep (0.5)
            midi_out.note_off (90, velocity)
            midi_out.note_off (93, velocity)
        elif sound == SOUND_AI_SCORES:
            midi_out.note_on (30, velocity)
            midi_out.note_on (31, velocity)
            sleep (0.5)
            midi_out.note_off (30, velocity)
            midi_out.note_off (31, velocity)


if __name__ == "__main__":
    game = Game ()


#INITIALISER LES BOUTONS.
#INITIALISER LES ECRITURES CLIQUABLES.
#CREATION DES STAGES DU JEU COMME PAR EXEMPLE DEBUTANT OU EXPERT.
#LES FLECHES EN HAUT ET EN BAS SONT UTILISES POUR DIRIGER LA RAQUETTE A GAUCHE EN MODE JOUEUR SIMPLE.
#LES FLECHES W ET S SONT UTILISES POUR DIRIGER LA RAQUETTE A GAUCHE ET LES FLECHES HAUT ET BAS SONT UTILISER POUR DIRIGER LA RAQUETTES A DROITE EN MODE MULTIJOUEUR.


    def handle_events():
        for e in pygame.event.get ():
            if e.type == pygame.QUIT:
                sys.exit ()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    game.current_screen = MAIN_MENU
                    game.reset_game ()
                if game.current_screen == MAIN_MENU:
                    if e.key == pygame.K_w or e.key == pygame.K_UP:
                        if game.menu_option > MENU_OPTION_SINGLE_PLAYER:
                            game.menu_selector.y -= MENU_FONT_SIZE * 1.5
                            game.menu_option -= 1
                    elif e.key == pygame.K_s or e.key == pygame.K_DOWN:
                        if game.menu_option < MENU_OPTION_EXIT:
                            game.menu_selector.y += MENU_FONT_SIZE * 1.5
                            game.menu_option += 1
                    elif e.key == pygame.K_RETURN:
                        if game.menu_option == MENU_OPTION_SINGLE_PLAYER:
                            game.current_screen = DIFFICULTY
                        elif game.menu_option == MENU_OPTION_MULTIPLAYER:
                            game.current_screen = MULTIPLAYER
                        elif game.menu_option == MENU_OPTION_EXIT:
                            sys.exit ()
                elif game.current_screen == DIFFICULTY:
                    if e.key == pygame.K_w or e.key == pygame.K_UP:
                        if game.difficulty_menu_option > MENU_OPTION_AI_EASY:
                            game.menu_selector.y -= MENU_FONT_SIZE * 1.5
                            game.difficulty_menu_option -= 1
                    elif e.key == pygame.K_s or e.key == pygame.K_DOWN:
                        if game.difficulty_menu_option < MENU_OPTION_AI_HARD:
                            game.menu_selector.y += MENU_FONT_SIZE * 1.5
                            game.difficulty_menu_option += 1
                    elif e.key == pygame.K_RETURN:
                        if game.difficulty_menu_option == MENU_OPTION_AI_EASY:
                            game.ai_difficulty = AI_EASY
                        elif game.difficulty_menu_option == MENU_OPTION_AI_HARD:
                            game.ai_difficulty = AI_HARD
                        game.current_screen = SINGLE_PLAYER
                    if e.key == pygame.K_ESCAPE:
                        game.current_screen = MAIN_MENU
                elif game.current_screen == SINGLE_PLAYER:
                    if e.key == pygame.K_UP:
                        game.player1.up = True
                        game.player1.down = False
                    elif e.key == pygame.K_DOWN:
                        game.player1.up = False
                        game.player1.down = True
                elif game.current_screen == MULTIPLAYER:
                    if e.key == pygame.K_w:
                        game.player1.up = True
                        game.player1.down = False
                    elif e.key == pygame.K_s:
                        game.player1.up = False
                        game.player1.down = True
                    elif e.key == pygame.K_UP:
                        game.player2.up = True
                        game.player2.down = False
                    elif e.key == pygame.K_DOWN:
                        game.player2.up = False
                        game.player2.down = True


#RE CREER LES LUTINS QUAND LE SCORE EST EGALE A ZERO.
    def redraw():
        pygame.display.flip ()
        screen.fill (BACKGROUND_COLOR)


#CREER ET DIRIGER L'INTELLIGENCE ATIFICIELLE.
        if game.current_screen == SINGLE_PLAYER:
            if game.ai_difficulty == AI_EASY:
                center = (game.player2.h / 2) - (game.ball.h / 2)
                chance = random.randint (0, 2)
                if game.ball.y >= (game.player2.y + (
                    lambda: center if not chance == 1 else random.randint (center, WINDOW_HEIGHT - PAD_HEIGHT)) ()):
                    game.player2.up = False
                    game.player2.down = True
                elif game.ball.y <= (game.player2.y + (
                lambda: center if not chance == 1 else random.randint (center, WINDOW_HEIGHT - PAD_HEIGHT)) ()):
                    game.player2.up = True
                    game.player2.down = False
            elif game.ai_difficulty == AI_HARD:
                if game.ball.y >= (game.player2.y + (game.player2.h / 2) - (game.ball.h / 2)):
                    game.player2.up = False
                    game.player2.down = True
                elif game.ball.y <= (game.player2.y + (game.player2.h / 2) - (game.ball.h / 2)):
                    game.player2.up = True
                    game.player2.down = False

        if game.current_screen == SINGLE_PLAYER or game.current_screen == MULTIPLAYER:
            game.draw_middle_line ()
            game.player1.draw ()
            game.player2.draw ()
            game.score1.draw ()
            game.score2.draw ()
            game.ball.draw ()

#RECOMMENCER LE JEU.
            if game.ball.x < 0:
                game.score2.value += 1
                game.play_sound (SOUND_AI_SCORES)
                game.ball.reset ()
            elif game.ball.x > WINDOW_WIDTH:
                game.score1.value += 1
                game.play_sound (SOUND_HUMAN_SCORES)
                game.ball.reset ()
            if game.score1.value == MAX_SCORE or game.score2.value == MAX_SCORE:
                game.score1.value = INITIAL_SCORE
                game.score2.value = INITIAL_SCORE
                game.ball.reset


#CREATION DES LIMITES POUR LES RAQUETTES.
            if game.player1.up and game.player1.y > 0:
                game.player1.y -= PAD_SPEED
            elif game.player1.down and (game.player1.y + game.player1.h) < WINDOW_HEIGHT:
                game.player1.y += PAD_SPEED
            if game.player2.up and game.player2.y > 0:
                game.player2.y -= PAD_SPEED
            elif game.player2.down and (game.player2.y + game.player2.h) < WINDOW_HEIGHT:
                game.player2.y += PAD_SPEED


#REBONDISSEMENT DE LA BALLE QUAND ELLE TOUCHE LA RAQUETTE ET LES FRONTIERES.
            game.direction_radians = math.radians (game.ball.direction)
            game.ball.x += game.ball.speed * math.cos (game.direction_radians)
            game.ball.y -= game.ball.speed * math.sin (game.direction_radians)

            if game.ball.y <= 0:
                game.ball.direction = (360 - game.ball.direction) % 360
            elif game.ball.y > WINDOW_HEIGHT - game.ball.w:
                game.ball.direction = (360 - game.ball.direction) % 360
            if game.check_collision (game.player1, game.ball):
                game.ball.diff = ((game.player1.y + game.player1.h) / 2) - ((game.ball.y + game.ball.h) / 2)
                game.ball.bounce (game.ball.diff)
                game.play_sound (SOUND_FIRST_PLAYER)
            elif game.check_collision (game.player2, game.ball):
                game.ball.diff = ((game.player2.y + game.player2.h) / 2) - ((game.ball.y + game.ball.h) / 2)
                game.ball.bounce (game.ball.diff)
                game.play_sound (SOUND_SECOND_PLAYER)

        elif game.current_screen == MAIN_MENU:
            game.menu_selector.draw ()
            screen.blit (title_font.render ("Pong", 1, GAME_COLOR, (TITLE_FONT_SIZE, TITLE_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((TITLE_FONT_SIZE / 2) * 8), MENU_FONT_SIZE))
            screen.blit (menu_font.render ("Joueur Unique", 1, GAME_COLOR, (MENU_FONT_SIZE, MENU_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((MENU_FONT_SIZE / 2) * 6), MENU_FONT_SIZE * 8))
            screen.blit (menu_font.render ("Multi-joueur", 1, GAME_COLOR, (MENU_FONT_SIZE, MENU_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((MENU_FONT_SIZE / 2) * 6), MENU_FONT_SIZE * 9.5))
            screen.blit (menu_font.render ("Quitter", 1, GAME_COLOR, (MENU_FONT_SIZE, MENU_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((MENU_FONT_SIZE / 2) * 6), MENU_FONT_SIZE * 11))
            screen.blit (nom_font.render ("BANGARIGADU YESHWIN RAJ", 1, GAME_COLOR,
                                             (NOM_FONT_SIZE, NOM_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((NOM_FONT_SIZE / 2) * 13.8), NOM_FONT_SIZE * 9.5))
        elif game.current_screen == DIFFICULTY:
            game.menu_selector.draw ()
            screen.blit (title_font.render ("Difficulté", 1, GAME_COLOR, (TITLE_FONT_SIZE, TITLE_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((TITLE_FONT_SIZE / 2) * 5), MENU_FONT_SIZE))
            screen.blit (menu_font.render ("Débutant", 1, GAME_COLOR, (MENU_FONT_SIZE, MENU_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((MENU_FONT_SIZE / 2) * 6), MENU_FONT_SIZE * 8))
            screen.blit (menu_font.render ("Expert", 1, GAME_COLOR, (MENU_FONT_SIZE, MENU_FONT_SIZE)),
                         ((WINDOW_WIDTH / 2) - ((MENU_FONT_SIZE / 2) * 6), MENU_FONT_SIZE * 9.5))



#L'EXECUTION.
    while (running):
        clock.tick (FPS)
        redraw ()
        handle_events ()