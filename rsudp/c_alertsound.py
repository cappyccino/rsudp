import sys, os
from threading import Thread
from rsudp import printM
import subprocess
from tempfile import NamedTemporaryFile
try:
	from pydub.playback import play, PLAYER
	pydub_exists = True
except ImportError:
	pydub_exists = False


class AlertSound(Thread):
	"""
	A sub-consumer class that simply prints incoming data to the terminal.
	This is enabled by setting the "printdata" > "enabled" parameter to `true`
	in the settings file. This is more of a debug feature than anything else,
	meant as a way to check that data is flowing into the port as expected.


	"""

	def __init__(self, sound=False, q=False):
		"""
		Initialize the process
		"""
		super().__init__()
		self.sender = 'AlertSound'
		self.alarm = False
		self.alive = True
		self.sound = sound

		if q:
			self.queue = q
		else:
			printM('ERROR: no queue passed to the consumer thread! We will exit now!', self.sender)
			sys.stdout.flush()
			self.alive = False
			sys.exit()

		printM('Starting.', self.sender)

	def _play_quiet(self):
		'''
		if FFPlay is the player, suppress printed output
		'''
		with NamedTemporaryFile("w+b", suffix=".wav") as f:
			self.sound.export(f.name, "wav")
			devnull = open(os.devnull, 'w')
			subprocess.call([PLAYER,"-nodisp", "-autoexit", "-hide_banner", f.name],stdout=devnull, stderr=devnull)

	def _play(self):
		if 'ffplay' in PLAYER:
			self._play_quiet()
		else:
			play(self.sound)

	def run(self):
		"""
		Reads data from the queue and print to stdout
		"""
		while True:
			d = self.queue.get()
			self.queue.task_done()
			if 'TERM' in str(d):
				self.alive = False
				printM('Exiting.', self.sender)
				sys.exit()
			elif 'ALARM' in str(d):
				printM('Playing alert sound...', sender=self.sender)
				if self.sound and pydub_exists:
					self._play()

				

		self.alive = False