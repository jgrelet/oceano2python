"""
code roscop
"""

import csv, shelve,sys

# class roscop 
# ------------
class Roscop:

  # constructor with values by default
	def __init__(self, file):
		self.file = file
		
	# call by print()
	def __repr__(self):
		return "class Roscop, file: {}".format(self.file)

	# read code roscop file
	def read(self):
		print("Code roscop file: %s" % self.file)
		with open(self.file, 'rt') as f:
			reader = csv.DictReader(f, delimiter=';')
			for row in reader:
				print("%s : %s : %s : %s : %s" % (row['key'],  row['long_name'], 
				row['standard_name'], row['units'], row['format']))
		return

# for testing in standalone context
# ---------------------------------    
if __name__ == "__main__":
	from roscop import Roscop
	r = Roscop("code_roscop.csv")
	r.read()
	print(r)