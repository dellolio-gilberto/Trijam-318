import pygame
import sys
import time

# ─── Inizializzazione ─────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ─── Costanti finestra ────────────────────────────────────────────────────────
LARGHEZZA = 1920
ALTEZZA = 1080
finestra = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Land the Rocket!")

# ─── Colori e font ───────────────────────────────────────────────────────────
BIANCO     = (255, 255, 255)
NERO       = (  0,   0,   0)
ROSSO      = (255,   0,   0)
VERDE      = (  0, 255,   0)
GRIGIO     = (150, 150, 150)
font       = pygame.font.Font("Minecraft.ttf", 22)

# ─── Caricamento immagini ────────────────────────────────────────────────────
sfondo_img     = pygame.transform.scale(pygame.image.load('sfondo2.png').convert(), (LARGHEZZA, ALTEZZA))
planet_img     = pygame.transform.scale(pygame.image.load('atterraggio2.png').convert_alpha(), (1980, 1080))
fuoco_img      = pygame.transform.scale(pygame.image.load('fuoco.png').convert_alpha(), (60, 48))
vita_img       = pygame.transform.scale(pygame.image.load('vita.png').convert_alpha(), (72, 72))

# Navicelle
navicelle = [
    pygame.transform.scale(pygame.image.load('navicella3.png').convert_alpha(), (276, 228)),
    pygame.transform.scale(pygame.image.load('navicella2.png').convert_alpha(), (276, 228)),
    pygame.transform.scale(pygame.image.load('navicella1.png').convert_alpha(), (276, 228))
]

# Esplosione a 3 frame
esplosione_imgs = [
    pygame.transform.scale(pygame.image.load(f'esplosione{i}.png').convert_alpha(), (510, 360))
    for i in range(1, 4)
]

