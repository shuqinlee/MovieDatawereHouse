# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import scrapy
from scrapy import signals
import random 
import logging

class TutorialSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

"""
class ProxyMiddleWare(object):  
    """docstring for ProxyMiddleWare"""  
    def process_request(self,request, spider):  
        '''add proxy for request'''  
        proxy = self.get_random_proxy()  
        logging.info("Request IP: %s", proxy)
#        print("this is request ip:"+proxy)  
        request.meta['proxy'] = proxy   
  
  
    def process_response(self, request, response, spider):  
        '''resolve response'''  
        # if response status is not 200, randomize IP again 
        if response.status != 200:  
            proxy = self.get_random_proxy()  
            logging.info("Request IP: " + proxy)
            # add proxy for current request  
            request.meta['proxy'] = proxy   
            return request  
        return response  
  
    def get_random_proxy(self):  
        '''randomize proxy from txt file'''  
        while 1:  
            with open('proxies.txt', 'r') as f:  
                proxies = f.readlines()  
            if proxies:  
                break  
            else:  
                time.sleep(1)  
        proxy = random.choice(proxies).strip()  
        return proxy
        """