import scrapy
from scrapy import Request
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class WebSpider(scrapy.Spider):
    spread_sheet_name = 'my_sheet'
    sheet_name = 'Sheet1'
    json_file_path = 'C:\\Users\\Farhan\\Downloads\\gspread-357308-79fb65e8a2a6.json'

    name = 'web'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']
    custom_settings = {'ROBOTSTXT_OBEY': False, 'LOG_LEVEL': 'INFO',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
                       'RETRY_TIMES': 5,
                       # 'FEED_URI': 'wesitedetail.csv',
                       # 'FEED_FORMAT': 'csv',
                       }

    def start_requests(self):
        urls = [data['url'] for data in self.read_google_sheet()]
        for url in urls:
            url_index = urls.index(url)
            yield Request(url=url, callback=self.parse, meta={'url_index': url_index})

    def parse(self, response):
        url_index = response.meta['url_index'] + 2
        try:
            title = response.xpath("//meta[@property='og:title']/@content").get().strip()
        except:
            title = ''
        try:
            description = response.xpath("//meta[@property='og:description']/@content").get().strip().replace('\n', '')
        except:
            description = ''
        creds = self.read_cred()
        client = gspread.authorize(creds)
        spread_sheet = client.open(self.spread_sheet_name).worksheet(self.sheet_name)
        range = f"A{url_index}:C{url_index}"
        data = [response.url, title, description]
        spread_sheet.batch_update([{"range": range, "values": [data]}])

    def read_google_sheet(self):
        creds = self.read_cred()
        client = gspread.authorize(creds)
        spread_sheet = client.open(self.spread_sheet_name).worksheet(self.sheet_name)
        request_data = spread_sheet.get_all_records()
        return request_data

    def read_cred(self):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.json_file_path, scopes)
        return creds
