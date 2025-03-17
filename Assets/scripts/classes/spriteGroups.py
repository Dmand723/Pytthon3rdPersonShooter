from typing import Iterable, Union
from pygame.sprite import AbstractGroup
from Assets.scripts.settings import *



class AllSprites(pg.sprite.Group):
    
    def __init__(self):
        super(AllSprites,self).__init__()
        self.offset = vec()
        self.displaySuface = pg.display.get_surface()
        self.bg = pg.image.load(os.path.join(PATHS["other"], "bg.png")).convert()

    def customDraw(self, player, spritesBelow,spritesAbove):
        self.offset.x = player.rect.centerx - WIDTH / 2
        self.offset.y = player.rect.centery - HEIGHT / 2

        self.displaySuface.blit(self.bg, -self.offset)
        for sprite in spritesBelow:
            sprite_offsetRect = sprite.image.get_rect(center=sprite.rect.center)
            sprite_offsetRect.center -= self.offset
            self.displaySuface.blit(sprite.image, sprite_offsetRect)
        
        # Draw the player 
        player_offsetRect = player.image.get_rect(center=player.rect.center)
        player_offsetRect.center -= self.offset
        self.displaySuface.blit(player.image, player_offsetRect)

         #Draw these on top of other sprites
        for sprite in spritesAbove:
            sprite_offsetRect = sprite.image.get_rect(center=sprite.rect.center)
            sprite_offsetRect.center -= self.offset
            self.displaySuface.blit(sprite.image, sprite_offsetRect)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if not sprite in spritesBelow and not sprite in spritesAbove:
                offsetRect = sprite.image.get_rect(center=sprite.rect.center)
                offsetRect.center -= self.offset
                self.displaySuface.blit(sprite.image, offsetRect)
        
    def getoffset(self):
        return self.offset
       