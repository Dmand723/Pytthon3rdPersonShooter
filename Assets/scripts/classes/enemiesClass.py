from Assets.scripts.settings import *
from Assets.scripts.classes.baseSprite import Entity

class BadBoy():
    def tellMeWherePlayer(self):
        enemyPos = vec(self.rect.center)
        playerPos = vec(self.target.rect.center)
        distanceToPlayer = (playerPos - enemyPos).magnitude()
        if distanceToPlayer != 0:
            dir = (playerPos-enemyPos).normalize()
        else:
            dir = vec()

        return distanceToPlayer,dir
    
    def tellMeWhereAttacker(self):
        enemyPos = vec(self.rect.center)
        attackerPos = vec(self.target.rect.center)
        distanceToPlayer = (attackerPos - enemyPos).magnitude()
        if distanceToPlayer != 0:
            dir = (attackerPos-enemyPos).normalize()
        else:
            dir = vec()

        return distanceToPlayer,dir


    def imComing(self):
        dist, dir = self.tellMeWherePlayer()
        if dist <= self.moveRadius:
            self.dir = dir
            self.status = self.status.split("_")[0]
        else:
            self.dir = vec()
        return dir
    
    def facePlayer(self):
        dist , dir =self.tellMeWherePlayer()
        if dist < self.agroRadius:
            if -0.5<dir.y<0.5:
                if dir.x <0: #Player is to the left
                    self.status = "left_idle"
                elif dir.x > 0: #Player is on the right 
                    self.status = "right_idle"
            else:
                if dir.y <0:#Player is up
                    self.status = "up_idle"
                elif dir.y>0:#player is down 
                    self.status = "down_idle"
    

    def drawHealthBar(self):
        if self.curHP > 70:
            color = green
        elif self.curHP >= 50:
            color = yellow
        else:
            color = red
        BarHeight = 20
        BarWidth = 100
        fillAmount = int(BarWidth*(self.curHP/100))
        startX =  (self.rect.width / 2)-BarWidth/2
        self.healthBar = pg.Rect(startX,0,fillAmount,BarHeight)
        self.outline = pg.Rect(startX,0,BarWidth,BarHeight)
        self.bgRect = pg.Rect(startX,0,BarWidth,BarHeight)
        if self.curHP <100:
            pg.draw.rect(self.image,niceGray,self.bgRect)
            pg.draw.rect(self.image,color,self.healthBar)
            pg.draw.rect(self.image,black,self.outline,3)
    
    def die(self):
        self.game
        self.kill()


class Coffin(Entity,BadBoy):
    def __init__(self, pos, groups, imgPath, game):
        super(Coffin,self).__init__(pos, groups, imgPath, game)
        self.target = self.game.player
        self.agroRadius = 600
        self.moveRadius = 500
        self.attackRadius = 50
        self.speed = 110
        self.game = game
    
    def update(self,dt):
        self.facePlayer()
        self.imComing()
        
        if not self.attacking:
            self.move(dt)
        self.attack()
        self.animate(dt)
        self.flash()
        self.drawHealthBar()
        self.ouchTimer()
        self.checkHealth()
        if self.target.curHP <=0 and self.target != self.game.player:
                self.target = self.game.player
        
    def takeDamage(self,ammount = 10):
        if self.canBeOuch:
            self.curHP -= ammount
            self.canBeOuch = False
            self.hitTime = pg.time.get_ticks()
           
       
    def attack(self):
        dist, dir = self.tellMeWherePlayer()
        if dist < self.attackRadius and not self.attacking:
            self.attacking = True
            self.frameIndex = 0
        if self.attacking:
            self.status = self.status.split("_")[0]+"_attack"

    def animate(self, dt):
        dist , dir = self.tellMeWherePlayer()
        super(Coffin,self).animate(dt)
        if int(self.frameIndex) == 3 and self.attacking:
            if dist <= self.attackRadius:
                damage = random.randint(5,10)
                self.target.takeDamage(damage)
                if self.target != self.game.player:
                    self.target.target = self
        if self.attacking and self.frameIndex >= len(self.animaions)-1:
            self.attacking = False

class Cactus(Entity,BadBoy):
    def __init__(self, pos, groups, imgPath, game):
        super(Cactus,self).__init__(pos, groups, imgPath, game)
        self.target = self.game.player
        self.agroRadius = 800
        self.moveRadius = 550
        self.attackRadius =350
        self.speed = 110
        self.bulletShot = False

    

    def update(self,dt):
        self.facePlayer()
        self.imComing()
        
        if not self.attacking:
            self.move(dt)
        self.attack()
        self.animate(dt)
        self.flash()
        self.drawHealthBar()
        self.ouchTimer()
        self.checkHealth()
        if self.target.curHP <=0 and self.target != self.game.player:
                self.target = self.game.player
      

    def drawMuzzle(self):
        self.muzzle = pg.Rect(0,0,5,5)
        pg.draw.rect(self.image,None,self.muzzle)

    def attack(self):
        dist, dir = self.tellMeWherePlayer()
        if dist < self.attackRadius and not self.attacking:
            self.attacking = True
            self.frameIndex = 0
        if self.attacking:
            
            self.status = self.status.split("_")[0]+"_attack"
    
    def animate(self, dt):
        dist , dir = self.tellMeWherePlayer()
        super(Cactus,self).animate(dt)
        if int(self.frameIndex) == 6 and self.attacking:
            if dist <= self.attackRadius:
                if dist < 40:
                    self.target.takeDamage(random.randint(5,10))
                else:
                    bulletStartPos = self.rect.center + dir *150
                    if not self.bulletShot:
                        self.game.spawnBullet(bulletStartPos,dir,self)
                        self.bulletShot = True
        if self.attacking and self.frameIndex >= len(self.animaions)-2:
            
            self.frameIndex = 0
            self.status = self.status.split("_")[0]
            self.attacking = False
            self.bulletShot = False
    