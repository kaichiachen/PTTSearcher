# coding=UTF-8
from __future__ import absolute_import
import logging
from datetime import datetime
import scrapy
from scrapy.http import FormRequest
from ptt.items import PttItem
from scrapy.conf import settings
import telepot


class ColorfulLog:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	@staticmethod
	def info(text):
		logging.info(ColorfulLog.OKGREEN + text + ColorfulLog.ENDC)

	@staticmethod
	def warning(text):
		logging.warning(ColorfulLog.WARNING + text + ColorfulLog.ENDC)

	@staticmethod
	def debug(text):
		logging.debug(ColorfulLog.OKBLUE + text + ColorfulLog.ENDC)

	@staticmethod
	def error(text):
		logging.error(ColorfulLog.FAIL + text + ColorfulLog.ENDC)

class PTTSpider(scrapy.Spider):
	name = 'ptt'
	allowed_domains = ['ptt.cc']
	start_urls = ('https://www.ptt.cc/bbs/' + settings.get('BOARD') +'/index.html', )

	DEBUG = False
	EXPIRED = 0
	MAX_RETRY = 1
	_pages = 0
	_retries = 0

	def __init__(self):
		date = settings.get('STOP_DATE', {'year': 2000, 'month': 1, 'day': 1})
		self.year = date['year']
		self.month = date['month']
		self.day = date['day']

		self.parsing_year = datetime.today().year
		self.parsing_month = datetime.today().month
		self.parsing_day = datetime.today().day

		# show cralwer log or not
		logging.getLogger('scrapy').propagate = PTTSpider.DEBUG

		if settings.get('TELE_BOT_TOKEN') is not None:
			self.bot = telepot.Bot(settings.get('TELE_BOT_TOKEN'))

		ColorfulLog.info('crawl the data until %d-%d-%d' % (self.year, self.month, self.day,))

	def parse(self, response):
		if len(response.xpath('//div[@class="over18-notice"]')) > 0:

			# auto click over18 notice page
			if self._retries < PTTSpider.MAX_RETRY:
				self._retries += 1
				ColorfulLog.warning('retry %d times...' % (self._retries,))
				yield FormRequest.from_response(response,
				                                formdata={'yes': 'yes'},
				                                callback=self.parse)
			else:
				ColorfulLog.warning('You cannot pass the age confirmation')

		else:
			self._pages += 1
			ColorfulLog.info('Page: ' + str(self._pages))
			ColorfulLog.info('Cralwer is parsing article in date: %d-%d-%d' % (self.parsing_year, self.parsing_month, self.parsing_day) )
			
			# check if crawler has detected expired article for 5 times
			if PTTSpider.EXPIRED < 5:
			    for href in response.css('.r-ent > div.title > a::attr(href)'):
			        url = response.urljoin(href.extract())
			        yield scrapy.Request(url, callback=self.parse_post)


			    next_page = response.xpath(
			        '//div[@id="action-bar-container"]//a[contains(text(), "' + u'上頁' + '")]/@href')
			    if next_page:
			        url = response.urljoin(next_page[0].extract())
			        yield scrapy.Request(url, self.parse)
			    else:
			        ColorfulLog.warning('Page is end')
			else:
				try:
					self.bot.sendMessage(settings.get('SEND_ID'), 'PTT: ' + settings.get('BOARD') +'爬完資料了')
				except:
					pass
				ColorfulLog.debug('Finish crawling!')

	def parse_post(self, response):
		item = PttItem()
		if len(response.xpath('//meta[@property="og:title"]/@content')) == 0:
			return

		item['title'] = response.xpath(
		    '//meta[@property="og:title"]/@content')[0].extract()
		item['author'] = response.xpath(
		    '//div[@class="article-metaline"]/span[text()="'+ u'作者' +'"]/following-sibling::span[1]/text()')[
		        0].extract().split(' ')[0]
		datetime_str = response.xpath(
			'//div[@class="article-metaline"]/span[text()="' + u'時間' + '"]/following-sibling::span[1]/text()')[
		        0].extract()

		date = datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %Y')
		self.parsing_year = date.year
		self.parsing_month = date.month
		self.parsing_day = date.day

		if date < datetime(self.year, self.month, self.day):
			PTTSpider.EXPIRED += 1
		else:
			PTTSpider.EXPIRED = 0

		item['date'] = date

		item['content'] = ''
		for line in response.xpath('//div[@id="main-content"]/text()'):
			item['content'] += line.extract()

		comments = []
		for comment in response.xpath('//div[@class="push"]'):
		    push_user = comment.css('span.push-userid::text')[0].extract()
		    push_content = comment.css('span.push-content::text')[0].extract()

		    comments.append({'user': push_user,
		                     'content': push_content})

		item['comments'] = comments
		item['url'] = response.url

		yield item