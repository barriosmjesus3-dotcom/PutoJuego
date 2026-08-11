import pygame
import math
import constantes

class Weapon:
    def __init__(self, imagen, imagen_bala, sonido):
        self.imagen = imagen
        self.imagen_bala = imagen_bala
        self.sonido = sonido
        self.rect = self.imagen.get_rect() if self.imagen else pygame.Rect(0, 0, 10, 10)
        self.angulo = 0
        self.ultimo_disparo = pygame.time.get_ticks()

    def update(self, jugador):
        pos_mouse = pygame.mouse.get_pos()
        dx = pos_mouse[0] - jugador.forma.centerx
        dy = pos_mouse[1] - jugador.forma.centery
        # Calculamos el ángulo en radianes y grados respecto al mouse
        self.angulo = math.degrees(math.atan2(-dy, dx))
        self.rect.center = jugador.forma.center

    def disparar(self, lista_balas, cadencia_actual=None):
        tiempo_actual = pygame.time.get_ticks()
        cadencia = cadencia_actual if cadencia_actual is not None else constantes.CADENCIA_DISPARO

        if tiempo_actual - self.ultimo_disparo >= cadencia:
            self.ultimo_disparo = tiempo_actual
            if self.sonido:
                self.sonido.play()
            
            pos_mouse = pygame.mouse.get_pos()
            # Creamos la bala pasando el centro del arma y la posición del mouse
            nueva_bala = Bullet(self.rect.centerx, self.rect.centery, pos_mouse, self.imagen_bala)
            lista_balas.append(nueva_bala)

    def dibujar(self, interfaz):
        if self.imagen:
            imagen_rotada = pygame.transform.rotate(self.imagen, self.angulo)
            rect_rotado = imagen_rotada.get_rect(center=self.rect.center)
            interfaz.blit(imagen_rotada, rect_rotado)


class Bullet:
    def __init__(self, x, y, pos_destino, imagen):
        self.x = float(x)
        self.y = float(y)
        
        # 1. Calculamos la distancia y ángulo hacia el destino
        dx = pos_destino[0] - x
        dy = pos_destino[1] - y
        angulo_rad = math.atan2(dy, dx)
        self.angulo_deg = math.degrees(-angulo_rad)

        # 2. Asignamos la velocidad en X e Y basándonos en el ángulo real
        self.dx = math.cos(angulo_rad) * constantes.VELOCIDAD_BALA
        self.dy = math.sin(angulo_rad) * constantes.VELOCIDAD_BALA

        # 3. Rotamos la imagen de la bala para que apunte en la dirección del trayecto
        if imagen:
            self.imagen = pygame.transform.rotate(imagen, self.angulo_deg)
            self.rect = self.imagen.get_rect(center=(int(self.x), int(self.y)))
        else:
            self.imagen = None
            self.rect = pygame.Rect(int(self.x), int(self.y), 6, 6)

    def update(self):
        # Mover en coordenadas flotantes para máxima precisión
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (int(self.x), int(self.y))

    def fuera_de_pantalla(self):
        return (self.rect.right < 0 or self.rect.left > constantes.ANCHO_VENTANA or
                self.rect.bottom < 0 or self.rect.top > constantes.ALTO_VENTANA)

    def dibujar(self, interfaz):
        if self.imagen:
            interfaz.blit(self.imagen, self.rect)
        else:
            pygame.draw.circle(interfaz, (255, 255, 0), self.rect.center, 3)