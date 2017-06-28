from .entities import Entity
import numpy as np
from tqdm import tqdm
import glob

class World:
    def __init__(self,name):
        self.name = name
        self.currentEID = 0
        self.spawn = (0,64,0) #SpawnLocation
        self.chunks = {}  #Actual World
        self.players = [] #List of player files
        self.entities={} #Entities in world

    def add_entity(self,location,look,type,name,uuid="",inventory=None):
        self.currentEID+=1
        self.entities[self.currentEID] = Entity(self.currentEID, location, look, type, name, uuid, inventory)
        return self.currentEID

    def remove_entity(self,eid,save=False):
        if save:
            self.saveEntity(self.entities[eid])
        del self.entities[eid]

    def saveEntity(self,entity):
        pass

    def loadWorld(self,name):
        pass

    def genChunk(self,x,z):

        if not x in self.chunks.keys():
            self.chunks[x] = {}
        self.chunks[x][z] = np.asarray([(0, 0,0,0) * 4096] * 16, dtype=np.ubyte).reshape((16, 4096, 4))
        for y in range(3):
            self.chunks[x][z][y] = np.asarray([(1, 0,0,0) * 4096], dtype=np.ubyte).reshape((4096, 4))
        self.saveChunk(x,z)

    def genWorld(self,type='flatland'):
        if type == 'flatland':
            for x in range(16):
                for z in range(16):
                    self.genChunk(x,-z)
                    self.genChunk(x, z)
                    self.genChunk(-x, z)
                    self.genChunk(-x,-z)


    def saveWorld(self):
        print("Saving World!")
        for x in self.chunks.keys():
            for z in self.chunks[x].keys():
                self.saveChunk(x,z)
        print("World Saved!")

    def loadFullWorld(self):
        print("Loading Full World!")
        for y in glob.glob1(self.name,"*.npy"):
            x = int(y.split("_")[1])
            z = int(y.split("_")[2].replace(".npy",""))
            self.loadChunk(x,z)
        print("Full World Loaded!")



    def loadSpawn(self):
        print("Loading spawn!")
        for x in range(6):
            for y in range(6):
                self.loadChunk(x,y)
                self.loadChunk(-x, y)
                self.loadChunk(x,-y)
                self.loadChunk(-x,-y)
        print("Spawn Loaded!")

    def loadChunk(self,x,z):
        if not x in self.chunks.keys():
            self.chunks[x]={}
        try:
            self.chunks[x][z]=np.load(self.name+"\chunks\chunk_"+str(x)+"_"+str(z)+".npy")

        except:
            print("Failed to Load chunk! "+str(x)+ " "+str(z))
            print("Generating chunk!")
            self.genChunk(x,z)

    def saveChunk(self,x,z):
        np.save(self.name + "\chunks\chunk_" + str(x) + "_" + str(z) + ".npy", self.chunks[x][z], allow_pickle=False)

    def getBlock(self,x,y,z):
        chunkX = x//16
        innerX = x%16
        chunkY = y // 16
        innerY = y % 16
        chunkZ = z // 16
        innerZ = z % 16
        if not chunkX in self.chunks:
            self.loadChunk( chunkX, chunkZ)
        if not chunkZ in self.chunks[chunkX]:
            self.loadChunk( chunkX, chunkZ)
        try:
            return self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX][2:]
        except:
            return (-1,0)

    def setBlock(self,x,y,z,block):
        chunkX = x//16
        innerX = x%16
        chunkY = y // 16
        innerY = y % 16
        chunkZ = z // 16
        innerZ = z % 16
        if not chunkX in self.chunks:
            self.loadChunk(self.name, chunkX, chunkZ)
        if not chunkZ in self.chunks[chunkX]:
            self.loadChunk(self.name, chunkX, chunkZ)

        if isinstance(block,tuple):
            self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX]=np.asarray([block[0],block[1],self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX][2],self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX][3]])
        else:
            self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX]=np.asarray([block[0],0,self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX][2],self.chunks[chunkX][chunkZ][chunkY][innerY*16*16 + innerZ*16 + innerX][3]])

    def getBlockLight(self,x,y,z):
        chunkX = x // 16
        innerX = x % 16
        chunkY = y // 16
        innerY = y % 16
        chunkZ = z // 16
        innerZ = z % 16
        if not chunkX in self.chunks:
            self.loadChunk(chunkX, chunkZ)
        if not chunkZ in self.chunks[chunkX]:
            self.loadChunk(chunkX, chunkZ)
        try:
            return self.chunks[chunkX][chunkZ][chunkY][innerY * 16 * 16 + innerZ * 16 + innerX][2]
        except:
            return -1

    def setBlockLight(self,x,y,z,light):
        chunkX = x // 16
        innerX = x % 16
        chunkY = y // 16
        innerY = y % 16
        chunkZ = z // 16
        innerZ = z % 16
        if not chunkX in self.chunks:
            self.loadChunk(chunkX, chunkZ)
        if not chunkZ in self.chunks[chunkX]:
            self.loadChunk(chunkX, chunkZ)
        self.chunks[chunkX][chunkZ][chunkY][innerY * 16 * 16 + innerZ * 16 + innerX][2] = light

    def getSkyLight(self, x, y, z):
        chunkX = x // 16
        innerX = x % 16
        chunkY = y // 16
        innerY = y % 16
        chunkZ = z // 16
        innerZ = z % 16
        if not chunkX in self.chunks:
            self.loadChunk(chunkX, chunkZ)
        if not chunkZ in self.chunks[chunkX]:
            self.loadChunk(chunkX, chunkZ)
        try:
            return self.chunks[chunkX][chunkZ][chunkY][innerY * 16 * 16 + innerZ * 16 + innerX][3]
        except:
            return -1

    def setSkyLight(self, x, y, z, light):
        chunkX = x // 16
        innerX = x % 16
        chunkY = y // 16
        innerY = y % 16
        chunkZ = z // 16
        innerZ = z % 16
        if not chunkX in self.chunks:
            self.loadChunk(chunkX, chunkZ)
        if not chunkZ in self.chunks[chunkX]:
            self.loadChunk(chunkX, chunkZ)
        self.chunks[chunkX][chunkZ][chunkY][innerY * 16 * 16 + innerZ * 16 + innerX][3] = light