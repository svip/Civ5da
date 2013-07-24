import argparse
import os, re
from xml.dom.minidom import parse

class Interact(object):
	outputfile = ''
	civ5dir    = ''
	comparison = False
	orglang    = 'en_US'
	
	def parsexmlfile(self, path, tablename=None):
		if tablename == None:
			tablename = 'Language_'+self.orglang
		tmp = {}
		dom = parse(path)
		lang = dom.getElementsByTagName(tablename)[0]
		for node in lang.childNodes:
			if node.nodeName.upper() == 'ROW':
				tag = node.getAttribute('Tag')
				text = node.getElementsByTagName('Text')[0].firstChild.data
				tmp.update({tag: text})
		return tmp
	
	# This combines the subpath of the Civilization V directory and adds the language.
	def pathjoin(self, paths):
		path = os.path.join(paths[0], paths[1])
		for p in paths[2:]:
			path = os.path.join(path, p)
		path = os.path.join(path, self.orglang)
		return path
	
	def getorgmessages(self):
		tmp = {}
		paths = {
			'vanilla': ['Assets', 'Gameplay', 'XML', 'NewText'], # Base game
			'DLC_01':  ['Assets', 'DLC', 'DLC_01', 'Gameplay', 'XML', 'Text'], # Mongolia DLC
			'DLC_02':  ['Assets', 'DLC', 'DLC_02', 'Gameplay', 'XML', 'Text'], # Spain & Inca DLC
			'DLC_03':  ['Assets', 'DLC', 'DLC_03', 'Gameplay', 'XML', 'Text'], # Polynesia DLC
			'DLC_04':  ['Assets', 'DLC', 'DLC_04', 'Gameplay', 'XML', 'Text'], # Denmark DLC
			'DLC_05':  ['Assets', 'DLC', 'DLC_05', 'Gameplay', 'XML', 'Text'], # Korea DLC
			'DLC_06':  ['Assets', 'DLC', 'DLC_06', 'Gameplay', 'XML', 'Text'], # Wonders of the Ancient World DLC
			'DLC_Deluxe': ['Assets', 'DLC', 'DLC_Deluxe', 'Gameplay', 'XML', 'Text'], # Babylon DLC
			'Expansion':  ['Assets', 'DLC', 'Expansion', 'Gameplay', 'XML', 'Text'],  # Gods and Kings expansion
			'Expansion2': ['Assets', 'DLC', 'Expansion2', 'Gameplay', 'XML', 'Text'], # Brave New World expansion
		}
		# The order to load the paths in, so that text messages from the newest expansion/dlcs overwrites the older
		# messages.
		pathorder = ['vanilla', 'DLC_Deluxe', 'DLC_01', 'DLC_02', 'DLC_03', 'DLC_04', 'DLC_05', 'DLC_06', 'Expansion', 'Expansion2']
		for comp in pathorder:
			# Verify that the directory exists (so people without some DLCs can use it).
			if not os.path.exists(os.path.join(self.civ5dir, self.pathjoin(paths[comp]))):
				continue
			for root, dirs, files in os.walk(os.path.join(self.civ5dir, self.pathjoin(paths[comp]))):
				for f in files:
					if re.match('Civ5.*\.xml', f, re.I):
						ntmp = self.parsexmlfile(os.path.join(root, f))
						tmp.update(ntmp)
		return tmp
	
	def getcurmessages(self):
		dom = parse(self.outputfile)
		language = dom.getElementsByTagName('Languages')[0].getElementsByTagName('Row')[0]
		tablename = language.getElementsByTagName('TableName')[0].firstChild.data
		return self.parsexmlfile(self.outputfile, tablename)
	
	def comparisoninteract(self, orgmsgs, curmsgs):
		for tag in curmsgs:
			if curmsgs[tag] == orgmsgs[tag]:
				print tag
				print curmsgs[tag]
				break
	
	def run(self):
		if self.comparison:
			orgmessages = self.getorgmessages()
			curmessages = self.getcurmessages()
			self.comparisoninteract(orgmessages, curmessages)
		else:
			print "Not implemented."
			return
		
		print self.outputfile
	
	def __init__(self):
		parser = argparse.ArgumentParser(description='Interactive translation.')
		parser.add_argument('outputfile', metavar='FILE', type=str, help='File being translated to.')
		parser.add_argument('--civ5', dest='civ5dir', help='Root directory of Civilization V')
		parser.add_argument('--originlang', dest='orglang', help='The original language to compare to (default: en_US)',
			default='en_US')
		args = parser.parse_args()
		
		self.outputfile = args.outputfile
		if args.civ5dir == '':
			self.comparison = False
		else:
			self.civ5dir = args.civ5dir
			self.comparison = True
		self.orglang = args.orglang
		
		self.run()

Interact()