from Assets.scripts.settings import *
from Assets.scripts.classes.baseSprite import Entity


class Player(Entity):
    def __init__(self,pos,groups,imgPath,game):
        super(Player,self).__init__(pos,groups,imgPath,game)

        # attack
        self.bulletDir = vec(1,0)
        self.didShoot = False
        self.speed = 250
        self.maxAmmo = 6
        self.ammo = self.maxAmmo

        #debug 
        self.godmode = False
    
    def animate(self,dt):
        super(Player,self).animate(dt)
        if int(self.frameIndex) == 2 and self.attacking:
            if not self.didShoot:
                bulletStartPos = self.rect.center + self.bulletDir*80
                self.game.spawnBullet(bulletStartPos,self.bulletDir,self)
                self.didShoot = True
        if self.attacking:
            if self.frameIndex >= len(self.animaions[self.status])-1:
                self.attacking = False
                self.didShoot = False

    def getStatus(self):
        if self.dir.x == 0 and self.dir.y == 0:
            self.status = self.status.split("_")[0]+"_idle"
        
        if self.attacking:
            self.status = self.status.split("_")[0]+"_attack"
    
    
                
    def getInputs(self):
        keys = pg.key.get_pressed()

        #movement===========================================
        if keys[pg.K_LEFT] or keys[pg.K_a]:#left
           self.dir.x = -1
           self.status = "left"
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:#right
            self.dir.x = 1
            self.status = "right"
        else:
            self.dir.x = 0
            
        if keys[pg.K_UP] or keys[pg.K_w]:#up
            self.dir.y = -1
            self.status = "up"
        elif keys[pg.K_DOWN] or keys[pg.K_s]:#down
           self.dir.y = 1
           self.status = "down"
        else:
            self.dir.y =0
        #====================================================

        #Shooting============================================
        if keys[pg.K_SPACE] or pg.mouse.get_pressed()[0]:
            if not self.attacking and self.ammo > 0:
                self.ammo -= 1
                self.attacking = True
                self.frameIndex = 0

                match self.status.split("_")[0]:
                    case "left":
                        self.bulletDir = vec(-1,0)
                    case "right":
                        self.bulletDir = vec(1,0)
                    case "up":
                        self.bulletDir = vec(0,-1)
                    case "down":
                        self.bulletDir = vec(0,1)
    
        if keys[pg.K_r]:
            self.reaload()
        #====================================================
        
        #Misc================================================
       

        #====================================================
    
    def reaload(self):
        self.ammo = self.maxAmmo

    def update(self,dt):
        self.getInputs()
        self.getStatus()
        if not self.attacking:
            self.move(dt)
        self.animate(dt)
        self.flash()
        self.ouchTimer()
        self.checkHealth()
        if self.godmode and self.curHP < self.maxHP:
            self.curHP = self.maxHP

    def die(self):
        self.game.clearGroups()
        self.kill()
        self.game.is_playing = False