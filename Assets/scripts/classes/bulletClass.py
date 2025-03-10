from typing import Any
from Assets.scripts.settings import *
from Assets.scripts.classes.baseSprite import BaseSprite

class Bullet(BaseSprite):
    def __init__(self, pos,dir, surface, groups,owner):
        super(Bullet,self).__init__(pos, surface, groups)
        self.pos = vec(self.rect.center)
        self.drift = random.uniform(-.05,.05)
        self.dir = dir
        self.mask = pg.mask.from_surface(self.image)
        self.dir.y + self.drift
        self.speed = random.randint(550,650)
        self.dur = 75
        self.owner = owner

    def update(self,dt):
        self.pos+=self.dir*self.speed*dt 
        self.rect.center = (round(self.pos.x),round(self.pos.y))
        self.dur -= 1
        if self.dur <=0:
            self.kill()