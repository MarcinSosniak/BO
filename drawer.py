import pygame

class Drawer:
    @staticmethod
    def draw(labirynth):
        pygame.init()

        gameDisplay = pygame.display.set_mode((640, 640))
        size = 40
        pygame.display.set_caption('ant labirynth')
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                # print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            max=1
            x=0
            y=0
            for row in labirynth.get_lab():
                for elem in row:
                    if elem is not None:
                        if elem > max:
                            max=elem

            for row in labirynth.get_lab():
                for elem in row:
                    color = (5, 25, 25) if elem is None else (int(elem/max*255), 100, 105)
                        # line.append(str(int(elem/max*9)))
                    
                    pygame.draw.rect(gameDisplay, color, pygame.Rect(x, y, size, size))
                    x += size
                
                x=0
                y += size

            pygame.display.update()
            clock.tick(60)