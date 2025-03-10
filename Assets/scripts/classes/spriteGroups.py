from typing import Iterable, Union
from pygame.sprite import AbstractGroup
from Assets.scripts.settings import *



class AllSprites(pg.sprite.Group):
    
    def __init__(self):
        super(AllSprites,self).__init__()
        self.offset = vec()
        self.displaySuface = pg.display.get_surface()
        self.bg = pg.image.load(os.path.join(PATHS["other"], "bg.png")).convert()

    def customDraw(self,player):
        self.offset.x = player.rect.centerx - WIDTH/2
        self.offset.y = player.rect.centery - HEIGHT/2

        self.displaySuface.blit(self.bg,-self.offset)
        for sprite in (sorted(self.sprites(),key=lambda sprite: sprite.rect.centery)):
            offsetRect = sprite.image.get_rect(center = sprite.rect.center)
            offsetRect.center -= self.offset
            self.displaySuface.blit(sprite.image,offsetRect)