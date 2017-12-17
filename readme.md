# Amazon Crawler
A relatively simple amazon.com crawler written in python. It has the following features:

 * supports hundreds of simultaneous requests, depending on machine's limits
 * supports using proxy servers
 * supports scaling to multiple machines orchestrating the crawl and keeping in sync
 * can be paused and restarted without losing its place
 * logs progress and warning conditions to a file for later analysis

## Pre-requisites

Before getting started, you need a number of things to be working

 * Redis
 * PostGreSQL
 * Python 2.7

All of these have working installers/setups available for Windows and Linux

## Getting it Setup
After you get a copy of this codebase pulled down locally (either downloaded as a zip or git cloned), you'll need to install the python dependencies:

    pip install -r requirements.txt

Then you'll need to go into the `settings.py` file and update a number of values:

 * **Database Name, Host and User** - Connection information for storing products in a postgres database
 * **Redis Host, Port and Database** - Connection information for storing the URL queue in redis
 * **Proxy List as well as User, Password and Port** - Connection information for your list of proxy servers

Once you've updated all of your connection information, you'll need to run the following at the command line to setup the postgres table that will store the product records:

    python models.py

The fields that are stored for each product are the following:

 * title
 * product_url *(URL for the detail page)*
 * listing_url *(URL of the subcategory listing page we found this product on)*
 * price
 * primary_img *(the URL to the full-size primary product image)*
 * crawl_time *(the time-stamp of when the crawl began)*

For gathering the product data, we also extended with some extra fields. These fields include:

 * bulletpoint_description *(the bullet-points usually found near a product)*
 * manufacturer_info *(info given by the manufacturer, due to inconsistent make-up this is currently pure HTML storage)*
 * product_information *(product information written by users, often contains two (best) reviews, directly after each-other.)*

Furthermore some specs were gathered:

 * s_dimensions *(dimensions given by manufacturer)*
 * s_weight *(item weight given by manufacturer)*
 * s_ASIN *(Amazon Standard Identification Number)*
 * s_MRA *(contains the raw Manufacturer Recommended Age)*
   * s_MRA_min *(contains the lower bound, reformatted to years)*
   * s_MRA_max *(contains the upper bound, reformatted to years)*
 * s_batteries *(batteries, if given by manufacturer in same name as dict_key used for identifying)*
 * s_manufacturer *(the manufacturer)*
 * s_department
 * s_IMM *(Item Model Number given by manufacturer)*

All data is stored within one table for easy conversion to a file-type of choice.
For the latter set of extended fields, due to inconsistencies in the site they might not always return information (or the correct one). Caution is advised when data is used blindly!

## How it Works
You begin the crawler for the first time by running:

    python crawler.py start

This runs a function that looks at all of the category URLs stored in the `start-urls.txt` file, and then explodes those out into hundreds of subcategory URLs it finds on the category pages. Each of these subcategory URLs is placed in the redis queue that holds the frontier listing URLs to be crawled.

Then the program spins up the number of threads defined in `settings.max_threads` and each one of those threads pops a listing URL from the queue, makes a request to it and then stores the (usually) 10-12 products it finds on the listing page. It also looks for the "next page" URL and puts that in the queue.

### Restarting the crawler
If you're restarting the crawler and don't want it to go back to the beginning, you can simply run it with

    python crawler.py

This will skip the step of populating the URL queue with subcategory links, and assumes that there are already URLs stored in redis from a previous instance of the crawler.

This is convenient for making updates to crawler or parsing logic that only affect a few pages, without going back to the beginning and redoing all of your previous crawling work.


## The second crawl
When having gathered a substantial amount of data with the previous code, we still need to retrieve the product specific data, to do this we need to run:

    python info_crawler.py start

This will run almost the same like the previous crawler, however due to the difference in requests that are gonna be made (product specific instead of listings), no real exception correcting code is yet put in place. It selects gets max_per_set from settings.py to check how much should be put in the queue at once. This is done through a SQL query in models.retrieve() that can be changed to your own needs. 
Common errors might be that you go over the max_recursion depth set by Python, or a NoneType error throws your code off. It is advised to keep an eye on the runtime environment of choice to check how it is going. Improvements are welcomed, but this is outside the scope of the project we adapted this for.


When wanting to continue after any error or problem, just run:

    python info_crawler.py

As the info_crawler and the crawler use different redis stacks to work from, both processes could work at the same time. The user needs to watch out themselves for getting kicked from the site!



## Known Limitations
Amazon uses many different styles of markup depending on the category and product type. This crawler focused mostly on the "Music, Movies & Games" category as well as the "Sports & Outdoors" category.

The extractors for finding product listings and their details will likely need to be changed to crawl different categories, or as the site's markup changes over time.