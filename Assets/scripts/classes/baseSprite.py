from os import walk
from Assets.scripts.settings import *



class BaseSprite(pg.sprite.Sprite):
    def __init__(self,pos,surface,groups):
        super(BaseSprite,self).__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.hitBox = self.rect.inflate(0,-self.rect.height/3)


class invisObj(pg.sprite.Sprite):
    def __init__(self,x,y,w,h, groups,game,goto ="",fromScene="",debug:bool = False):
        super().__init__(groups)
        self.game = game
        self.rect = pg.Rect(x,y,w,h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hitBox = self.rect.inflate(-20,-20)
        self.goto = goto
        self.fromScene = fromScene

        if debug:
            self.image = pg.Surface((w, h))
            self.image.fill((0, 0, 255))  

class Entity(pg.sprite.Sprite):
    def __init__(self, pos,groups,imgPath,game,debug:bool = False,status:str = 'down_idle',scale:int = 1):
        super(Entity,self).__init__(groups)
        self.game = game
        self.scale = scale
        self.importAssets(imgPath)
        self.status = status
        self.frameIndex = 0
        self.image = self.animaions[self.status][self.frameIndex]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.debug = debug
        #movement
        self.pos = vec(self.rect.center)
        self.dir = vec()
        self.speed =  500

        # collisons
        self.hitbox = self.rect.inflate(0,-self.rect.height/2)

        #attacking
        self.attacking =False
        
        #stats
        self.maxHP = 100
        self.curHP = self.maxHP
        self.canBeOuch = True
        self.hitTime = None
        self.ouchCoolDown = 400
        self.mask = pg.mask.from_surface(self.image)
        
    
    def takeDamage(self,ammount = 10):
        if self.canBeOuch:
            self.curHP -= ammount
            self.canBeOuch = False
            self.hitTime = pg.time.get_ticks()
            # Update Health bar
    
    def ouchTimer(self):
        if not self.canBeOuch:
            curTime = pg.time.get_ticks()
            if curTime - self.hitTime > self.ouchCoolDown:
                self.canBeOuch = True

    def checkHealth(self):
        if self.curHP <=0:
            if len(self.game.enemies) ==1:
                self.game.lastEnemyPos = self.pos 
            self.die()
        

        
    def importAssets(self,path):
        self.animaions = {}
        for i,folder in enumerate(walk(path)):
            if i == 0:
                for name in folder[1]:
                    self.animaions[name] = []
            else:
                for filename in sorted(folder[2],key = lambda string: int(string.split(".")[0])):
                    path = folder[0].replace("\\","/")+"/"+filename
                    surf =pg.image.load(path).convert_alpha()
                    surf = pg.transform.scale(surf, (surf.get_width() * self.scale, surf.get_height() * self.scale))
                    key = path.split("/")[-2]
                    self.animaions[key].append(surf)
    
    
    def checkColisions(self,dir):#Colistions between player and objects
        
        for sprite in self.game.solidObjects.sprites():
            if sprite.hitBox.colliderect(self.hitbox):
                if dir == "horizontal":
                    if self.dir.x > 0:#Player is moving right
                        self.hitbox.right = sprite.hitBox.left
                    if self.dir.x < 0:#Player is moving left
                        
                        self.hitbox.left = sprite.hitBox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx

                else:
                    if self.dir.y > 0:#Player is moving down
                        self.hitbox.bottom = sprite.hitBox.top
                    elif self.dir.y <0:#Player is moving up  ########### look at the indent Level your doen ccolisions works just fine but i dont think it is posable to be moving down and up at the same time ########### 
                            self.hitbox.top = sprite.hitBox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
    

    def move(self,dt):
        #normalize direction===========================
        if self.dir.magnitude() != 0:
            self.dir.normalize()
        #==============================================

        #Horizontal Movement============================
        self.pos.x += self.dir.x * self.speed *dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        #===============================================

        #Horizontal Collisions==========================
        self.checkColisions("horizontal")
        #===============================================

        #Vertical Movement============================
        self.pos.y += self.dir.y * self.speed *dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        #===============================================

        #Vertical Collisions==========================
        self.checkColisions("vertical")

    def animate(self,dt):
        curAnitmation = self.animaions[self.status]
        self.frameIndex += 15*dt
        if self.frameIndex >= len(curAnitmation):
            self.frameIndex = 0
        self.image = curAnitmation[int(self.frameIndex)]
        self.mask = pg.mask.from_surface(self.image)
    
    def flash(self,color= white):
        if not self.canBeOuch:
            if self.sinWaveValue():
                mask = pg.mask.from_surface(self.image)
                whiteSurf = mask.to_surface()
                whiteSurf.set_colorkey(black)
                self.image = whiteSurf
            
    def sinWaveValue(self):
        value = math.sin(pg.time.get_ticks())
        if value>0:
            return True
        return False