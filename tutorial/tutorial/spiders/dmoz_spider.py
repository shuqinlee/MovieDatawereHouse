#!/usr/bin/python

import scrapy
import logging
from tutorial.items import AmazonItem
import re
import os
			
class AmazonSpider(scrapy.Spider):
	name = "amazon"
	allowed_domains = ["amazon.com"]
	start_urls = [
		"https://www.amazon.com/dp/B0078V2LCY/"
	]
	processed = ""

	def parse(self, response):
		config = open("config.txt", 'r')
		l = config.readline()
		self.processed = re.findall('Processed:.*?\'(.*?)\'', l)[0]
		logging.info("Processed file configured: " + self.processed)
		processedFile = open(self.processed, 'a+')

		l = config.readline()
		inFile = re.findall('Input:.*?\'(.*?)\'', l)[0]
		f = open(inFile, "r")
		i = 0
		for line in f:
			i += 1
			print("*******" + str(i) + "******")
			if i == 100: break
			processedFile.seek(0, os.SEEK_SET)
			if line in processedFile.readlines(): # check whether processed
				continue
			nexturl = line.strip()
			yield scrapy.Request(nexturl, callback=self.parse_contents)
		f.close()


	def write_processed(self, response):
		url = response.url
		f = open(self.processed, "a")
		f.write(url + "\n")
		f.close()

	def parse_contents(self, response):
		item = AmazonItem()
		html = response.body.replace("\n", "")
		
		'''
		1. get "key word" and "content" in every field
		2. get each element in every field if exists
		3. save them
		'''
		KEYWORDS = {"genres", "studio", "director", "starring", "supporting_actors", "mpaa_rating", "desc", "runtime"}
		fieldPtn = r'<th class="a-span2">(.*?)</th>.*?<td>(.*?)</td>'
		fieldRes = re.findall(fieldPtn, html)
		fieldDict = dict()
		if fieldRes:
			pass
			for s in fieldRes:
				key = s[0].strip()
				content = s[1].strip()
				key = key.lower().replace(" ", "_")

				if key in KEYWORDS:
					fieldDict[key] = content
	#		print("******* field dict: *******")
	#		print fieldDict # {'Generes': '<a href=...></a>...'}

			for key, value in fieldDict.items():
				contentPtn = r'<a .*?>(.*?)</a>'
				contentRes = re.findall(contentPtn, value) 
				if not contentRes:
					fieldDict[key] = [value]
					item[key] = [value]
				else:
					contentRes = map(lambda x: x.strip(), contentRes)
					fieldDict[key] = contentRes
					item[key] = contentRes

#			print "******** FINAL RESULT TYPE 1 ********"
#			for key, value in fieldDict.items():
#				print(key)
#				print(value)
#				print("**************")
				
			# desc
			desc = str(response.xpath("//div[@class='dv-info']/div/p/text()").extract())
			item["desc"] = [str(desc)]
			
			# runtime
			timepat = re.compile(r"<dt>.*?Runtime:.*?</dt>.*?<dd>(.*?)</dd>")
			dl = response.xpath("//dl").extract()
			dl = dl[0].replace("\n", "")
			timeres = timepat.search(dl)
			if timeres:
				runtime = str(timeres.group(1).strip()) # the original was in unicode
				item["runtime"] = [runtime]
			
			# avg_rating
			avgRatingPtn = r'<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="(.*?)"> '
			avgRatingPtn = r'<span data-hook="rating-out-of-text" class="arp-rating-out-of-text">(.*?)</span>'
			avgRatingRes = re.findall(avgRatingPtn, html)
			fieldDict["average_rating"] = avgRatingRes
			item["average_rating"] = avgRatingRes
			
			item["ptype"] = 0
			self.write_processed(response)
			yield item
		else:
			KEYWORDS = {"actors", "directors", "producers", "writers", "language", "number_of_discs", "number_of_tapes", "rated", "studio", "dvd_release_date", "run_time", "average_rating"}
			# to-do
			detailsPat = r'<h2>Product details</h2>.*?<div class="content">.*?<ul>(.*?)</ul>.*?</div>'
			detailsRes = re.findall(detailsPat, html)
			if not detailsRes:
				return
#			print detailsRes
			fieldPat = r'<li>.*?<b>(.*?):.*?</b>(.*?)</li>'
			fieldRes = re.findall(fieldPat, detailsRes[0])
#			print("***** TYPE 2.2 *****")
#			print(fieldRes)
			for field in fieldRes:
				key = field[0].lower().replace(" ", "_").strip()
				
				val = field[1].strip()
#				print(key)
#				print(val)
				if key not in KEYWORDS:
					continue
#				print("***** TYPE 2.3 *****")
#				print field
				
				if key == "actors":
					key = "supporting_actors"
				elif key == "directors":
					key = "director"
				elif key == "run_time":
					key = "runtime"
				elif key == "rated":
					key = "mpaa_rating"
					ratePat = r'.*?<span class="a-size-small">(.*?)</span>.*?<span class="a-letter-space"></span>.*?</div>.*?</div>(.*$)'
					rateRes = re.search(ratePat, val)
					abbr = rateRes.group(1).strip()
					full = rateRes.group(2).strip()
					fieldDict[key] = [abbr + " (" + full + ")"]
					item[key] = [abbr + " (" + full + ")"]
					continue
				
				linkPat = r'<a.*?>(.*?)</a>'
				linkRes = re.findall(linkPat, val)
#				print linkRes
				if linkRes:
					fieldDict[key] = linkRes
				else:
#					print("***** TYPE 2.4 *****")
#					print(val)
					fieldDict[key] = [val.strip()]	
					item[key] = [val.strip()]
			avgRatingPtn = r'<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="(.*?)"> '
			avgRatingRes = re.findall(avgRatingPtn, html)
			fieldDict["average_rating"] = avgRatingRes
			item["average_rating"] = avgRatingRes
			item["ptype"] = 1
			self.write_processed(response)
			
#			print "******** FINAL RESULT TYPE 2 ********"
#			for key, value in fieldDict.items():
#				print(key)
#				print(value)
#				print("**************")
			yield item
