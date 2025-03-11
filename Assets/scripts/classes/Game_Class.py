from Assets.scripts.settings import *
from Assets.scripts.classes.playerClass import Player
from Assets.scripts.classes.spriteGroups import AllSprites
from Assets.scripts.classes.baseSprite import BaseSprite,invisObj ,Entity
from pytmx.util_pygame import load_pygame
from Assets.scripts.classes.bulletClass import Bullet
from Assets.scripts.classes.enemiesClass import Coffin,Cactus

class Game(object):
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.is_playing = True
        self.window = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.players = pg.sprite.Group()
        self.all_sprites = AllSprites()
        self.solidObjects = pg.sprite.Group()
        self.enities = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.cactusGroup = pg.sprite.Group()
        self.coffinGroup = pg.sprite.Group()
        self.bulletsGroup = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.mapSprites = pg.sprite.Group()

        self.lastEnemyPos = vec()

        self.goto = "0"
        self.fromScene = "start"
        self.levelPaths = ['Assets/sprites/myMaps/map.tmx',"Assets/sprites/myMaps/map2.tmx"]    
        
        self.musicPaths = ['Assets/sound/music.mp3','Assets/sound/music.mp3']
        
        self.keys = pg.sprite.Group()
        self.keySpawed = False
        self.onkey = False

        self.curPlayerSpawn = vec()
        self.gameSetup()

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

    def update(self):
        self.dt = self.clock.tick(FPS)/1000
        self.all_sprites.update(self.dt)

        #Bullet collisions
        self.checkBulletCol()
        


        boundsHit = pg.sprite.groupcollide(self.doors,self.players,False,False) # Coll between player and doors
        if boundsHit:
            for hit in boundsHit:
                self.goto = hit.goto
                self.fromScene = hit.fromScene
                self.loadMap(int(self.goto))   

        if not self.keySpawed:
            self.checkEnemiesDead()   
        elif self.keySpawed:
            self.key.animate(self.dt)
            keyHit = pg.sprite.groupcollide(self.keys,self.players,False,False)
            if keyHit:
                
                self.onkey = True
            else:
                self.onkey = False

        
    def draw(self):
        self.window.fill(black)
        self.all_sprites.customDraw(self.player)
       
        self.DrawBarHoriz(self.window,(25,50),self.player.curHP,250,red,"HP")
        self.drawDataImg((25,90),self.bulletImgMini,self.player.ammo)

        if self.player.ammo == 0:
            draw_text(self.window,'Press R to reload',30,center_x,center_x)
        if self.onkey:
            draw_text(self.window,'Press E to pickup',30,center_x,center_y+60)

        pg.display.flip()

    def loadData(self):
        

        self.tmx_map_data = load_pygame(self.levelPaths[0])
        self.tmx_map2_data = load_pygame(self.levelPaths[1])
        # self.tmx_map3_data = load_pygame(self.levelPaths[2])
        # self.tmx_map4_data = load_pygame(self.levelPaths[3])
        
        self.bulletSurf = pg.image.load("Assets/sprites/other/particle.png").convert_alpha()
        
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

    def loadMap(self,mapInt):
        self.clearGroups()
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
                if Ent.name == 'Hole':
                    invisObj(Ent.x,Ent.y,Ent.width,Ent.height,(self.mapSprites,self.solidObjects,self.doors),self,Ent.goto,Ent.fromScene)
                if Ent.name == "Wall" or Ent.name == 'HB':
                    invisObj(Ent.x,Ent.y,Ent.width,Ent.height,(self.mapSprites,self.solidObjects),self)
                if Ent.name == "Player":
                    if Ent.fromScene == self.fromScene:
                        self.curPlayerSpawn = vec(Ent.x,Ent.y)
                        self.spawnPlayer()
               

        elif mapInt == 1:
            self.all_sprites.bg = self.bg = pg.image.load(os.path.join(PATHS["other"], "bg2.png")).convert()
            for x,y,surf in self.tmx_map2_data.get_layer_by_name("Bounds").tiles():
                bound = BaseSprite((x*TILE_SIZE,y*TILE_SIZE),surf,(self.all_sprites,self.solidObjects,self.mapSprites))
            for obj in self.tmx_map2_data.get_layer_by_name("Objects"):
                BaseSprite((obj.x,obj.y),obj.image,(self.all_sprites,self.mapSprites))
            for Ent in  self.tmx_map2_data.get_layer_by_name("Entities"):
                if Ent.name == "Coffin":
                    Coffin((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["coffin"],self)
                if Ent.name == "Cactus":
                    Cactus((Ent.x, Ent.y),(self.all_sprites,self.enemies,self.coffinGroup),PATHS["cactus"],self)
                if Ent.name == "Player":
                    if Ent.fromScene == self.fromScene:
                        self.curPlayerSpawn = vec(Ent.x,Ent.y)
                        self.spawnPlayer()
               
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

        
        

    
    def spawnPlayer(self):
        self.player = Player((self.curPlayerSpawn.x,self.curPlayerSpawn.y),(self.players,self.all_sprites),os.path.join(spritesDir,"player"),self,debug=True) 

    def checkBulletCol(self):
        pg.sprite.groupcollide(self.bulletsGroup,self.solidObjects,True,False) #Coll between bullets and solid objects
        hits2 = pg.sprite.groupcollide(self.bulletsGroup,self.enemies,False,False,pg.sprite.collide_mask)#Coll between enimies and bullets
        hits = pg.sprite.groupcollide(self.enemies,self.bulletsGroup,False,True,pg.sprite.collide_mask) # Coll between bullets and enemies 
       
        if hits2:
            for bullet in hits2:
                if hits:
                    for hit in hits:

                        hit.takeDamage(random.randint(10,25))
                        hit.target = bullet.owner
                    
        playerHits = pg.sprite.groupcollide(self.players,self.bulletsGroup,False,True,pg.sprite.collide_mask)#Coll between players and bullets
        if playerHits:
            self.player.takeDamage(random.randint(10,15))
    

    def reSpawnPlayer(self):
        self.player.pos = self.curPlayerSpawn
        self.all_sprites.add(self.player)
        

    def spawnBullet(self,pos,dir,owner):
        Bullet(pos,dir,self.bulletSurf,(self.all_sprites,self.bulletsGroup),owner)

    def checkEnemiesDead(self):
        if len(self.enemies) == 0:
            self.spawnKey()
            self.keySpawed = True

    def spawnKey(self):
        key_position = self.lastEnemyPos
        key_path = PATHS['sprites']+'/keys/key1'  # Load your key image
        self.key = Entity(key_position, (self.all_sprites,self.keys), key_path,self,status='idle',scale=2) # Add the key to the appropriate groups
        
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
        self.window.fill(black)
        draw_text(self.window, TITLE, 150, WIDTH / 2, HEIGHT / 4,  green, "impact")
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
                    
                    