# ─── Suoni ───────────────────────────────────────────────────────────────────
suono_atterraggio = pygame.mixer.Sound('atterraggio.wav')
suono_esplosione  = pygame.mixer.Sound('esplosione.wav')
pygame.mixer.music.load('musica.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# ─── FPS ─────────────────────────────────────────────────────────────────────
clock = pygame.time.Clock()
FPS = 60

# ─── Parametri gioco ─────────────────────────────────────────────────────────
livello         = 1
carburante_max  = 50
gravità_base    = 0.2
spinta_min      = -1
vel_sicura      = 3
vite_massime    = 3
landing_offset  = 220
limite_altezza  = -350  # Limite di altezza per quando la navicella si perde

# ─── Stato dinamico ──────────────────────────────────────────────────────────
carburante       = carburante_max
altezza          = 100
velocità         = 0
gravità          = gravità_base
in_discesa       = False
atterrata        = False
esplosa          = False
pronto_next      = False
tempo_inizio     = 0
tempo_fine       = 0
punteggio        = 0
punteggio_totale = 0
vite_rimaste     = vite_massime
game_over        = False
spinta           = spinta_min
esplosione_frame = 0
esplosione_timer = 0

# ─── Funzioni ────────────────────────────────────────────────────────────────
def mostra_testo(t, x, y, c=BIANCO):
    s = font.render(t, True, c)
    finestra.blit(s, (x, y))

def mostra_testo_centrato(testo, y, colore=BIANCO):
    s = font.render(testo, True, colore)
    rect = s.get_rect(center=(LARGHEZZA // 2, y))
    finestra.blit(s, rect)

def calcola_punteggio(c_max, c_rim, t_dis):
    penalità = c_max*1 + c_rim*2 + int(t_dis)*3
    return max(0, 1000*max(1, livello/3) - penalità)

def start_level():
    global carburante, altezza, velocità, gravità, spinta
    global in_discesa, atterrata, esplosa, pronto_next
    global tempo_inizio, game_over, esplosione_frame, esplosione_timer

    if esplosa:
        pygame.mixer.music.play(-1)  # Riprende la musica quando si riavvia il livello

    carburante       = max(0, carburante_max - (1 * livello))
    altezza          = 100
    velocità         = 0
    gravità          = gravità_base
    spinta           = spinta_min*livello*0.3
    in_discesa       = False
    atterrata        = False
    esplosa          = False
    pronto_next      = False
    tempo_inizio     = 0
    game_over        = False
    esplosione_frame = 0
    esplosione_timer = 0


start_level()

# ─── Main loop ───────────────────────────────────────────────────────────────
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
                altezza = ALTEZZA - planet_img.get_height() - navicella_img.get_height()
                velocità = 0
                tempo_fine = time.time()
                atterrata = True
                c_rimasto = carburante
                t_discesa = tempo_fine - tempo_inizio
                punteggio = calcola_punteggio(carburante_max, c_rimasto, t_discesa)
                suono_atterraggio.play()
                pronto_next = True

    # ─── Fisica ───────────────────────────────────────────────────────────────
    if in_discesa and not (atterrata or esplosa):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and carburante > 0:
            velocità += spinta
            carburante -= 0.5

        velocità += gravità
        altezza += velocità

        if altezza <= limite_altezza:  # La navicella si perde se sale troppo in alto
            esplosa = True
            vite_rimaste -= 1
            suono_esplosione.play()
            pygame.mixer.music.stop()  # Ferma la musica quando la navicella esplode
            if vite_rimaste <= 0:
                game_over = True

        nx = LARGHEZZA // 2 - navicella_img.get_width() // 2
        ny = int(altezza)
        nav_rect = pygame.Rect(nx + 10, ny + 10, navicella_img.get_width() - 20, navicella_img.get_height() - 20)
        planet_rect = planet_img.get_rect(midbottom=(LARGHEZZA // 2, ALTEZZA))
        landing_line = planet_rect.bottom - landing_offset

        if nav_rect.bottom >= landing_line:
            altezza = landing_line - navicella_img.get_height()
            tempo_fine = time.time()
            if abs(velocità) <= vel_sicura:
                atterrata = True
                c_rimasto = carburante
                t_discesa = tempo_fine - tempo_inizio
                punteggio = calcola_punteggio(carburante_max, c_rimasto, t_discesa)
                punteggio_totale += punteggio
                suono_atterraggio.play()
                pronto_next = True
            else:
                esplosa = True
                vite_rimaste -= 1
                suono_esplosione.play()
                pygame.mixer.music.stop() 
                if vite_rimaste <= 0:
                    game_over = True

    # aggiorna sprite navicella
    if vite_rimaste > 0:
        navicella_img = navicelle[vite_rimaste - 1]

    # ─── Disegno ──────────────────────────────────────────────────────────────
    finestra.blit(sfondo_img, (0, 0))
    planet_rect = planet_img.get_rect(midbottom=(LARGHEZZA // 2, ALTEZZA))
    finestra.blit(planet_img, planet_rect)

    nx = LARGHEZZA // 2 - navicella_img.get_width() // 2
    ny = int(altezza)

    # disegna navicella solo se non esplosa
    if not esplosa:
        finestra.blit(navicella_img, (nx, ny))

    # disegna fuoco
    if in_discesa and pygame.key.get_pressed()[pygame.K_SPACE] and carburante > 0 and not (atterrata or esplosa):
        fx = LARGHEZZA // 2 - fuoco_img.get_width() // 2
        fy = ny + navicella_img.get_height() - 20
        finestra.blit(fuoco_img, (fx, fy))

    # Animazione esplosione (più rapida)
    if esplosa and esplosione_frame < len(esplosione_imgs):
        esplosione_timer += 1
        # velocizza animazione: cambia frame ogni 8 tick
        if esplosione_timer % 8 == 0:
            esplosione_frame += 1
        if esplosione_frame < len(esplosione_imgs):
            img = esplosione_imgs[esplosione_frame]
            ex = LARGHEZZA // 2 - img.get_width() // 2
            ey = int(altezza + navicella_img.get_height() // 2 - img.get_height() // 2)
            finestra.blit(img, (ex, ey))

    # HUD
    hud_x = 20
    hud_y = 20
    hud_w = 320
    hud_h = 100

    hud_surface = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
    hud_surface.fill((0, 0, 0, 160))
    finestra.blit(hud_surface, (hud_x, hud_y))

    linea = 0
    spazio = 36
    mostra_testo("STATUS PANEL", hud_x + 20, hud_y + linea); linea += spazio
    mostra_testo(f"Level: {livello}", hud_x + 20, hud_y + linea); linea += spazio
        
    # Mostra la scritta "Fuel" e la percentuale sopra la barra
    fuel_percent = int((carburante / carburante_max) * 100)
    mostra_testo(f"Fuel: {fuel_percent}%", hud_x + 20, hud_y + linea); linea += spazio

    # Barra carburante
    barra_larghezza = 280
    barra_altezza = 20
    barra_x = hud_x + 20
    barra_y = hud_y + linea

    # pygame.draw.rect(finestra, GRIGIO, (barra_x, barra_y, barra_larghezza, barra_altezza), border_radius=10)

    # if carburante_max > 0:
    #    riempimento = int(barra_larghezza * (carburante / carburante_max))
    #    pygame.draw.rect(finestra, VERDE, (barra_x, barra_y, riempimento, barra_altezza), border_radius=10)

    if atterrata:
        mostra_testo_centrato("Successful landing!", 300, VERDE)
        mostra_testo_centrato(f"Score: {int(punteggio)}", 350, VERDE)
        mostra_testo_centrato("Press ENTER to proceed to the next level", 420, VERDE)

    elif esplosa:
        if game_over:
            mostra_testo_centrato("GAME OVER", 250, ROSSO)
            mostra_testo_centrato(f"Total Score: {int(punteggio_totale)}", 300, ROSSO)
            mostra_testo_centrato("Press R to restart the game", 350, ROSSO)
        else:
            mostra_testo_centrato("The ship exploded!", 300, ROSSO)
            mostra_testo_centrato("Press R to retry this level", 350, ROSSO)


    elif not in_discesa:
        mostra_testo_centrato("Press SPACE to start descent", ALTEZZA // 2, BIANCO)

    pygame.display.flip()
    clock.tick(FPS)

