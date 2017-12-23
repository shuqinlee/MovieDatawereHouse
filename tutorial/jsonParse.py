#!/usr/bin/python

import json

jpath = "/Users/shuqinlee/Documents/Programming/Python/Scrapy/tutorial/amazon1222_02.json"
f = open(jpath, 'r')
jobj = json.load(f)
for o in jobj:
	if "genres" in o:
		if o["ptype"] == 0:
			print o["genres"]