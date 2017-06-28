from server.server import PyMineServerFactory
from twisted.internet import reactor

print("Starting Server!")
factory = PyMineServerFactory()
factory.online_mode=False
factory.max_players = 10
factory.motd = "Chibill's Python Server"
factory.listen('127.0.0.1', 25565)
factory.LoadWorld('world')
reactor.run()
