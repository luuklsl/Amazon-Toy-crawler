# -*- coding: utf-8 -*-
import sys
from datetime import datetime

import eventlet

import settings
from models import ProductRecord, retrieve
from helpers import make_request, log, format_url, enqueue_url, dequeue_url, enq_redis, deq_redis, page_save
from extractors import * # get_title, get_url, get_price, get_primary_img, price_on_page, get_category, get_bullets, get_product_description, manu_info

crawl_time = datetime.now()


settings.max_threads = 1 #override the setting locally for now

save_html = False


pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)


def begin_crawl():
    count = 0
    database_get = retrieve()
    print len (database_get)
    print database_get
    for entry in database_get:
        enq_redis("products", (entry[0],entry[2]))
        # enq_redis("products", entry[])
        print entry[2]
        count += 1
    log("Enqueued a total of {} products".format(count))


    # explode out all of our category `start_urls` into subcategories
    # with open(settings.start_file, "r") as f:
    #     for line in f:
    #         line = line.strip()
    #         if not line or line.startswith("#"):
    #             continue  # skip blank and commented out lines

    #         #page, html = make_request(line)
    #         count = 0

    #         # look for subcategory links on this page
    #         #subcategories = page.findAll("div", "bxc-grid__image")  # downward arrow graphics
    #         #subcategories = page.findAll("li", "acs-ln-special-link") # Only "Shop all" links
    #         #sidebar = page.find("div", "browseBox")
    #         #if sidebar:
    #         #    subcategories.extend(sidebar.findAll("li"))  # left sidebar
    #         enqueue_url(line)
    #         #for subcategory in subcategories:
            #    link = subcategory.find("a")
            #    if not link:
            #        continue
            #    link = link["href"]
            #    count += 1
            #    enqueue_url(link)
            #    print("Enqueued {}".format(link))

            #log("Found {} subcategories on {}".format(count, line))


def fetch_info():

    global crawl_time
    redis_entry = deq_redis('products')
    x = redis_entry.strip("()'")
    redis_list = x.split(", '")
    # for y in range(len(redis_list)):
    #     # redis_list[y] = 3
    #     print y
    #     redis_list[y].strip("'")
    x= int(redis_list[0])
    url = redis_list[1]
    # print x
    # # print redis_list
    # return
    if url is None:
        log("WARNING, no product found, is there still any queued?")
        return
    

    page, html = make_request(url)
    if not page: #if we dont find the page, we can't do anything with it
        return

    if save_html:
        print ("saving")
        page_save(html)

    # f = open("thing.html", 'r')
    # html = f.read()
    # f.close()

    # print page


    product_price = price_on_page(page)
    category = get_category(page.find("ul", "a-unordered-list a-horizontal a-size-small"))
    bullets = get_bullets(page.find("ul", "a-unordered-list a-vertical a-spacing-none"))
    manufacturer_inf = manu_info(page)
    # print ("found as manu_inf: {}".format(manufacturer_inf))
    product_description = get_product_description(page.find("div", "a-row feature"))
    specs = get_specs(page.find("table", "a-keyvalue prodDetTable"))
    
    # specs = TODO: expand upon this
        #possibly use a switch to expand upon this?
        # table


    # print product_description




    # for item in items[:settings.max_details_per_listing]:

    #     product_image = get_primary_img(item)
    #     if not product_image:
    #         log("No product image detected, skipping")
    #         continue

    #     product_title = get_title(item)
    #     product_url = get_url(item)
    #     product_price = get_price(item)

    #     product = ProductRecord(
    #         title=product_title,
    #         product_url=format_url(product_url),
    #         listing_url=format_url(url),
    #         price=product_price,
    #         primary_img=product_image,
    #         crawl_time=crawl_time

    #     )
    #     product_id = product.save()
    #     # download_image(product_image, product_id)

    # # add next page to queue
    # next_link = page.find("a", id="pagnNextLink")
    # if next_link:
    #     log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
    #     enqueue_url(next_link["href"])
    #     pile.spawn(fetch_listing)
    # retrieve()


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        log("Seeding the URL frontier with subcategory URLs")
        begin_crawl()  # put a bunch of subcategory URLs into the queue

    log("Beginning crawl at {}".format(crawl_time))
    # [pile.spawn(fetch_listing) for _ in range(settings.max_threads)]
    # pool.waitall()
    fetch_info()
