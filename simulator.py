from utils import fix_scaling
from control import calculate_acceleration_kmhs
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

try:
    import pygame
    import numpy as np
except ModuleNotFoundError as e:
    print(e)
    raise SystemExit('Please run `pip install -r requirements.txt`')

width, height = 1400, 200
fps = 60

black = 0, 0, 0
red = 255, 0, 0
sky = 200, 220, 255
cable = 190, 210, 245
rail = 200, 200, 100
grass = 100, 255, 100
marker = 0, 150, 0

if __name__ == '__main__':
    fix_scaling()
    pygame.init()

    print('Click left mouse button to place new vehicle')
    print('Press [Delete] to remove nearest vehicle')
    print('Press [+] to increase or [-] to decrease the number of passengers')
    print('Press [*] to increase speed (for test purposes)')
    print('Press [P] to pause')
    print('Press [Esc] or [Q] to exit')

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('MSI Fuzzy Control')

    pygame.font.init()
    font = pygame.font.SysFont('Consolas', 16)

    host_img = pygame.image.load('host.png')
    object_img = pygame.image.load('object.png')
    pillar_img = pygame.image.load('pillar.png')

    p = 0
    x_km = 0
    v_kmh = 40
    a_kmhs = 0
    d_km = np.inf
    paused = False
    objects = set()

    clock = pygame.time.Clock()
    while True:
        dt_ms = clock.tick(fps)

        if not paused:
            dt_s = dt_ms / 1000
            d_km = np.inf
            while True:
                if not objects:
                    break
                nearest_km = min(objects)
                if nearest_km < x_km:
                    objects.remove(nearest_km)
                else:
                    d_km = nearest_km - x_km
                    break

            a_kmhs = calculate_acceleration_kmhs(v_kmh, d_km*1000, p)

            v_kmh += a_kmhs * dt_s
            if v_kmh < 0:
                v_kmh = 0  # don't go backwards
            x_km += (v_kmh / 3600) * dt_s

        km2px = lambda km: int((km - x_km) * 5000 + 200)
        px2km = lambda px: x_km + (px - 200) / 5000

        pygame.draw.rect(screen, sky, (0, 0, width, 132))
        pygame.draw.rect(screen, grass, (0, 133, width, height))

        pygame.draw.line(screen, rail, (0, 132), (width, 132), 1)
        pygame.draw.line(screen, cable, (0, 110), (width, 110), 1)
        # pygame.draw.line(screen, red, (200, 100), (200, 140), 1)

        textsurface = font.render(f'x={x_km*1000:.1f}m', True, black)
        screen.blit(textsurface, (10, 10))

        textsurface = font.render(f'v={v_kmh:.1f}km/h', True, black)
        screen.blit(textsurface, (10, 30))

        textsurface = font.render(f'a={a_kmhs:.1f}km/h/s', True, black)
        screen.blit(textsurface, (10, 50))

        textsurface = font.render(f'p={p}/100', True, black)
        screen.blit(textsurface, (140, 10))

        textsurface = font.render(f'd={d_km*1000:.3f}{"" if d_km == np.inf else "m"}', True, black)
        screen.blit(textsurface, (140, 30))

        left_km = px2km(0)
        right_km = px2km(width)
        for km in np.arange(round(left_km/0.05)*0.05, right_km, 0.05):
            textsurface = font.render(f'{abs(km)*1000:.0f}m', True, marker)
            screen.blit(textsurface, (km2px(km)-8, 150))
            screen.blit(pillar_img, (km2px(km)-8, 107))

        for obj_km in objects.copy():
            screen.blit(object_img, (km2px(obj_km), 110))

        screen.blit(host_img, (100, 110))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                objects.add(px2km(event.pos[0]))
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    raise SystemExit
                elif event.key == pygame.K_DELETE:
                    if objects:
                        objects.remove(min(objects))
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    p = min(p+5, 100)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    p = max(p-5, 0)
                elif event.key == pygame.K_KP_MULTIPLY:
                    v_kmh += 10
