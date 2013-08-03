# -*- encoding: utf-8 -*-
import argparse
import os, re, sys
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
		category = None
		for node in lang.childNodes:
			if node.nodeType == node.COMMENT_NODE:
				category = node.data
			if node.nodeName.upper() == 'ROW':
				tag = node.getAttribute('Tag')
				text = u''.join(node.getElementsByTagName('Text')[0].firstChild.data.strip())
				gender = None
				plurality = None
				ignore = False
				for subnode in node.childNodes:
					if subnode.nodeName.upper() == 'GENDER':
						gender = subnode.firstChild.data.strip()
					if subnode.nodeName.upper() == 'PLURALITY':
						plurality = subnode.firstChild.data.strip()
					if subnode.nodeType == subnode.COMMENT_NODE:
						if 'ignore' in subnode.data:
							ignore = True
				tmp.update({tag: {'Text': text, 'category': category, 'Gender': gender, 'Plurality': plurality, 'ignore': ignore}})
		return tmp
	
	# This combines the subpath of the Civilization V directory and adds the language.
	def pathjoin(self, paths, lang=None):
		path = os.path.join(paths[0], paths[1])
		for p in paths[2:]:
			path = os.path.join(path, p)
		if lang==None:
			lang = self.orglang
		path = os.path.join(path, lang)
		return path
	
	def getorgmessages(self):
		print "Loading original messages...",
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
			srcpath = os.path.join(self.civ5dir, self.pathjoin(paths[comp]))
			if not os.path.exists(srcpath):
				srcpath = os.path.join(self.civ5dir, self.pathjoin(paths[comp], self.orglang.upper()))
				if not os.path.exists(srcpath):
					continue
			for root, dirs, files in os.walk(srcpath):
				for f in files:
					if re.match('Civ5.*\.xml', f, re.I):
						ntmp = self.parsexmlfile(os.path.join(root, f))
						tmp.update(ntmp)
		print "done."
		return tmp
	
	def getcurmessages(self):
		# Take a backup.
		f = open(self.outputfile + '.bak.xml', 'w')
		w = open(self.outputfile, 'r')
		f.write(w.read())
		f.close()
		w.close()
		print "Loading new messages...",
		dom = parse(self.outputfile)
		language = dom.getElementsByTagName('Languages')[0].getElementsByTagName('Row')[0]
		tablename = language.getElementsByTagName('TableName')[0].firstChild.data
		print "done."
		return self.parsexmlfile(self.outputfile, tablename)
	
	def msgssort(self, x, y):
		catx = x["category"] if x["category"] != None else ""
		caty = y["category"] if y["category"] != None else ""
		return 1 if catx>caty else -1
	
	def save(self, messages):
		dom = parse(self.outputfile)
		table = dom.getElementsByTagName('Table')[0]
		languages = dom.getElementsByTagName('Languages')[0]
		
		language = dom.createElement(languages.getElementsByTagName('TableName')[0].firstChild.data)
		
		smsgs = []
		for tag in messages:
			el = messages[tag]
			el.update({"Tag": tag})
			smsgs.append(el)
		
		smsgs.sort(self.msgssort)
		
		curcategory = ''
		for el in smsgs:
			if el['category'] != None and el['category'].strip() != curcategory:
				curcategory = el['category'].strip()
				language.appendChild(dom.createComment(curcategory))
			row = dom.createElement('Row')
			row.attributes['Tag'] = el["Tag"]
			if el['ignore']:
				row.appendChild(dom.createComment('ignore'))
			text = dom.createElement('Text')
			text.appendChild(dom.createTextNode(el['Text']))
			row.appendChild(text)
			if el['Gender'] != None:
				gender = dom.createElement('Gender')
				gender.appendChild(dom.createTextNode(el['Gender']))
				row.appendChild(gender)
			if el['Plurality'] != None:
				plurality = dom.createElement('Plurality')
				plurality.appendChild(dom.createTextNode(el['Plurality']))
				row.appendChild(plurality)
			language.appendChild(row)
		
		while dom.firstChild != None:
			dom.removeChild(dom.firstChild)
		
		gamedata = dom.createElement('GameData')
		
		gamedata.appendChild(table)
		gamedata.appendChild(languages)
		gamedata.appendChild(language)
		
		dom.appendChild(gamedata)
		
		print len(dom.getElementsByTagName('Row'))
		
		f = open(self.outputfile, 'w')
		f.write(dom.toprettyxml(u'  ', u'\n', 'UTF-8'))
		f.close()
	
	def comparisoninteract(self, orgmsgs, curmsgs):
		for tag in curmsgs:
			if curmsgs[tag]['Text'] == orgmsgs[tag]['Text'] and not curmsgs[tag]['ignore']:
				print tag
				print "Category: %s" % curmsgs[tag]['category'],
				if orgmsgs[tag]['category'] != curmsgs[tag]['category']:
					print ' (%s)' % orgmsgs[tag]['category']
				else:
					print
				if orgmsgs[tag]['Gender'] != None:
					print "Gender: %s" % orgmsgs[tag]['Gender']
				if orgmsgs[tag]['Plurality'] != None:
					print "Plurality: %s" % orgmsgs[tag]['Plurality']
				print
				print orgmsgs[tag]['Text']
				print
				print ':i to ignore, blank to skip, :q to quit and save, :s to just save'
				t = raw_input('Translate: ').decode(sys.stdin.encoding)
				if t.lower() == ':i':
					curmsgs[tag]['ignore'] = True
				elif t.lower() == '':
					continue
				elif t.lower() == ':q':
					self.save(curmsgs)
					return False
				elif t.lower() == ':s':
					self.save(curmsgs)
				else:
					curmsgs[tag]['Text'] = u"".join(t)
					if orgmsgs[tag]['Gender'] != None:
						t = raw_input('Translate gender: ')
						if t.strip() == '':
							curmsgs[tag]['Gender'] = None
						else:
							curmsgs[tag]['Gender'] = t
					if orgmsgs[tag]['Plurality'] != None:
						t = raw_input('Translate plurality: ')
						if t.strip() == '':
							curmsgs[tag]['Plurality'] = None
						else:
							curmsgs[tag]['Plurality'] = t
					print curmsgs[tag]
		self.save(curmsgs)
		print 'Messages run through...'
	
	def run(self):
		if self.comparison:
			orgmessages = self.getorgmessages()
			curmessages = self.getcurmessages()
			self.comparisoninteract(orgmessages, curmessages)
		else:
			print "Not implemented."
			return
	
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
