import re

def run():
	f = open('Language_Danish.xml')
	tags = {}
	for line in f.readlines():
		if re.match('.*<Row.+Tag=', line, re.I):
			tag = re.sub(r'.*<Row.+Tag="([^"]+)".*>.*', r'\1', line, re.I).strip()
			try:
				t = tags[tag]
				print tag
				print line
			except KeyError:
				tags.update({tag: True})

run()