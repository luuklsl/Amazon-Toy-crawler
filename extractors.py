from HTMLParser import HTMLParser

htmlparser = HTMLParser()


def get_title(item):
    title = item.find("h2", "s-access-title")
    if title:
        return htmlparser.unescape(title.text.encode("utf-8"))
    else:
        return "<missing product title>"


def get_url(item):
    link = item.find("a", "s-access-detail-page")
    if link:
        return link["href"]
    else:
        return "<missing product url>"


def get_price(item):
    price = item.find("span", "s-price")
    if price:
        return price.text
    return None


def get_primary_img(item):
    thumb = item.find("img", "s-access-image")
    if thumb:
        src = thumb["src"]

        p1 = src.split("/")
        p2 = p1[-1].split(".")

        base = p2[0]
        ext = p2[-1]

        return "/".join(p1[:-1]) + "/" + base + "." + ext

    return None


def price_on_page(page):
    # print html
    price = page.find("span", "a-color-price")
    if price:
        return price.text
    return None

def get_category(page):
    try:
        categories = page.findAll("a", "a-link-normal a-color-tertiary")
    except AttributeError:
        return "<missing catgory>"
    result = str().encode("utf-8")
    if categories:
        # print categories[0]
        y = 0    
        for x in categories:
            result += x.text.encode("utf-8")
            if y < len(categories)-1:
                result = result + " > "
            y +=1
        return str(result)
    else:
        return "<missing catgory>"

def get_bullets(page):
    try:
        bullets = page.findAll("span", "a-list-item")
    except AttributeError:
        return "<no bullets found>"
    res = str().encode("utf-8")
    if bullets:
        for x in bullets:
            res = res + " " + x.text.encode("utf8")
        # print("this is result of bulletes: {}".format(res).encode("utf-8"))
        try:
            return res.encode("utf8")
        except UnicodeDecodeError:
            return res
    return "<no bullets found>"

def manu_info(page):
    manufacturer_inf = page.find("div","a-section a-spacing-extra-large bucket")
    if not manufacturer_inf:
        manufacturer_inf = "<no manufacturer_inf>"
    return str(manufacturer_inf)

def get_product_description(page):
    # print page
    try:
        product_des = page.findAll("p")
        res = str().encode('utf-8')
        if page:
            for p in product_des:
                res += " " + p.text.encode("utf-8")
            # print ("product description: {}".format(res))
        try:
            return res.encode("utf-8")
        except UnicodeDecodeError:
            return res
        else:
            return "<No product description found>"
    except AttributeError:
        return "<possible kick from amazon?>"

def get_specs(page):
    # print page
    # , "Customer Reviews":None  <-- kept that one out due to Amazon loading this with JS, current script doesn't know how to handle this
    specs = {"Product Dimensions":None, "Item Weight":None, "ASIN":None, "Item model number": None, "Manufacturer recommended age":None, "Batteries":None, "Manufacturer":None, "Department":None}
    try:
        table_r = page.findAll("tr")
    except AttributeError:
        return specs
    # specs = {"dimensions", "weight", "ASIN", "MRA_min", "MRA_max", "batteries", "maufacturer", "department", "review"}
    # print specs
    for rows in table_r:
        key = rows.find("th").text
        if key in specs:
            specs[key] = rows.find("td").text
        # else:
            # print "supperflous information found {}".format(key)
    print specs
    return specs


#s_dimensions, S_weight, S_ASIN, S_MRA_min, S_MRA_max
#s_batteries, s_manufacturers, s_department, S_review
# products2(price,bulletpoint_description, manfacturer_info, product_info, s_dimensions, s_weight, s_ASIN, s_MRA_min, s_MRA_max, s_MRA_raw, s_batteries, s_manufacturer, s_department