import scrapy
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from config import HEAD_URL, ALLOWED_DOMAINS

class ViolinSpider(scrapy.Spider):
    name = "violins"
    allowed_domains = [ALLOWED_DOMAINS]
    head_url = HEAD_URL
    start_urls = [
    HEAD_URL + "/collections/beginner-violins",
    HEAD_URL + "/collections/intermediate-violins",
    HEAD_URL + "/collections/advanced-violins",
    HEAD_URL + "/collections/professional-violins",
    HEAD_URL + "/collections/electric-violins",
    HEAD_URL + "/collections/ex-rental-violins",
    HEAD_URL + "/collections/second-hand-violins",
    ]
    max_pages = 10
    collected_data = []  # The data is keep on a list to be processed on a dataframe
    page_count = {}

    def start_requests(self):
        for url in self.start_urls:
            self.page_count[url] = 1
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"category": url.split("/")[-1].replace("-", " ")},
            )

    def parse(self, response):
        # Identify the current page by the category
        category = response.meta["category"]
        base_url = response.url.split("?")[0]

        products = response.css("div.productitem")
        for product in products:
            item = {
                "name": product.css("h2.productitem--title a::text")
                .get(default="")
                .strip(),
                "price": product.css("div.price__current span.money::text")
                .get(default="")
                .strip(),
                "average_rating": product.css("div.jdgm-prev-badge").attrib.get(
                    "data-average-rating", None
                ),
                "number_of_reviews": product.css("div.jdgm-prev-badge").attrib.get(
                    "data-number-of-reviews", None
                ),
                "stock": product.css(
                    "span.product-stock-level__text div.product-stock-level__badge-text::text"
                )
                .get(default="")
                .strip(),
                "description": product.css("div.productitem--description p::text")
                .get(default="")
                .strip(),
                "image": product.css("img.productitem--image-primary").attrib.get(
                    "src", ""
                ),
                "category": category,
            }
            self.collected_data.append(item)
            yield item

        # Verify the next page
        if self.page_count[base_url] < self.max_pages:
            next_page = response.css("li.pagination--next a::attr(href)").get()
            if next_page:
                self.page_count[base_url] += 1
                next_page_url = self.head_url + next_page
                yield scrapy.Request(
                    url=next_page_url, callback=self.parse, meta={"category": category}
                )
        else:
            self.page_count[base_url] = 1