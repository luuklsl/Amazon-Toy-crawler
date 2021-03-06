# -*- coding: utf-8 -*-
import sys
from datetime import datetime

import eventlet

import settings
from models import ProductRecord, retrieve, insert_extra
from helpers import make_request, log, format_url, enqueue_url, dequeue_url, enq_redis, deq_redis, page_save, smem
from extractors import * # get_title, get_url, get_price, get_primary_img, price_on_page, get_category, get_bullets, get_product_description, manu_info

crawl_time = datetime.now()


# settings.max_threads = 1 #override the setting locally for now

save_html = False


pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)


def begin_crawl():
    count = 0
    database_get = retrieve()
    print len (database_get)
    # print database_get
    for entry in database_get:
        enq_redis("products", (entry[0],entry[2]))
        # enq_redis("products", entry[])
        print entry[2]
        count += 1
    log("Enqueued a total of {} products".format(count))




def fetch_info():

    global crawl_time
    redis_entry = deq_redis('products')
    if not redis_entry:
        return
    x = redis_entry.strip("()'")
    redis_list = x.split(", '")
    x= int(redis_list[0])
    url = redis_list[1]
    
    if url is None:
        log("WARNING, no product found, is there still any queued?")
        return
    

    page, html = make_request(url, identifier=x)
    if page is None: #if we dont find the page, we can't do anything with it
        print "Page does not exists?"
        return


    if save_html:
        print ("saving")
        page_save(html)

    print "id is: {}".format(x)
    print url
    product_price = price_on_page(page)
    category = get_category(page.find("ul", "a-unordered-list a-horizontal a-size-small"))
    bullets = get_bullets(page.find("ul", "a-unordered-list a-vertical a-spacing-none"))
    manufacturer_inf = manu_info(page)
    # print ("found as manu_inf: {}".format(manufacturer_inf))
    product_description = get_product_description(page.find("div", "a-row feature"))
    specs = get_specs(page.find("table", "a-keyvalue prodDetTable")) #returns a dict with set keys
    # print (type(product_price), type(category), type(bullets), type(manufacturer_inf), type(product_description))
    # print (product_price, category, bullets, manufacturer_inf, product_description)
    # for keys in specs:
        # print type(specs[keys])
    # product_price = product_price.replace(".",",")
    insert_extra(product_price, category, bullets, manufacturer_inf, product_description, specs, int(x))
    pile.spawn(fetch_info)



if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        log("Seeding the URL frontier with subcategory URLs")
        begin_crawl()  # put a bunch of subcategory URLs into the queue

    log("Beginning crawl at {}".format(crawl_time))
    while (smem("products")):
        try:
            [pile.spawn(fetch_info) for _ in range(settings.max_threads)]
            pool.waitall()
        except MemoryError:
            # print smem()
            break
        except KeyboardInterrupt:
            break
        except:
            continue

    # fetch_info()
