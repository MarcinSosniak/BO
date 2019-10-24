import pygame

class Drawer:
    @staticmethod
    def draw(labirynth,cfg):
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
            target_x=0
            target_y=0
            for row in labirynth.get_lab():
                for elem in row:
                    color = (0,0,0)
                    if cfg.get_instance().anthill_pos.x() == target_x and cfg.get_instance().anthill_pos.y() == target_y:
                        color= (150,75,0)
                    elif cfg.get_instance().target_pos.x() == target_x and cfg.get_instance().target_pos.y() == target_y:
                        color = (0,255,0)
                    else:
                        color = (5, 25, 25) if elem is None else ((128,100,105) if elem *2 < max and elem> 0.01*max else (int(elem/max*255), 100, 105))
                        # line.append(str(int(elem/max*9)))
                    
                    pygame.draw.rect(gameDisplay, color, pygame.Rect(x, y, size, size))
                    x += size
                    target_x+=1
                x=0
                y += size
                target_y+=1
                target_x=0

            pygame.display.update()
            clock.tick(60)
