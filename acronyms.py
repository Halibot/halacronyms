from module import XMPPModule
import game
import halutils

class Acronyms(XMPPModule):

	games = {}

	def deinit(self):
		for g in self.games.items():
			g[1].wait = STOP

	def recvMsg(self, msg):
		room = msg["from"].bare
		g = self.games.get(room)
		if not g or not g.thread.is_alive():
			return
		self.games[room].msg(str(msg["from"]).split("/")[1], msg["body"])

	def recvGroupMsg(self, msg):
		cmd, args = halutils.splitArgList(msg)
		if cmd != "!acronyms":
			return

		if len(args) == 0:
			return #TODO

		if args[0] == "start":
			if msg["mucroom"] in self.games and self.games[msg["mucroom"]].thread.is_alive():
				self.xmpp.reply(msg, "Game is already active")
				return
			self.games[msg["mucroom"]] = game.Game(self.xmpp, msg["mucroom"])
		elif args[0] == "stop":
			g = self.games.get(msg["mucroom"])
			if not g or not g.thread.is_alive():
				self.xmpp.reply(msg, "Game is not active...")
				return
			g.stop()
			self.xmpp.reply(msg, "Game stopped")
