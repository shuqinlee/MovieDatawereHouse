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
			line = str(line.strip())
#			if i == 100: break
			processedFile.seek(0, os.SEEK_SET)
			
			if str(line) + "\n" in processedFile.xreadlines(): # check whether processed
				print("processed!!")
				continue
			nexturl = line.strip()
			yield scrapy.Request(nexturl, callback=self.parse_contents)
		f.close()


	def write_processed(self, response):
		url = response.url
		f = open(self.processed, "a")
		f.write(url + "\n")
		f.close()

	def transfer_runtime(self, origin):
		pat = '(.*?) hour.*?(\d+) minute'
		res = re.search(pat, origin)
		minute = 0
		if res:
			hour = int(res.group(1))
			minute = int(res.group(2))
			minute = hour * 60 + minute
		else:
			pat = r"(\d+) minute"
			res = re.search(pat, origin)
			minute = int(res.group(1))
		return minute
	def transfer_rating(self, origin):
		ratingPtn = r"^(.*?) out"
		ratingRes = re.search(ratingPtn, origin)
		return float(ratingRes.group(1))
		
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
			for s in fieldRes:
				key = s[0].strip()
				content = s[1].strip()
				key = key.lower().replace(" ", "_")

				if key in KEYWORDS:
					fieldDict[key] = content

			for key, value in fieldDict.items():

				contentPtn = r'<a .*?>(.*?)</a>'
				contentRes = re.findall(contentPtn, value) 
					
				if not contentRes:
					fieldDict[key] = value
					item[key] = value
				else:
					contentRes = map(lambda x: x.strip(), contentRes)
					fieldDict[key] = contentRes
					item[key] = contentRes
				
			# desc
			desc = str(response.xpath("//div[@class='dv-info']/div/p/text()").extract())
			item["desc"] = str(desc)
			
			# runtime
			timepat = re.compile(r"<dt>.*?Runtime:.*?</dt>.*?<dd>(.*?)</dd>")
			dl = response.xpath("//dl").extract()
			dl = dl[0].replace("\n", "")
			timeres = timepat.search(dl)
			if timeres:
				runtime = str(timeres.group(1).strip()) # the original was in unicode
				item["runtime"] = self.transfer_runtime(runtime)
			
			# avg_rating
			avgRatingPtn = r'<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="(.*?)"> '
			avgRatingPtn = r'<span data-hook="rating-out-of-text" class="arp-rating-out-of-text">(.*?)</span>'
			avgRatingRes = re.findall(avgRatingPtn, html)
			item["average_rating"] = self.transfer_rating(avgRatingRes[0])
			item["ptype"] = 0
			item["oid"] = re.findall("https://www.amazon.com/dp/(.*?)/", response.url)[0]
			
			# name
			name = response.xpath("//h1[@id='aiv-content-title']/text()").extract()[0]
			name = name.replace("\n", "")
			name = name.strip()
			logging.info("Name: %s", name)
			item["name"] = name
			self.write_processed(response)
			yield item
		else:
			KEYWORDS = {"actors", "directors", "language", "rated", "studio", "dvd_release_date", "run_time", "average_rating", "amazon_best_sellers_rank"}

			detailsPat = r'<h2>Product details</h2>.*?<div class="content">.*?<ul>(.*?)</ul>.*?</div>'
			detailsRes = re.findall(detailsPat, html)
			if not detailsRes:
				return

			fieldPat = r'<li.*?>.*?<b>(.*?):.*?</b>(.*?)</li>'
			fieldRes = re.findall(fieldPat, detailsRes[0])

			for field in fieldRes:
				key = field[0].lower().replace(" ", "_").strip()
				val = field[1].strip()

				if key not in KEYWORDS:
					continue
				
				if key == "actors":
					key = "supporting_actors"
				elif key == "directors":
					key = "director"
				elif key == "run_time":
					key = "runtime"
					item["runtime"] = self.transfer_runtime(val)
					continue
				elif key == "amazon_best_sellers_rank":
					rankPat = r"#([1-9][\d]{0,2}[,\d{3}]*).*?in Movies"
					res = re.search(rankPat, val)
					if res:
						item["rank"] = int(res.group(1).replace(",", ""))
						continue
				elif key == "rated":
					key = "mpaa_rating"
					ratePat = r'.*?<span class="a-size-small">(.*?)</span>.*?<span class="a-letter-space"></span>.*?</div>.*?</div>(.*$)'
					rateRes = re.search(ratePat, val)
					if rateRes is None: 
						ratePat = r'<img.*?src=".*?".*?width=".*?".*?align=".*?".*?alt="(.*?)".*?height=".*?".*?border=".*?".*?>'
						rateRes = re.search(ratePat, val)
						item[key] = rateRes.group(1).lower().strip()
						fieldDict[key] = rateRes.group(1).lower().strip()
					else:
						abbr = rateRes.group(1).strip()
						full = rateRes.group(2).strip()
						fieldDict[key] = abbr + " (" + full + ")"
						item[key] = abbr + " (" + full + ")"
					continue
				
				linkPat = r'<a.*?>(.*?)</a>'
				linkRes = re.findall(linkPat, val)
				if linkRes:
					fieldDict[key] = linkRes
					item[key] = linkRes
				else:
					fieldDict[key] = val.strip()	
					item[key] = val.strip()
			# avgRating
			avgRatingPtn = r'<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="(.*?)"> '
			avgRatingRes = re.findall(avgRatingPtn, html)

			item["average_rating"] = self.transfer_rating(avgRatingRes[0]) 
			# ptype
			item["ptype"] = 1
			# oid
			item["oid"] = re.findall("https://www.amazon.com/dp/(.*?)/", response.url)[0]
			# name
			namePtn = r'<span.*?id="productTitle".*?class="a-size-large".*?>(.*?)<'
			nameRes = re.search(namePtn, html)
			item["name"] = nameRes.group(1).strip()
			
			
			self.write_processed(response)

			yield item
