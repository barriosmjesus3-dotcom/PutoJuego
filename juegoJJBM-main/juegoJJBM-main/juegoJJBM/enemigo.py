import pygame
import math
import random
import constantes

class Malo:
    def __init__(self, animaciones=None):
        self.flip = False
        self.vida = 100
        self.animaciones = animaciones if animaciones else []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Asignar imagen inicial
        if self.animaciones:
            self.image = self.animaciones[self.frame_index]
        else:
            self.image = pygame.Surface((25, 25))
            self.image.fill((255, 0, 0))  # Color de respaldo si no hay imágenes

        # Aparecer fuera de la pantalla
        pos_x, pos_y = self.generar_posicion_fuera()
        self.forma = pygame.Rect(0, 0, constantes.ANCHO_PERSONAJE, constantes.ALTO_PERSONAJE)
        self.forma.center = (pos_x, pos_y)

        self.velocidad = 2

    def generar_posicion_fuera(self):
        borde = random.randint(0, 3)
        margen = 50

        if borde == 0:    # Arriba
            x = random.randint(0, constantes.ANCHO_VENTANA)
            y = -margen
        elif borde == 1:  # Abajo
            x = random.randint(0, constantes.ANCHO_VENTANA)
            y = constantes.ALTO_VENTANA + margen
        elif borde == 2:  # Izquierda
            x = -margen
            y = random.randint(0, constantes.ALTO_VENTANA)
        else:             # Derecha
            x = constantes.ANCHO_VENTANA + margen
            y = random.randint(0, constantes.ALTO_VENTANA)

        return x, y

    def update(self, jugador):
        # 1. Movimiento hacia el jugador
        dx = jugador.forma.centerx - self.forma.centerx
        dy = jugador.forma.centery - self.forma.centery
        distancia = math.hypot(dx, dy)

        if distancia != 0:
            dx /= distancia
            dy /= distancia

        self.forma.x += dx * self.velocidad
        self.forma.y += dy * self.velocidad

        # 2. Orientación (voltear a la izquierda/derecha)
        self.flip = True if dx < 0 else False

        # 3. Lógica de Animación
        cooldown_animacion = 150  # Velocidad de animación en milisegundos
        if self.animaciones:
            if pygame.time.get_ticks() - self.update_time >= cooldown_animacion:
                self.frame_index = (self.frame_index + 1) % len(self.animaciones)
                self.image = self.animaciones[self.frame_index]
                self.update_time = pygame.time.get_ticks()

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        return self.vida <= 0

    def dibujar(self, interfaz):
        imagen_flip = pygame.transform.flip(self.image, self.flip, False)
        rect_visual = imagen_flip.get_rect(center=self.forma.center)
        interfaz.blit(imagen_flip, rect_visual)