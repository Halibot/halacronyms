import string as boo
import random
import time
import threading

STARTING = 1
GATHERING = 2
VOTING = 3
ENDING = 4
STOP = 5

class Answer():
	def __init__(self, user, string):
		self.user = user
		self.string = string
		self.votes = 0

class Game():

	state = STARTING
	answers = []
	voted = []
	thread = None
	wait = None

	def __init__(self, xmpp, room):
		self.xmpp = xmpp
		self.room = room
		self.thread = threading.Thread(target=self.start)
		self.thread.start()

	def start(self):
		self.state = STARTING
		self.answers = []
		self.voted = []

		self._request()
		if self.wait == STOP:
			print("Thread terminating")
			return

		self._post()
		if self.wait == STOP:
			print("Thread terminating")
			return

		self._vote()
		if self.wait == STOP:
			print("Thread terminating")
			return

		self._reveal()
		print("Thread terminating")

	def stop(self):
		self.wait = STOP

	def msg(self, user, ans):
		if self.state == GATHERING:
			if user in [a.user for a in self.answers]:
				self.xmpp.sendMsg(self.room + "/" + user, "You already entered!")
				return

			self.answers.append(Answer(user,ans))
			self.xmpp.sendGroupMsg(self.room, "Received {} responses...".format(len(self.answers)))
			self.xmpp.sendMsg(self.room + "/" + user, "Received your entry!")

		elif self.state == VOTING:
			if user in self.voted:
				self.xmpp.sendMsg(self.room + "/" + user, "You already voted!")
				return
			try:
				if int(ans) > len(self.answers) or int(ans) < 0:
					return
			except:
				pass
			
			self.voted.append(user)
			self.answers[int(ans)].votes += 1	
			self.xmpp.sendMsg(self.room + "/" + user, "Received your vote!")

	def _request(self):
		pass

	def _post(self):
		r = random.randint(3, 6)
		foo = ""

		for i in range(r):
			foo += boo.ascii_uppercase[random.randint(0,25)]

		self.xmpp.sendGroupMsg(self.room, "The string is '{}'. You have 120 seconds, send entries to {}. Good luck!".format(foo, self.xmpp.jid))
		self.state = GATHERING
		self._wait(120)

	def _vote(self):
		self.state = VOTING
		self.xmpp.sendGroupMsg(self.room, "Submitting period is over. Here are the strings, send the number of your vote to {}.\n{}".format(self.xmpp.jid,"\n".join(["{}. {}".format(i,self.answers[i].string) for i in range(len(self.answers))])))
		# Do nothing, wait for votes to collect
		self._wait(60)

	def _reveal(self):
		self.state = ENDING

		if len(self.voted) == 0:
			self.xmpp.sendGroupMsg(self.room, "There were no votes, so I win.")
			return

		blerr = sorted(self.answers, key=lambda x: x.votes)[0]
		winner = blerr.user
		ans = blerr.string

		self.xmpp.sendGroupMsg(self.room, "The winner is '{}' with '{}'. Hooray.".format(winner, ans))
		# TODO: Signal to remove this game object

	def _wait(self, sec):
		start = time.clock()
		while not self.wait:
			if (time.clock() - start) >= sec:
				return False
	
		ret = False
	
		# Add more interrupts if needed
		if self.wait == STOP:
			ret = True
	
		return ret
