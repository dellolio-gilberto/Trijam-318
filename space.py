import pygame
import sys
import time

# ─── Inizializzazione ───
pygame.init()
pygame.mixer.init()

# ─── Costanti finestra ───
LARGHEZZA = 1920
ALTEZZA = 1080
finestra = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Atterra la Navicella!")

# ─── Colori e font ───
BIANCO     = (255, 255, 255)
NERO       = (  0,   0,   0)
ROSSO      = (255,   0,   0)
VERDE      = (  0, 255,   0)
GRIGIO     = (150, 150, 150)
font       = pygame.font.SysFont("consolas", 28)

# ─── Caricamento immagini ───
sfondo_img     = pygame.transform.scale(pygame.image.load('sfondo.png').convert(), (LARGHEZZA, ALTEZZA))
navicella_img  = pygame.transform.scale(pygame.image.load('navicella.png').convert_alpha(), (60, 60))
planet_img     = pygame.transform.scale(pygame.image.load('atterraggio2.png').convert_alpha(), (400, 120))
fuoco_img      = pygame.transform.scale(pygame.image.load('fuoco.png').convert_alpha(), (32, 32))
vita_img       = pygame.transform.scale(pygame.image.load('vita.png').convert_alpha(), (32, 32))

# ─── Suoni ───
suono_atterraggio = pygame.mixer.Sound('atterraggio.mp3')
suono_esplosione  = pygame.mixer.Sound('esplosione.mp3')
pygame.mixer.music.load('musica.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# ─── FPS ───
clock = pygame.time.Clock()
FPS = 60

# ─── Parametri gioco ───
livello         = 1
carburante_max  = 50
gravità_base    = 0.3
spinta          = -0.6
vel_sicura      = 2.2
vite_massime    = 3

# ─── Stato dinamico ───
carburante     = carburante_max
altezza        = 100
velocità       = 0
gravità        = gravità_base
in_discesa     = False
atterrata      = False
esplosa        = False
pronto_next    = False
tempo_inizio   = 0
tempo_fine     = 0
punteggio      = 0
vite_rimaste   = vite_massime
game_over      = False

# ─── Funzioni ───
def mostra_testo(t, x, y, c=BIANCO):
    s = font.render(t, True, c)
    finestra.blit(s, (x, y))

def mostra_testo_centrato(testo, y, colore=BIANCO):
    s = font.render(testo, True, colore)
    rect = s.get_rect(center=(LARGHEZZA // 2, y))
    finestra.blit(s, rect)

def calcola_punteggio(c_max, c_rim, t_dis):
    penalità = c_max*1 + c_rim*2 + int(t_dis)*3
    return max(0, 1000 - penalità)

def start_level():
    global carburante, altezza, velocità, gravità
    global in_discesa, atterrata, esplosa, pronto_next, tempo_inizio, game_over

    carburante   = (carburante_max - (1 * livello))
    altezza      = 100
    velocità     = 0
    gravità      = max(0.00, gravità_base - (livello - 1) * 0.02)
    in_discesa   = False
    atterrata    = False
    esplosa      = False
    pronto_next  = False
    tempo_inizio = 0
    game_over    = False

start_level()

# ─── Main loop ───
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE and not in_discesa and not esplosa and not game_over:
                in_discesa   = True
                tempo_inizio = time.time()

            if e.key == pygame.K_r and esplosa:
                if game_over:
                    livello = 1
                    vite_rimaste = vite_massime
                start_level()

            if e.key == pygame.K_RETURN and pronto_next:
                livello += 1
                start_level()

            if e.key == pygame.K_v and in_discesa and not (atterrata or esplosa):
                altezza = ALTEZZA - planet_img.get_height() - 60
                velocità = 0
                tempo_fine = time.time()
                atterrata = True
                c_rimasto = carburante
                t_discesa = tempo_fine - tempo_inizio
                punteggio = calcola_punteggio(carburante_max, c_rimasto, t_discesa)
                suono_atterraggio.play()
                pronto_next = True

    if in_discesa and not (atterrata or esplosa):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and carburante > 0:
            velocità += spinta
            carburante -= 0.5

        velocità += gravità
        altezza += velocità

        if altezza + navicella_img.get_height() >= ALTEZZA - planet_img.get_height():
            altezza = ALTEZZA - planet_img.get_height() - navicella_img.get_height()
            tempo_fine = time.time()

            if abs(velocità) <= vel_sicura:
                atterrata = True
                c_rimasto = carburante
                t_discesa = tempo_fine - tempo_inizio
                punteggio = calcola_punteggio(carburante_max, c_rimasto, t_discesa)
                suono_atterraggio.play()
                pronto_next = True
            else:
                esplosa = True
                vite_rimaste -= 1
                suono_esplosione.play()
                if vite_rimaste <= 0:
                    game_over = True

    finestra.blit(sfondo_img, (0, 0))

    planet_rect = planet_img.get_rect(midbottom=(LARGHEZZA // 2, ALTEZZA))
    finestra.blit(planet_img, planet_rect)

    nx = LARGHEZZA // 2 - navicella_img.get_width() // 2
    ny = int(altezza)
    finestra.blit(navicella_img, (nx, ny))

    if in_discesa and pygame.key.get_pressed()[pygame.K_SPACE] and carburante > 0 and not (atterrata or esplosa):
        fx = LARGHEZZA // 2 - fuoco_img.get_width() // 2
        fy = ny + navicella_img.get_height() - 8
        finestra.blit(fuoco_img, (fx, fy))

    mostra_testo(f"Livello: {livello}", 20, 20)
    mostra_testo(f"Velocità: {velocità:.2f}", 20, 60)
    mostra_testo(f"Carburante: {int(carburante)}", 20, 90)
    mostra_testo(f"Gravità: {gravità:.2f}", 20, 120)

    pygame.draw.rect(finestra, GRIGIO, (20, 160, 200, 20), border_radius=5)
    if carburante_max > 0:
        w = int(200 * (carburante / carburante_max))
        pygame.draw.rect(finestra, VERDE, (20, 160, w, 20), border_radius=5)

    for i in range(vite_rimaste):
        x = LARGHEZZA - (i + 1) * 40 - 10
        finestra.blit(vita_img, (x, 20))

    if atterrata:
        mostra_testo_centrato(f"✅ Atterraggio! Punteggio: {punteggio}", 300, VERDE)
        mostra_testo_centrato("Premi INVIO per il livello successivo", 340, VERDE)
    elif esplosa:
        mostra_testo_centrato("💥 Hai esploso la navicella!", 300, ROSSO)
        mostra_testo_centrato("Premi R per riprovare", 340, ROSSO)
        if game_over:
            mostra_testo_centrato("❌ GAME OVER", 400, ROSSO)
            mostra_testo_centrato("Premi R per ricominciare", 440, ROSSO)
    elif not in_discesa:
        mostra_testo_centrato("Premi SPAZIO per iniziare", ALTEZZA // 2, BIANCO)

    pygame.display.flip()
    clock.tick(FPS)

