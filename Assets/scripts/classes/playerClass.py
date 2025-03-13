from Assets.scripts.settings import *
from Assets.scripts.classes.baseSprite import Entity


class Player(Entity):
    def __init__(self,pos,groups,imgPath,game,debug:bool = False,):
        self.normalSpeed = 350
        self.sprintSpeed = 550
        super(Player,self).__init__(pos,groups,imgPath,game,debug,speed=self.normalSpeed)

        # attack
        self.bulletDir = vec(1,0)
        self.didShoot = False

       

        self.maxAmmo = 6
        self.ammo = self.maxAmmo

        self.invetory = {}

        
        self.maxStanima = 100
        self.stanima = 100
        self.sprinting = False
        self.stanimaRegenCooldown = 70
        self.stanimaCooldownTimer = 0

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

        #Movement=========================================================================
        if not self.attacking:
            #Left and right-------------------------------------------------------------------
            if keys[pg.K_LEFT] or keys[pg.K_a]:#Moving left
               self.dir.x = -1
               self.status = "left"
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:#Moving right
                self.dir.x = 1
                self.status = "right"
            else:# Not moving left or right 
                self.dir.x = 0
            #Up and down---------------------------------------------------------------------- 
            if keys[pg.K_UP] or keys[pg.K_w]:#up
                self.dir.y = -1
                self.status = "up"
            elif keys[pg.K_DOWN] or keys[pg.K_s]:#down
               self.dir.y = 1
               self.status = "down"
            else:# Not moving up or down
                self.dir.y =0
            #Sprinting-----------------------------------------------------------------------
            if keys[pg.K_LSHIFT] and (self.dir.x !=0 or self.dir.y !=0) and self.stanima > 0:
                self.sprinting = True
            else:
                self.sprinting = False
        #================================================================================

        #Shooting========================================================================
        if keys[pg.K_SPACE] or pg.mouse.get_pressed()[0]:
            if not self.attacking and self.ammo > 0:
                self.ammo -= 1
                self.attacking = True
                self.frameIndex = 0

                self.bulletDir, dist = self.tellMeWhereMouse()
                self.faceCrosshair()
        if keys[pg.K_r]:
            self.reaload()
        #================================================================================
        
        #Misc============================================================================
       

        #================================================================================
    
    def tellMeWhereMouse(self):
        mousePos = vec(self.game.mouse.rect.center)
        playerPos = vec(self.rect.center)
        distanceToPlayer = (playerPos - mousePos).magnitude()
        if distanceToPlayer != 0:
            dir = (playerPos-mousePos).normalize()
        else:
            dir = vec()

        return -dir, distanceToPlayer
    
    def faceCrosshair(self):
        dir, dist =self.tellMeWhereMouse()
        if -0.5<dir.y<0.5:
            if dir.x <0: #Crosshair is to the left
                self.status = "left"
            elif dir.x > 0: #Crosshair is on the right 
                self.status = "right"
        else:
            if dir.y <0:#Crosshair is up
                self.status = "up"
            elif dir.y>0:#Crosshair is down 
                self.status = "down"

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
        
        #Sprinting
        if self.sprinting:
            
            self.stanima -=1
            if self.stanima > 0:
                self.stanimaCooldownTimer = self.stanimaRegenCooldown
                self.speed = self.sprintSpeed
            else: 
                self.speed = self.normalSpeed
        else:
            self.speed =self.normalSpeed
            if self.stanima < self.maxStanima and self.stanimaCooldownTimer ==0:
                self.stanima +=1
            elif self.stanimaCooldownTimer > 0:
                self.stanimaCooldownTimer -=1
            
        
        
    def die(self):
        self.game.clearGroups()
        self.kill()
        self.game.is_playing = False