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
    categories = page.findAll("a", "a-link-normal a-color-tertiary")
    result = str()
    if categories:
        # print categories[0]
        y = 0    
        for x in categories:
            result += htmlparser.unescape(x.text.encode("utf-8"))
            if y < len(categories)-1:
                result = result + " > "
            y +=1
        return result
    else:
        return "<missing catgory >"

def get_bullets(page):
    bullets = page.findAll("span", "a-list-item")
    res = str()
    if bullets:
        for x in bullets:
            res = res + " " + htmlparser.unescape(x.text.encode("utf-8"))
        print("this is result of bulletes: {}".format(res))
        return res
    return "<No bullets>"

def manu_info(page):
    manufacturer_inf = page.find("div","a-section a-spacing-extra-large bucket")
    if not manufacturer_inf:
        manufacturer_inf = "<no manufacturer_inf>"
    return manufacturer_inf

def get_product_description(page):
    # print page
    product_des = page.findAll("p")
    res = str()
    if page:
        for p in product_des:
            res += " " + htmlparser.unescape(p.text.encode("utf-8"))
        # print ("product description: {}".format(res))
        return res
    else:
        return "<No product description found>"

def get_specs(page):
    print page
    specs = {"dimensions":None, "weight":None, "ASIN":None, "MRA_min":None, "MRA_max":None, "batteries":None, "maufacturer":None, "department":None, "review":None}
    specs = {"dimensions", "weight", "ASIN", "MRA_min", "MRA_max", "batteries", "maufacturer", "department", "review"}
    print specs


#s_dimensions, S_weight, S_ASIN, S_MRA_min, S_MRA_max
#s_batteries, s_manufacturers, s_department, S_review