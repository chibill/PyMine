from twisted.internet import reactor
from . import world, blocks,util
from quarry.net.server import ServerFactory, ServerProtocol


class PyMineServerProtocol(ServerProtocol):

    def send_chunk(self,x,y):
        pass

    def send_inital_chunks(self,x,y):
        for x in util.spiral(60,(x,y)):
            self.send_chunk(x[0],x[1])

    def update_keep_alive(self):
        self.send_packet("keep_alive", self.buff_type.pack_varint(0))

    def player_joined(self):

        ServerProtocol.player_joined(self)

        location = self.factory.world.spawn
        look = (0, 0)

        if self.display_name in self.factory.world.players:
            self.eid = self.factory.world.load(self.uuid) #Load and save eid
        else:
            self.eid = self.factory.world.add_entity(self.factory.world.spawn,(0,0),'Player',self.display_name,self.uuid,None)
            # Send "Join Game" packet
        self.send_packet("join_game",
                             self.buff_type.pack("iBiBB",
                                                 self.eid,  # entity id
                                                 1,  # game mode
                                                 0,  # dimension
                                                 0,  # difficulty
                                                 10),  # max players

                         self.buff_type.pack_string("flat"),  # level type
                         self.buff_type.pack("?", False))  # reduced debug info
        self.send_packet("plugin_message",
                         self.buff_type.pack_string("MC|Brand") + self.buff_type.pack_string("PyMine"))
        spawn =self.factory.world.spawn
        self.send_packet("spawn_position", self.buff_type.pack_position(spawn[0],spawn[1],spawn[2]))

        self.send_packet("player_abilities", self.buff_type.pack("?ff", 0b1111, 1.2, 10.0))
        location = self.factory.world.entities[self.eid].location
        look = self.factory.world.entities[self.eid].look
        # Send "Player Position and Look" packet
        self.send_packet("player_position_and_look",
                             self.buff_type.pack("dddff?",
                                                 location[0],  # x
                                                 location[1],  # y
                                                 location[2],  # z
                                                 look[0],  # yaw
                                                 look[1],  # pitch
                                            0b00000),  # flags
                         self.buff_type.pack_varint(0))  # teleport id
        self.send_inital_chunks(0,0)
        self.tasks.add_loop(1.0, self.update_keep_alive)



    def player_left(self):
        ServerProtocol.player_left(self)
        # Announce player left
        self.factory.send_chat_all(u"\u00a7e%s has left." % self.display_name)
        self.factory.world.remove_entity(self.eid,True)


    def packet_plugin_message(self, buff):
        channel = buff.unpack_string()
        if channel == "MC|Brand":
            print self.display_name + " Conencted using a " + buff.unpack_string() + " client."
        buff.discard()

    def packet_chat_message(self, buff):
        p_text = buff.unpack_string()
        print "<" + self.display_name + ">", p_text
        if p_text.startswith("/"):
            command = p_text.split(" ")
            if command[0] == "/stop":
                self.factory.world.saveWorld()
                self.factory.send_kick_all("Server Closed!")
            elif command[0] == "/save":
                self.factory.world.saveWorld("../")
                self.factory.send_chat_all("World Saved!")
            elif command[0] == "/getblock":
                block = self.factory.world.getBlock(int(command[1]),int(command[2]),int(command[3]))
                self.send_packet("chat_message",self.buff_type.pack_chat("Block at"+command[1]+" "+command[2]+" "+command[3]+" is "+blocks.id_block[block[0]]+" with metadata of "+str(block[1]))+self.buff_type.pack('B',0))

        else:
            self.factory.send_chat_all("<%s> %s" % (self.display_name, p_text))

class PyMineServerFactory(ServerFactory):
    protocol = PyMineServerProtocol
    def LoadWorld(self,name='world'):
        self.world = world.World(name)
        try:
            self.world.loadSpawn()
        except Exception as e:
            print(e)
            print("Unable to load world: "+name)
            print("Generating new world!")
            self.world.genWorld()
            self.world.saveWorld()

    def send_chat_all(self, message):
        data = self.buff_type.pack_chat(message) + self.buff_type.pack('B', 0)

        for player in self.players:
            player.send_packet("chat_message", data)
    def send_kick(self,message,player):
        message = self.buff_type.pack_chat(message)
        player.send_packet("disconnect",message)
        player.close()

    def send_kick_all(self,message):
        for x in self.players:
            self.send_kick(message,x)

