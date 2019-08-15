#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author:zj time: 2019/7/23 9:08
import os
import re
import requests
import threading
from lxml import etree
from urllib import request
from queue import Queue

class Producess(threading.Thread):
	headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'
		}
	def __init__(self, page_queue, img_queue, *args, **kwargs):
		super(Producess, self).__init__(*args, **kwargs)
		self.page_queue = page_queue
		self.img_queue = img_queue

	def run(self):
		while True:
			if self.page_queue.empty():
				break
			url = self.page_queue.get()
			self.parse_images(url)

	def parse_images(self, url):
		response = requests.get(url, headers=self.headers)
		text = response.text
		html = etree.HTML(text)
		images = html.xpath('//div[contains(@class, "page-content")]//img[@class!="gif"]')
		for image in images:
			img_url = image.get('data-original')
			suffix = os.path.splitext(img_url)[1]
			alt = image.get('alt')
			alt = re.sub(r"[\.\?？，②！*!~]", '', alt)
			filename = alt + suffix
			self.img_queue.put((img_url, filename))


class Consumer(threading.Thread):
	def __init__(self, page_queue, img_queue, *args, **kwargs):
		super(Consumer, self).__init__(*args, **kwargs)
		self.page_queue = page_queue
		self.img_queue = img_queue

	def run(self):
		while True:
			if self.img_queue.empty() and self.page_queue.empty():
				break
			img_url, filename = self.img_queue.get()
			request.urlretrieve(img_url, 'images/'+filename)

def main():
	page_queue = Queue(100)
	img_queue = Queue(1000)
	for i in range(1, 101):
		url = 'http://www.doutula.com/photo/list/?page=%d'%i
		page_queue.put(url)

	for x in range(5):
		t = Producess(page_queue, img_queue)
		t.start()

	for x in range(5):
		t = Consumer(page_queue, img_queue)
		t.start()


if __name__ == '__main__':
	main()