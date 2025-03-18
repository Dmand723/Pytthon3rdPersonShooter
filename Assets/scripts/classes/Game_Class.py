from Assets.scripts.settings import *
from Assets.scripts.classes.playerClass import Player
from Assets.scripts.classes.spriteGroups import AllSprites
from Assets.scripts.classes.baseSprite import BaseSprite,invisObj ,Entity,TransportDoor,MouseSprite
from pytmx.util_pygame import load_pygame
from Assets.scripts.classes.bulletClass import Bullet, FireBall
from Assets.scripts.classes.enemiesClass import Coffin,Cactus,Witch


class Game(object):
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.is_playing = True
        self.window = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        
        self.createGroups()

        self.lastEnemyPos = vec()

        self.goto = "0"
        self.fromScene = "0"
        self.levelPaths = [PATHS['map1'],PATHS['map2']]    
        
        self.musicPaths = [PATHS['sound']+'/music.mp3',PATHS['sound']+'/music.mp3']
        
        self.interactables = pg.sprite.Group()
        
        self.onkey = False
        self.trapDoorHit = False

        self.onTorch = False

        self.interactText:str = ''

        self.curPlayerSpawn = vec()
        self.player = None
        
        self.gameSetup()
        pg.mouse.set_visible(False)
        self.mousePos = pg.mouse.get_pos()
        
    
    def createGroups(self):
        self.players = pg.sprite.Group()
        self.mouseSprite = pg.sprite.Group()
        self.all_sprites = AllSprites()
        self.spritesBelowPlayer = pg.sprite.Group()
        self.solidObjects = pg.sprite.Group()
        self.damageObjs = pg.sprite.Group()
        self.enities = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.cactusGroup = pg.sprite.Group()
        self.coffinGroup = pg.sprite.Group()
        self.bulletsGroup = pg.sprite.Group()
        self.transports = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.mapSprites = pg.sprite.Group()
        self.spritesOnTop = pg.sprite.Group()

    def get_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.mixer.music.stop()
                pg.quit()
                sys.exit()
            if event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    pg.mixer.music.stop()
                    self.is_playing = False
                elif event.key == pg.K_e:
                    if self.keySpawed and self.onkey:
                        self.key.kill()
                        self.player.invetory['key'] = 1 
                    if self.onTorch:
                        self.torch.kill()
                        self.player.invetory['torch'] = 1
                    elif self.trapDoorHit and not self.trapDoor.isOpen:
                        try: 
                            if self.player.invetory['key'] >0:
                                self.trapDoor.openDoor()
                                self.player.invetory['key'] -=1
                            else:
                                self.interactText = 'Missing key'
                        except KeyError:
                            self.interactText = 'Missing key'

                    elif self.trapDoor.isOpen and self.trapDoorHit:
                        self.goto = self.trapDoor.goto
                        self.fromScene = self.trapDoor.fromScene
                        self.loadMap(int(self.goto))
                elif event.key == pg.K_m:#Mute/Unmute game music
                    if pg.mixer.music.get_volume() > 0:
                        pg.mixer.music.set_volume(0)
                    else:
                        pg.mixer.music.set_volume(50)

    def update(self):
        self.dt = self.clock.tick(FPS)/1000
        self.all_sprites.update(self.dt)

        #Bullet collisions
        self.checkBulletCol()

        self.checkDamangeCol()
        
        self.checkTransportCol()
        # self.mousePos = vec(pg.mouse.get_pos())
        # self.mousePos.x = self.mousePos.x+WIDTH
        # self.mousePos.y = self.mousePos.y+HEIGHT
        # self.mouse.rect.center = self.mousePos
        # print(self.mousePos,"Mouse")
        # print(self.player.pos,'Player')


           

        if not self.keySpawed:
            self.checkEnemiesDead()   
        elif self.keySpawed:
            self.key.animate(self.dt)
        if len(self.interactables) != 0:
            Hit = pg.sprite.groupcollide(self.interactables,self.players,False,False)
            if Hit:
                for item in Hit:
                    if item.tag == 'key':
                        self.onkey = True
                    else:
                        self.onkey = False
                    if item.tag == 'torch':
                        self.onTorch = True
                    else:
                        self.onTorch = False
            else:
                self.onkey = False
                self.onTorch = False
        else:
            self.onkey = False
            self.onTorch = False

        
    def draw(self):
        self.window.fill(black)
        self.all_sprites.customDraw(self.player,self.spritesBelowPlayer,self.spritesOnTop)
       
        self.hpBar = self.DrawBarHoriz(self.window,(25,50),self.player.curHP,250,red,"HP")
        self.stanimaBar = self.DrawBarHoriz(self.window,(25,110),self.player.stanima,250,blue,'Stanima')
        self.ammoBar = self.drawDataImg((25,150),self.bulletImgMini,self.player.ammo)
        if int(self.goto) ==1:
            self.drawFog()

        if self.player.ammo == 0:
            draw_text(self.window,'Press R to reload',30,center_x,center_x)
        if self.onkey:
            self.interactText = 'Press E to pickup'
        elif self.trapDoorHit and not self.trapDoor.isOpen:
            if self.interactText != 'Missing key':
                self.interactText = 'Press E to open'
        elif self.trapDoorHit and self.trapDoor.isOpen:
            self.interactText = 'Press E to enter'
        elif self.onTorch:
            self.interactText = "Press E to pickup torch"
        else:
            self.interactText = ''
        draw_text(self.window,self.interactText,30,center_x,center_y+60)
        pg.display.flip()

    def loadData(self):
        

        self.tmx_map_data = load_pygame(self.levelPaths[0])
        self.tmx_map2_data = load_pygame(self.levelPaths[1])
        # self.tmx_map3_data = load_pygame(self.levelPaths[2])
        # self.tmx_map4_data = load_pygame(self.levelPaths[3])
        
        self.bulletSurf = pg.image.load(PATHS['other']+'/particle.png').convert_alpha()
        self.mouseImg = pg.image.load(PATHS['other']+'/crosshair.png')
        
        self.bulletImg = pg.image.load(os.path.join(PATHS['other'],"bullet.png")).convert_alpha()
        self.bulletImgMini = pg.transform.scale(self.bulletImg,(30,30))
        

    def gameSetup(self):
        self.loadData()
        self.loadMap(int(self.goto)) 
       
    def clearGroups(self):
        self.players.empty()
        self.all_sprites.empty() 
        self.solidObjects.empty() 
        self.enities.empty() 
        self.enemies.empty() 
        self.cactusGroup.empty()  
        self.coffinGroup.empty()  
        self.bulletsGroup.empty() 
        self.mapSprites.empty()  
        self.transports.empty()
        self.doors.empty()
        self.spritesBelowPlayer.empty()
        self.spritesOnTop.empty()
        self.damageObjs.empty()
        self.interactables.empty()

    def loadMap(self,mapInt):
        self.window.fill(black)
        draw_text(self.window, 'Loading. . .', 150, WIDTH / 2, HEIGHT / 4,  green, "impact")
        pg.display.flip()
        self.clearGroups()
        self.mouse = MouseSprite((0,0),self.mouseImg,(self.all_sprites,self.mouseSprite),self)
        pg.mixer.music.load(self.musicPaths[int(self.goto)])
        pg.mixer.music.play(-1)
        if mapInt == 0:
            self.all_sprites.bg = self.bg = pg.image.load(os.path.join(PATHS["other"], "bg.png")).convert()
            for x,y,surf in self.tmx_map_data.get_layer_by_name("Bounds").tiles():
                BaseSprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.mapSprites))
            for obj in self.tmx_map_data.get_layer_by_name("Objects"):
                BaseSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.mapSprites))
            for Ent in  self.tmx_map_data.get_layer_by_name("Entities"): 
                if Ent.name == "Coffin":
                    Coffin((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["coffin"],self)
                if Ent.name == "Cactus":
                    Cactus((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["cactus"],self)
                if Ent.name == 'TrapDoor':
                    surf1 = pg.transform.scale(Ent.image,(Ent.width,Ent.height))
                    surf2 = pg.image.load(os.path.join(PATHS['tilesets'],Ent.img2))
                    surf2 = pg.transform.scale(surf2,(Ent.width,Ent.height))
                    self.trapDoor = TransportDoor((Ent.x,Ent.y),surf1,surf2,(self.all_sprites,self.mapSprites,self.spritesBelowPlayer,self.doors,self.transports),Ent.name)
                if Ent.name == "Wall" or Ent.name == 'HB':
                    invisObj(Ent.x,Ent.y,Ent.width,Ent.height,(self.mapSprites,self.solidObjects),self)
                if Ent.name == "Player":
                    if Ent.fromScene == self.fromScene:
                        if self.player:
                            self.curPlayerSpawn = vec(Ent.x,Ent.y)
                            self.reSpawnPlayer()
                        else:
                            self.curPlayerSpawn = vec(Ent.x,Ent.y)
                            self.spawnPlayer()
               

        elif mapInt == 1:
            self.all_sprites.bg = self.bg = pg.image.load(os.path.join(PATHS["other"], "bg2.png")).convert()
            for x,y,surf in self.tmx_map2_data.get_layer_by_name("Bounds").tiles():
                BaseSprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.mapSprites))
            for obj in self.tmx_map2_data.get_layer_by_name("Objects"):
                BaseSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.mapSprites))
            for obj in self.tmx_map2_data.get_layer_by_name("Damage"):
                BaseSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.mapSprites,self.damageObjs))
            for Ent in  self.tmx_map2_data.get_layer_by_name("Entities"): 
                if Ent.name == "Coffin":
                    Coffin((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["coffin"],self)
                if Ent.name == "Cactus":
                    Cactus((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["cactus"],self)
                if Ent.name == 'WitchDoc':
                    Witch((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["witchDoc"],self)
                if Ent.name == "Bolder":
                    BaseSprite((Ent.x,Ent.y),Ent.image,(self.all_sprites,self.mapSprites,self.solidObjects,self.spritesOnTop))
                if Ent.name == "Torch":
                    self.torch = Entity((Ent.x,Ent.y), (self.all_sprites,self.spritesBelowPlayer,self.interactables), PATHS['sprites']+"/torch",self,status='idle',scale=1,tag='torch')
                if Ent.name == 'TrapDoor':
                    surf1 = pg.transform.scale(Ent.image,(Ent.width,Ent.height))
                    surf2 = pg.image.load(os.path.join(PATHS['tilesets'],Ent.img2))
                    surf2 = pg.transform.scale(surf2,(Ent.width,Ent.height))
                    self.trapDoor = TransportDoor((Ent.x,Ent.y),surf1,surf2,(self.all_sprites,self.mapSprites,self.spritesBelowPlayer,self.doors,self.transports),Ent.name)
                if Ent.name == "Wall" or Ent.name == 'HB':
                    invisObj(Ent.x,Ent.y,Ent.width,Ent.height,(self.mapSprites,self.solidObjects),self)
                if Ent.name == "Player":
                    if Ent.fromScene == self.fromScene:
                        if self.player:
                            self.curPlayerSpawn = vec(Ent.x,Ent.y)
                            self.reSpawnPlayer()
                        else:
                            self.curPlayerSpawn = vec(Ent.x,Ent.y)
                            self.spawnPlayer()
            self.createFog()

        # elif mapInt == 2: 
        #     for x,y,surf in self.tmx_map3_data.get_layer_by_name("Bounds").tiles():
        #         BaseSprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.solidObjects,self.mapSprites))
        #     for obj in self.tmx_map3_data.get_layer_by_name("Objects"):
        #         BaseSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.mapSprites))
        #     for Ent in  self.tmx_map3_data.get_layer_by_name("Entities"):
        #         if Ent.name == "Player":
        #             self.curPlayerSpawn = vec(Ent.x,Ent.y)
        #         if Ent.name == "Coffin":
        #             Coffin((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["coffin"],self)
        #         if Ent.name == "Cactus":
        #             Cactus((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["cactus"],self)
                    
        
        # elif mapInt == 3:
        #     for x,y,surf in self.tmx_map4_data.get_layer_by_name("Bounds").tiles():
        #         BaseSprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.solidObjects,self.mapSprites))
        #     for obj in self.tmx_map4_data.get_layer_by_name("Objects"):
        #         BaseSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.mapSprites))
        #     for Ent in  self.tmx_map4_data.get_layer_by_name("Entities"):
        #         if Ent.name == "Player":
        #             self.curPlayerSpawn = vec(Ent.x,Ent.y)
        #         if Ent.name == "Coffin":
        #             Coffin((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["coffin"],self)
        #         if Ent.name == "Cactus":
        #             Cactus((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["cactus"],self)

        else:
            print("Error No Map "+mapInt)
        
        self.keySpawed = False

    def createFog(self):#Creates a fog that obstructs players veiw
        self.fog = pg.Surface((WIDTH,HEIGHT))
        self.fog.fill(black)
        self.light_mask = pg.image.load(PATHS["other"]+"/lightMask.png").convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask,LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

    def drawFog(self,vec =None):
       

        self.fog.fill(black)
        try:
            if self.player.invetory['torch'] > 0:
                lightCenter = self.player.rect.center - self.all_sprites.getoffset()
            else:
                lightCenter = self.torch.rect.center - self.all_sprites.getoffset()
        except KeyError:
            lightCenter = self.torch.rect.center - self.all_sprites.getoffset()
        self.light_rect.center = lightCenter
        self.fog.blit(self.light_mask,self.light_rect)
        self.window.blit(self.fog,(0,0),special_flags=pg.BLEND_MULT)

    def spawnPlayer(self):
        self.player = Player((self.curPlayerSpawn.x,self.curPlayerSpawn.y),(self.players,self.all_sprites),os.path.join(spritesDir,"player"),self,debug=True) 

    def checkBulletCol(self):
        bullethit = pg.sprite.groupcollide(self.bulletsGroup,self.solidObjects,False,False) #Coll between bullets and solid objects
        if bullethit:
            for hit in bullethit:
                hit.die()
        hits2 = pg.sprite.groupcollide(self.bulletsGroup,self.enemies,False,False,pg.sprite.collide_mask)#Coll between enimies and bullets
        hits = pg.sprite.groupcollide(self.enemies,self.bulletsGroup,False,False,pg.sprite.collide_mask) # Coll between bullets and enemies 
       
        if hits2:
            for bullet in hits2:
                if hits:
                    for hit in hits:

                        hit.takeDamage(random.randint(10,25))
                        hit.target = bullet.owner
                bullet.die()
                    
        playerHits = pg.sprite.groupcollide(self.bulletsGroup,self.players,False,False,pg.sprite.collide_mask)#Coll between players and bullets
        if playerHits:
            for bul in playerHits:
                if bul.owner != self.player:
                    self.player.takeDamage(random.randint(10,15))
                    bul.die()
           
    def checkDamangeCol(self):
        dmgHit1 = pg.sprite.groupcollide(self.players,self.damageObjs,False,False,pg.sprite.collide_mask)#Coll bettween players and damage objects
        if dmgHit1:
            self.player.takeDamage(random.randint(3,5))
        dmgHit2 = pg.sprite.groupcollide(self.enemies,self.damageObjs,False,False,pg.sprite.collide_mask)#Col bettween enemies and damage objects
        if dmgHit2:
            for hit in dmgHit2:
                hit.takeDamage(random.randint(3,5))
    
    def checkTransportCol(self):
        boundsHit = pg.sprite.groupcollide(self.transports,self.players,False,False) # Coll between player and transports
        if boundsHit:
            for hit in boundsHit:
                if hit.name == 'TrapDoor':
                    self.trapDoorHit = True
                else:
                    self.trapDoorHit = False
        else:
            self.interactText = ''
            self.trapDoorHit = False

    def reSpawnPlayer(self):
        self.player.pos = self.curPlayerSpawn
        self.all_sprites.add(self.player)
        self.players.add(self.player)
        

    def spawnBullet(self,pos,dir,owner):
        Bullet(pos,dir,self.bulletSurf,(self.all_sprites,self.bulletsGroup),owner)

    def spawnFireBall(self,pos,dir,owner):
        FireBall(pos,dir,(self.all_sprites,self.bulletsGroup),owner)

    def checkEnemiesDead(self):
        if len(self.enemies) == 0:
            self.spawnKey()
            self.keySpawed = True

    def spawnKey(self):
        key_position = self.lastEnemyPos
        key_path = PATHS['sprites']+'/keys/key'+self.goto  # Load your key image
        if int(self.goto) == 0:
            self.key = Entity(key_position, (self.all_sprites,self.interactables), key_path,self,status='idle',scale=2,tag='key')
        if int(self.goto) == 1:
            self.key = Entity(key_position, (self.all_sprites,self.interactables), key_path,self,status='idle',scale=1,tag='key')  

    def DrawBarHoriz(self,surf,pos,value,length,fillColor,tag="",hasTag = True):
        value = value
        if value < 0:
            value = 0
        else:
            value = value
        BarLength = int(length)
        BarHeight = int(length*.1)
        fillAmount = (value/100)*BarLength
        outlineRect = pg.Rect(pos[0],pos[1],BarLength,BarHeight)
        if pos[1] > WIDTH/2:
            moveValue = pos[0] + (BarLength-fillAmount)
        else:
            moveValue = pos[0]
        fillRect = pg.Rect(moveValue,pos[1],fillAmount,BarHeight)
        pg.draw.rect(surf,fillColor,fillRect)
        pg.draw.rect(surf,black,outlineRect,3)
        if hasTag:
            draw_text(surf,tag,BarHeight,(pos[0]*2),(pos[1]-(BarHeight+5)),black)
            draw_text(surf,str(value)+" / 100", int(BarHeight),pos[0]+70,pos[1]+4)

    def drawBarVert(self,surf,pos,value,height,fillColor,tag="",hasTag = True):
        value = value
        if value < 8:
            value = 0
        else:
            value = value
        BarHeight = int(height)
        BarLength = int(height*.15)
        fillAmount = (value/100)*BarLength
        outlineRect = pg.Rect(pos[0],pos[1],BarLength,BarHeight)
        fillRect = pg.Rect(pos[0],pos[1]-170,BarLength,fillAmount-170)
        pg.draw.rect(surf,fillColor,fillRect)
        pg.draw.rect(surf,black,outlineRect,3)
        if hasTag:
            draw_text(surf,tag,20,(pos[0]*2),(pos[1]-(BarHeight+5)),black)
            draw_text(surf,str(value)+" / 100", 20,pos[0]+70,pos[1]-3)

    def drawDataImg(self,pos,img,data,horz=True):
        surf = pg.display.get_surface()
        image = img
        imgRect = image.get_rect()
        w = imgRect.width
        h = imgRect.height
        if horz:
            for i in range(data):
                imgRect.x = pos[0]+(w+5)*i
                imgRect.y = pos[1]
                surf.blit(image,imgRect)
        else:
            for i in range(data):
                imgRect.x = pos[0]
                imgRect.y = pos[1]+(h+5)*i
                surf.blit(image,imgRect)

    def play(self):
        while self.is_playing:
            self.clock.tick(FPS)
            self.get_events()
            self.update()
            self.draw()

    def start_screen(self):
        bg = pg.image.load(PATHS['other']+ '/startScreen.png')
        self.window.fill(grassGreen)
        draw_text(self.window, TITLE, 150, WIDTH / 2, HEIGHT / 4,  niceGray, "impact")
        pg.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYUP:
                    if event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                        waiting = False

    def end_screen(self):
        self.window.fill(black)
        
        draw_text(self.window, "GameOver", 150, WIDTH / 2, HEIGHT / 4,red, "impact")
        draw_text(self.window, "yould you like to play again (Y/N)?", 75, WIDTH / 2, HEIGHT / 4+200,green, "impact")
        pg.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    return "quit"
                    pg.quit()
                if event.type == pg.KEYUP:
                    if event.key == pg.K_y:
                        waiting = False
                    elif event.key == pg.K_n:
                        return "quit"