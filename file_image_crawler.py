## web_crawler to extract the composer name
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import platform
import scrapy
from scrapy.crawler import CrawlerProcess
import json

class JsonWriterPipeline(object):
    
    def open_spider(self, spider):
        self.file = open('composerresult.jl', 'w')
        
    def close_spider(self, spider):
        self.file.close()
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    
##linked in scrapy webpage
class LinkedInAnonymousSpider(scrapy.Spider):
      name = "linkedin_anonymous"
      allowed_domains = ["linkedin.com"]
      start_urls = []
    
      base_url = "https://www.linkedin.com/pub/dir/?first=%s&last=%s&search=Search"
        
      def __init__(self, input=None, first=None, last=None):
         self.input = input
         self.first = first
         self.last  = last
        
      def start_requests(self):
         if self.first and self.last:
                url = self.base_url % (self.first, self.last)
                yield self.make_requests_from_url(url)
         elif self.input:
                i = 0
                for line in open(self.input, 'r').readlines():
                    i += 1
                    if line.strip():
                        t = line.split("\t")
                        name = t[0]
                        parts = [n.strip() for n in name.split(' ')]
                        last = parts.pop()
                        first = " ".join(parts)
                        
                        if first and last:
                            url = self.base_url % (first, last)
                            yield self.make_requests_from_url(url)
                            
      def parse(self, response):
          if response.xpath('//div[@class="profile-overview-content"]').extract():
             yield scrapy.Request(response.url, callback=self.parse_full_profile_page)
          else:
             for sel in response.css('div.profile-card'):
                    url = sel.xpath('./*/h3/a/@href').extract()[0]
                    yield scrapy.Request(url, callback=self.parse_full_profile_page)
                    
# firstname = ['Hasan', 'James']
# lastname = ['Arslan', 'Bond']
# for a in range(len(firstname)):
#     settings = get_project_settings()
#     crawler = CrawlerProcess(settings)
#     spider  = LinkedInAnonymousSpider()
#     crawler.crawl(spider, [], firstname[a], lastname[a])
#     crawler.start()
        
    
class Setspider(scrapy.Spider):
     name = "composer"
     start_urls = ['https://en.wikipedia.org/wiki/List_of_piano_composers']
     
     custom_settings = {
         'ITEM_PIPELINES':{'__main__.JsonWriterPipeline': 1},
         'FEED_FORMAT':'json',
         'FEED_URI': 'composerresult.json'
     }

     def parse(self, response):
         keydict = []
         for key in response.css('span.mw-headline::text').extract():
             keydict.append(key)
         print(keydict)
         for i, composer in enumerate(response.css('div.div-col.columns.column-width>ul')):  
             if keydict[i] == '20th century':
                print(keydict[i+1])
                # additional 
                for sub_composer in response.css('table.wikitable.sortable>tbody'):
                    composer0 = sub_composer.css('span.fn a ::text').extract()
                    linkage0  = sub_composer.css('span.fn a::attr(href)').extract()
                print(composer0)
                yield{
                    keydict[i]: [{'composer': composer0[k], 'linkage': linkage0[k]} for k in range(len(composer0))]
                }
                
                composer1 = composer.css('a ::text').extract()
                linkage1  = composer.css('a::attr(href)').extract()
                yield{
                    keydict[i+1]: [{'composer': composer1[m], 'linkage': linkage1[m]} for m in range(len(composer1))]
                   
                }
                
             else:
                composer2 = composer.css('a ::text').extract()
                linkage2  = composer.css('a::attr(href)').extract()
                yield{
                    keydict[i]: [{'composer': composer2[n], 'linkage': linkage2[n]} for n in range(len(composer2))]
                    
                }
    
process = CrawlerProcess()
process.crawl(Setspider)
process.start()

