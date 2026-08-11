import pygame
import os
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import constantes
from personaje import Personaje
from weapon import Weapon
from enemigo import Malo

pygame.init()
pygame.font.init()
pygame.mixer.init()

ventana = pygame.display.set_mode((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
pygame.display.set_caption("Juego Pygame")

# Fuentes para la interfaz y menús
fuente_titulo = pygame.font.SysFont("Arial", 48, bold=True)
fuente_boton = pygame.font.SysFont("Arial", 28, bold=True)
fuente_hud = pygame.font.SysFont("Arial", 22, bold=True)

def escalar_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale), int(h * scale)))

# ---------------------------------------------------------
# 1. CARGA DE ASSETS
# ---------------------------------------------------------

# RUTA PARA TU IMAGEN DE FONDO
RUTA_FONDO = "assets/Menu.png"

imagen_fondo = None
if os.path.exists(RUTA_FONDO):
    try:
        imagen_fondo = pygame.image.load(RUTA_FONDO).convert()
        imagen_fondo = pygame.transform.scale(imagen_fondo, (constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA))
    except Exception as e:
        print(f"Error al cargar la imagen de fondo: {e}")

# Sprites del Jugador
animaciones_jugador = []
for i in range(7):
    try:
        img = pygame.image.load(f"assets/images/caracters/player/Player_{i}.png").convert_alpha()
        img = escalar_img(img, constantes.ESCALA_PERSONAJE)
        animaciones_jugador.append(img)
    except FileNotFoundError:
        pass

# Sprites animados del Enemigo (Goblin)
animaciones_enemigo = []
ruta_enemigos = "assets/images/malos/goblin/"

