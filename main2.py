import time

YELLOW_THRESHOLD = 7
ORANGE_THRESHOLD = 14
RED_THRESHOLD = 28

class Survivor:
	def __init__(self):
		self.xp = 0
		self.xp_level = "blue"
  
	def gain_xp(self, amount: int):
		self.xp += amount
		if self.xp >= YELLOW_THRESHOLD and self.xp_level == "blue":
			self.yellow()
		if self.xp >= ORANGE_THRESHOLD and self.xp_level == "yellow":
			self.orange()
		if self.xp >= RED_THRESHOLD:
			self.red()
	
	def yellow(self):
		self.xp_level = "yellow"

	def orange(self):
		self.xp_level = "orange"

	def red(self):
		self.xp_level = "red"

class TurnManager:
	def __init__(self, total: int, loop: bool = False):
		self.start = True
		self.turn = 0
		self.total = total
		self.loop = loop
	
	def get_turn(self):
		return self.turn

	def free_turn(self):
		return self.turn

	def next_turn(self):
		if self.start == True:
			self.turn -= 1
			self.start = False

		self.turn += 1
		if self.turn >= self.total:
			if self.loop == True:
				self.turn = 0
			else:
				return None
		
		return self.turn

four_turns = TurnManager(4, False)
four_turns_loop = TurnManager(4, True)

global_turns = ["surv", "zomb", "spawn", "end"]
global_turn_manager = TurnManager(len(global_turns), True)

while True:
    print(global_turns[global_turn_manager.next_turn()])
    time.sleep(0.4)