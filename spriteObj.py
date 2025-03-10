from Assets.scripts.settings import *

class SpriteObj(pg.sprite.Sprite):
    def __init__(self,spriteFolderName='',tag="Object",spriteAmount = 1,animatedSptrite = False,
                 spriteColor = transparent,boundType = "solid",moveType = ["keyboard"],
                 verticalMovement = False,horizontalMovement = False, speed = 10,
                 imageSize = ((TILE_SIZE[0])*2,(TILE_SIZE[1])*2)):
        
        super(SpriteObj, self).__init__()
        #animation vars
        self.animIndex = 0
        self.canFlip = False
        self.canAnimate = animatedSptrite
        self.animDir = 10
        self.animCooldown = self.animDir
        self.imgsOrg = []
        self.animatedSprite = animatedSptrite
        self.spriteAmount = spriteAmount
        playerDir = os.path.join(spritesDir,spriteFolderName)
        
        if spriteFolderName != '' and self.animatedSprite:
            for i in range(0,self.spriteAmount):
                
                try:
                    x = pg.image.load(os.path.join(playerDir,str.format("{}.png",i))).convert()
                    self.imgsOrg.append(x)
                except:
                    pass
                self.image = self.imgsOrg[self.animIndex]
        elif spriteFolderName != '' and not self.animatedSprite:
            spriteNum = random.randint(0,self.spriteAmount-1)
            self.image = pg.image.load(os.path.join(playerDir,str.format("{}.png",spriteNum))).convert()
        else:
            self.image = pg.Surface([TILE_SIZE[0], TILE_SIZE[1]]) 
            self.image.fill(spriteColor) 
            self.image.set_colorkey(spriteColor) 
        

        #speed vars
        self.speed = speed

        #player vars
        
        # self.image = pg.image.load(os.path.join(spritesDir,"player.png")).convert()
        self.image.set_colorkey(black)
        self.imgsize = imageSize
        self.image = pg.transform.scale(self.image,self.imgsize)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        self.rect.bottom = HEIGHT-90
        self.tag = tag

        #movement vars
        self.mouseMovement = True
        self.verticalMovement = verticalMovement
        self.horizontalMovement = horizontalMovement
        self.boundType = boundType #solid wrap bounce none
        self.moveType = moveType #mouse or keyboard if none then auto
        self.moveDirX = 1
        self.moveDirY = 1
        self.goingLeft = False
        self.goingRight = True

        #mouse vars
        self.curMousePos = pg.mouse.get_pos()

    def update(self,dt):
        self.move()
        if self.animatedSprite:
            if self.canFlip:
                self.animate()
            else:
                self.animCooldown -= dt
                if self.animCooldown <= 0:
                    self.canFlip = True
                

        

    def animate(self):
        if self.moveDirX !=0 or self.moveDirY !=0:
            self.animIndex +=1
            if self.animIndex >= len(self.imgsOrg):
                self.animIndex = 0
            
            
            self.image = self.imgsOrg[self.animIndex]
            self.image.set_colorkey(black)
            self.image = pg.transform.scale(self.image,self.imgsize)
            self.canFlip = False
            self.animCooldown = self.animDir
            if self.moveDirX < 0:
                self.image = pg.transform.flip(self.image,self.rect.x,0)
            
        
        

    def move(self):
        if not self.verticalMovement:
            self.moveDirY = 0
        if not self.horizontalMovement:
            self.moveDirX = 0
        mousePos = pg.mouse.get_pos()
        if self.boundType == "wrap":
            if self.rect.left >= WIDTH:
                self.rect.right = 0
            elif self.rect.right <= 0:
                self.rect.left = WIDTH
            if self.rect.bottom < 0:
                self.rect.top = HEIGHT
            elif self.rect.top > HEIGHT:
                self.rect.bottom = 0
        elif self.boundType == "bounce":
            print(self.tag,"is set to bounce movement")
            if self.rect.right >= WIDTH or self.rect.left <= 0:
                print(self.tag,"?")
                self.moveDirX *=-1
                
            if self.rect.top <=0 or self.rect.bottom >= HEIGHT:
                self.moveDirY *=-1
        elif self.boundType == "solid":
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            elif self.rect.left < 0:
                self.rect.left = 0
            if self.rect.top < 0:
                self.rect.top = 0
            elif self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
        elif self.boundType == "none":
            print(self.tag,"is set to none bound type")
            pass
        if "keyboard" in self.moveType:
            self.moveDirX = 0
            self.moveDirY = 0
            keys = pg.key.get_pressed()
            if self.horizontalMovement:
                if keys[pg.K_LEFT] or keys[pg.K_a]:
                    self.moveDirX = -1
                    self.mouseMovement = False

                    #Flip Sprite
                    if not self.goingLeft:
                        self.image = pg.transform.flip(self.image,self.rect.x,0)
                    self.goingLeft = True
                    self.goingRight = False
                elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                    self.moveDirX = 1
                    self.mouseMovement = False

                    #Flip Sprite
                    if not self.goingRight:
                        self.image = pg.transform.flip(self.image,self.rect.x,0)
                    self.goingLeft = False
                    self.goingRight = True
                elif not (keys[pg.K_LEFT]) and not (keys[pg.K_a]):
                    self.moveDirX = 0
                elif not (keys[pg.K_RIGHT]) and not (keys[pg.K_d]):
                    self.moveDirX = 0
            if self.verticalMovement:
                if keys[pg.K_UP] or keys[pg.K_w]:
                    self.moveDirY = -1
                elif keys[pg.K_DOWN] or keys[pg.K_s]:
                    self.moveDirY = 1
                elif not (keys[pg.K_UP] and not keys[pg.K_w]):
                    self.moveDirY = 0
                elif not (keys[pg.K_DOWN]) and not (keys[pg.K_s]):
                    self.moveDirY = 0

        if mousePos[0] != self.curMousePos[0]:
            self.mouseMovement = True
        if mousePos[1] != self.curMousePos[1]:
            self.mouseMovement = True

        if mousePos < self.curMousePos and ("mouse" in self.moveType):#mouse going left 
            if not self.goingLeft:
                    self.image = pg.transform.flip(self.image,self.rect.x,0)
            self.goingLeft = True
            self.goingRight = False
        if mousePos > self.curMousePos and ("mouse" in self.moveType):#mouse going right 
            if not self.goingRight:
                    self.image = pg.transform.flip(self.image,self.rect.x,0)
            self.goingLeft = False
            self.goingRight = True

        if "mouse" in self.moveType and self.mouseMovement:
            self.moveDirX = 0
            self.moveDirY = 0
            mouseX = mousePos[0]
            mouseY = mousePos[1]
            self.curMousePos = mousePos
            if self.horizontalMovement:
                self.rect.centerx = mousePos[0]
            if self.verticalMovement:
                self.rect.centery = mousePos[1]

        if 'auto' in  self.moveType:
            print(self.tag, "is set to auto")
            
        self.rect.center = (self.rect.centerx + self.speed * self.moveDirX, self.rect.centery + self.speed * self.moveDirY)