if os.path.exists(ruta_enemigos):
    archivos = sorted([f for f in os.listdir(ruta_enemigos) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    for archivo in archivos:
        try:
            img = pygame.image.load(os.path.join(ruta_enemigos, archivo)).convert_alpha()
            escala = getattr(constantes, 'ESCALA_ENEMIGO', 1.0)
            img = escalar_img(img, escala)
            animaciones_enemigo.append(img)
        except Exception as e:
            print(f"Error cargando {archivo}: {e}")

# Imagen del Arma
try:
    imagen_pistola = pygame.image.load("assets/images/arma/Pistol07.png").convert_alpha()
    imagen_pistola = escalar_img(imagen_pistola, constantes.ESCALA_ARMA)
except FileNotFoundError:
    imagen_pistola = None

# Imagen de la Bala
try:
    imagen_bala = pygame.image.load("assets/images/arma/bala1.png").convert_alpha()
    escala_b = getattr(constantes, 'ESCALA_BALA', 1.0)
    imagen_bala = escalar_img(imagen_bala, escala_b)
except FileNotFoundError:
    imagen_bala = None

# Sonido de Disparo
try:
    sonido_disparo = pygame.mixer.Sound("assets/sonidos/Piu.MP3")
    sonido_disparo.set_volume(0.4)
except FileNotFoundError:
    sonido_disparo = None

RUTA_MUSICA = "assets/sonidos/music.mp3"  # <--- Cambia "tu_musica.mp3" por la ruta de tu archivo

if os.path.exists(RUTA_MUSICA):
    try:
        pygame.mixer.music.load(RUTA_MUSICA)
        pygame.mixer.music.set_volume(0.3)  # Ajusta el volumen entre 0.0 y 1.0
        pygame.mixer.music.play(-1)          # El -1 hace que la música se repita en bucle infinito
        print("Música de fondo cargada con éxito.")
    except Exception as e:
        print(f"Error al cargar la música: {e}")


# ---------------------------------------------------------
# FUNCIONES AUXILIARES PARA MENÚS
# ---------------------------------------------------------
def dibujar_boton(superficie, texto, x, y, ancho, alto, color_base, color_hover, pos_mouse):
    rect = pygame.Rect(x, y, ancho, alto)
    col = color_hover if rect.collidepoint(pos_mouse) else color_base
    
    # Sombra del botón
    pygame.draw.rect(superficie, (0, 0, 0, 150), rect.move(3, 3), border_radius=10)
    # Botón principal
    pygame.draw.rect(superficie, col, rect, border_radius=10)
    pygame.draw.rect(superficie, (255, 255, 255), rect, width=2, border_radius=10)

    txt_surf = fuente_boton.render(texto, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=rect.center)
    superficie.blit(txt_surf, txt_rect)

    return rect


# ---------------------------------------------------------
# 2. INICIALIZACIÓN DE VARIABLES DE JUEGO
# ---------------------------------------------------------
# Estados del juego: "MENU", "JUGANDO", "GAME_OVER"
estado_juego = "MENU"

def reiniciar_partida():
    global jugador, pistola, lista_balas, lista_enemigos, puntos
    global tiempo_spawn, ultimo_spawn, item_gris_rect, tiempo_ultimo_item
    global buff_activo, tiempo_fin_buff
    global mover_arriba, mover_abajo, mover_izquierda, mover_derecha

    jugador = Personaje(400, 300, animaciones_jugador)
    pistola = Weapon(imagen_pistola, imagen_bala, sonido_disparo)
    lista_balas = []
    lista_enemigos = []

    puntos = 0
    tiempo_spawn = 2000
    ultimo_spawn = pygame.time.get_ticks()

    item_gris_rect = None
    tiempo_ultimo_item = pygame.time.get_ticks()

    buff_activo = False
    tiempo_fin_buff = 0

    mover_arriba = False
    mover_abajo = False
    mover_izquierda = False
    mover_derecha = False

# Inicializar estado base
reiniciar_partida()

tiempo_spawn_min = 400
INTERVALO_SPAWN_ITEM = 12000
DURACION_BUFF = 5000
CADENCIA_MEJORADA = constantes.CADENCIA_DISPARO / 3

reloj = pygame.time.Clock()
run = True

# ---------------------------------------------------------
# 3. BUCLE PRINCIPAL
# ---------------------------------------------------------
while run:
    reloj.tick(constantes.FPS)
    tiempo_actual = pygame.time.get_ticks()
    pos_mouse = pygame.mouse.get_pos()

    # DIBUJAR FONDO BASE
    if imagen_fondo:
        ventana.blit(imagen_fondo, (0, 0))
    else:
        ventana.fill(constantes.COLOR_BG)

    # Captura global de eventos
    eventos = pygame.event.get()
    for event in eventos:
        if event.type == pygame.QUIT:
            run = False

    # ---------------------------------------------------------
    # ESTADO: MENÚ INICIAL
    # ---------------------------------------------------------
    if estado_juego == "MENU":
        # Título
        titulo = fuente_titulo.render("SURVIVAL GAME", True, (255, 255, 255))
        ventana.blit(titulo, titulo.get_rect(center=(constantes.ANCHO_VENTANA // 2, 160)))

        # Botones
        btn_jugar = dibujar_boton(ventana, "JUGAR", constantes.ANCHO_VENTANA // 2 - 100, 280, 200, 50, (40, 160, 60), (60, 200, 80), pos_mouse)
        btn_salir = dibujar_boton(ventana, "SALIR", constantes.ANCHO_VENTANA // 2 - 100, 360, 200, 50, (180, 40, 40), (220, 60, 60), pos_mouse)

        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_jugar.collidepoint(pos_mouse):
                    reiniciar_partida()
                    estado_juego = "JUGANDO"
                elif btn_salir.collidepoint(pos_mouse):
                    run = False

    # ---------------------------------------------------------
    # ESTADO: JUGANDO
    # ---------------------------------------------------------
    elif estado_juego == "JUGANDO":
        # Captura de teclado
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT): mover_izquierda = True
                if event.key in (pygame.K_d, pygame.K_RIGHT): mover_derecha = True
                if event.key in (pygame.K_w, pygame.K_UP): mover_arriba = True
                if event.key in (pygame.K_s, pygame.K_DOWN): mover_abajo = True

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT): mover_izquierda = False
                if event.key in (pygame.K_d, pygame.K_RIGHT): mover_derecha = False
                if event.key in (pygame.K_w, pygame.K_UP): mover_arriba = False
                if event.key in (pygame.K_s, pygame.K_DOWN): mover_abajo = False

        # Spawn de Item Gris
        if item_gris_rect is None and (tiempo_actual - tiempo_ultimo_item >= INTERVALO_SPAWN_ITEM):
            tiempo_ultimo_item = tiempo_actual
            margin = 40
            x_item = random.randint(margin, constantes.ANCHO_VENTANA - margin)
            y_item = random.randint(margin, constantes.ALTO_VENTANA - margin)
            item_gris_rect = pygame.Rect(x_item, y_item, 16, 16)

        if item_gris_rect and jugador.forma.colliderect(item_gris_rect):
            item_gris_rect = None
            buff_activo = True
            tiempo_fin_buff = tiempo_actual + DURACION_BUFF

        if buff_activo and tiempo_actual >= tiempo_fin_buff:
            buff_activo = False

        # Spawns de Enemigos
        tiempo_spawn = max(tiempo_spawn_min, 2000 - (puntos * 15))
        if tiempo_actual - ultimo_spawn >= tiempo_spawn:
            ultimo_spawn = tiempo_actual
            nuevo_enemigo = Malo(animaciones_enemigo)
            lista_enemigos.append(nuevo_enemigo)

        # Movimiento del Jugador
        delta_x = 0
        delta_y = 0
        if mover_derecha: delta_x += constantes.VELOCIDAD
        if mover_izquierda: delta_x -= constantes.VELOCIDAD
        if mover_abajo: delta_y += constantes.VELOCIDAD
        if mover_arriba: delta_y -= constantes.VELOCIDAD

        jugador.movimiento(delta_x, delta_y)
        jugador.update()

        # Disparos
        cadencia_actual = CADENCIA_MEJORADA if buff_activo else constantes.CADENCIA_DISPARO
        if pygame.mouse.get_pressed()[0]:
            pistola.disparar(lista_balas, cadencia_actual)

        pistola.update(jugador)

        # Actualizar enemigos
        for enemigo in lista_enemigos:
            enemigo.update(jugador)
            if enemigo.forma.colliderect(jugador.forma):
                jugador.recibir_dano(0.5)

        # Transición a GAME OVER
        if jugador.vida <= 0:
            estado_juego = "GAME_OVER"

        # Actualizar balas
        for bala in lista_balas[:]:
            bala.update()
            if bala.fuera_de_pantalla():
                lista_balas.remove(bala)
                continue

            for enemigo in lista_enemigos[:]:
                if bala.rect.colliderect(enemigo.forma):
                    if bala in lista_balas:
                        lista_balas.remove(bala)
                    murio = enemigo.recibir_dano(50)
                    if murio:
                        lista_enemigos.remove(enemigo)
                        puntos += 10
                    break

        # Renderizado Gameplay
        if item_gris_rect:
            pygame.draw.circle(ventana, (180, 180, 180), item_gris_rect.center, 8)
            pygame.draw.circle(ventana, (255, 255, 255), item_gris_rect.center, 8, 2)

        jugador.dibujar(ventana)
        pistola.dibujar(ventana)

        for enemigo in lista_enemigos:
            enemigo.dibujar(ventana)

        for bala in lista_balas:
            bala.dibujar(ventana)

        # HUD
        texto_puntos = fuente_hud.render(f"Puntos: {puntos}", True, constantes.COLOR_TEXTO)
        ventana.blit(texto_puntos, (15, 15))

        if buff_activo:
            tiempo_restante = max(0, (tiempo_fin_buff - tiempo_actual) / 1000)
            texto_buff = fuente_hud.render(f"¡CADENCIA x3! ({tiempo_restante:.1f}s)", True, (255, 215, 0))
            ventana.blit(texto_buff, (15, 45))

    # ---------------------------------------------------------
    # ESTADO: GAME OVER
    # ---------------------------------------------------------
    elif estado_juego == "GAME_OVER":
        # Overlay oscuro semitransparente sobre el juego
        overlay = pygame.Surface((constantes.ANCHO_VENTANA, constantes.ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        ventana.blit(overlay, (0, 0))

        # Título y Puntaje
        txt_go = fuente_titulo.render("¡GAME OVER!", True, (255, 50, 50))
        ventana.blit(txt_go, txt_go.get_rect(center=(constantes.ANCHO_VENTANA // 2, 150)))

        txt_puntos = fuente_boton.render(f"Puntuación Final: {puntos}", True, (255, 255, 255))
        ventana.blit(txt_puntos, txt_puntos.get_rect(center=(constantes.ANCHO_VENTANA // 2, 220)))

        # Botones
        btn_reiniciar = dibujar_boton(ventana, "REINICIAR", constantes.ANCHO_VENTANA // 2 - 110, 300, 220, 50, (40, 120, 200), (60, 150, 240), pos_mouse)
        btn_menu = dibujar_boton(ventana, "MENÚ PRINCIPAL", constantes.ANCHO_VENTANA // 2 - 110, 370, 220, 50, (180, 40, 40), (220, 60, 60), pos_mouse)

        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_reiniciar.collidepoint(pos_mouse):
                    reiniciar_partida()
                    estado_juego = "JUGANDO"
                elif btn_menu.collidepoint(pos_mouse):
                    estado_juego = "MENU"

    pygame.display.update()

pygame.quit()
sys.exit()