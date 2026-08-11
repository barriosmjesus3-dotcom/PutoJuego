import pygame
import constantes

class Personaje:
    def __init__(self, x, y, animaciones):
        self.flip = False
        self.animaciones = animaciones
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Sistema de Vida
        self.vida_max = 100
        self.vida = 100

        if self.animaciones:
            self.image = self.animaciones[self.frame_index]
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((0, 255, 0))

        self.forma = pygame.Rect(0, 0, constantes.ANCHO_PERSONAJE, constantes.ALTO_PERSONAJE)
        self.forma.center = (x, y)

    def movimiento(self, delta_x, delta_y):
        self.forma.x += delta_x
        self.forma.y += delta_y

        # Restricción de bordes de la pantalla
        if self.forma.left < 0:
            self.forma.left = 0
        if self.forma.right > constantes.ANCHO_VENTANA:
            self.forma.right = constantes.ANCHO_VENTANA
        if self.forma.top < 0:
            self.forma.top = 0
        if self.forma.bottom > constantes.ALTO_VENTANA:
            self.forma.bottom = constantes.ALTO_VENTANA

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0

    def update(self):
        # Girar el personaje dinámicamente según la posición del ratón
        pos_raton = pygame.mouse.get_pos()
        rect_visual = self.image.get_rect(center=self.forma.center)
        if pos_raton[0] < rect_visual.centerx:
            self.flip = True
        else:
            self.flip = False

        # Animación del jugador
        cooldown_animacion = 200
        if self.animaciones:
            if pygame.time.get_ticks() - self.update_time >= cooldown_animacion:
                self.frame_index = (self.frame_index + 1) % len(self.animaciones)
                self.image = self.animaciones[self.frame_index]
                self.update_time = pygame.time.get_ticks()

    def dibujar(self, interfaz):
        imagen_flip = pygame.transform.flip(self.image, self.flip, False)
        rect_visual = imagen_flip.get_rect(center=self.forma.center)
        interfaz.blit(imagen_flip, rect_visual)

        # Barra de Vida sobre el personaje
        ancho_barra = 40
        alto_barra = 6
        porcentaje = self.vida / self.vida_max

        x_barra = rect_visual.centerx - (ancho_barra // 2)
        y_barra = rect_visual.top - 10

        pygame.draw.rect(interfaz, constantes.COLOR_VIDA_VACIA, (x_barra, y_barra, ancho_barra, alto_barra))
        pygame.draw.rect(interfaz, constantes.COLOR_VIDA_LLENA, (x_barra, y_barra, int(ancho_barra * porcentaje), alto_barra))
        pygame.draw.rect(interfaz, (255, 255, 255), (x_barra, y_barra, ancho_barra, alto_barra), 1)