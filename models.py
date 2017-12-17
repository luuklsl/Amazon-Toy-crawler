import psycopg2

import settings

conn = psycopg2.connect(database=settings.database, host=settings.host, user=settings.user, password=settings.password)
cur = conn.cursor()


class ProductRecord(object):
    """docstring for ProductRecord"""
    def __init__(self, title, product_url, listing_url, price, primary_img, crawl_time):
        super(ProductRecord, self).__init__()
        self.title = title
        self.product_url = product_url
        self.listing_url = listing_url
        self.price = price
        self.primary_img = primary_img
        self.crawl_time = crawl_time

    def save(self):
        cur.execute("INSERT INTO products (title, product_url, listing_url, price, primary_img, crawl_time) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (
            self.title,
            self.product_url,
            self.listing_url,
            self.price,
            self.primary_img,
            self.crawl_time,
        ))
        conn.commit()
        return cur.fetchone()[0]

def insert_extra(price, category, bullets, manfacturer_info, product_info, specs, id_num):
    string = specs["Manufacturer recommended age"]
    try:
        st = string.split("-")
        print st
        # print len(st)
        if len(st)==1: #the target is specified as `x months/years and up`
            if (st[0].find("years")>=0 ):
                z = st[0].find("years")
            elif (st[0].find("months")>=0):
                z = st[0].find("months") 
            st[0] = st[0][:z]
            


        elif (st[1].find("years")== -1): #if years is not found
            x = st[1].find("months")    #find whereever month is hiding
            st[1] = str(float(st[1][:x])/12) #devide by 12, add years
            st[0] = str(float(st[0][:x])/12)
        else:
            if (st[0].find("months")>=0):   #if only the first one is written in months
                z = st[0].find("months")
                st[0] = str(float(st[0][:z])/12) #do same as above
            x = st[1].find("years") #for second one, cut off
        if len(st)>1:  #if we had something to split on before
            try:
                st[1] =st[1][:x]
            except UnboundLocalError:
                print st
                raise ValueError()
            # print st[1]
            st[1] = st[1]+" years"
            st[0] = st[0]+" years"
        else:
            st.append(None)
    except AttributeError:
        st = []
        st.append(None)
        st.append(None)
        # st[1] = None
    # print (st)
    # print (st[0],st[1])

    cur.execute("""UPDATE products2 SET 
        price = %s, 
        category = %s, 
        bulletpoint_description = %s, 
        manfacturer_info = %s, 
        product_information = %s, 
        s_dimensions = %s, 
        s_weight = %s, 
        s_IMM = %s, 
        s_ASIN = %s, 
        s_MRA_min = %s, 
        s_MRA_max = %s, 
        s_MRA_raw = %s, 
        s_batteries = %s, 
        s_manufacturer = %s,
        s_department = %s
        WHERE id =%s RETURNING id""", (
        price,
        category,
        bullets,
        manfacturer_info,
        product_info,
        specs["Product Dimensions"],                #s_dimensions
        specs["Item Weight"],                       #s_weight
        specs["Item model number"],                 #s_IMM
        specs["ASIN"],                              #s_ASIN
        st[0],                                    #s_MRA_min
        st[1],                                    #s_MRA_max
        specs["Manufacturer recommended age"],      #s_MRA_raw
        specs["Batteries"],                         #s_batteries
        specs["Manufacturer"],                      #s_manufacturer
        specs["Department"],                        #s_departmnet
        id_num
        ))
    conn.commit()
    return cur.fetchone()[0]



def retrieve():
    cur.execute("""SELECT * 
FROM products2
WHERE price IS NULL
LIMIT {}""".format(settings.max_per_set))
    return cur.fetchall()


if __name__ == '__main__':

    # setup tables
    cur.execute("DROP TABLE IF EXISTS products2")
    conn.commit()
    cur.execute("""CREATE TABLE products2 (
        id          serial PRIMARY KEY,
        title       varchar(2056),
        product_url varchar(2056),
        listing_url varchar(2056),
        price       varchar,
        primary_img varchar(2056),
        crawl_time timestamp,
        category text,
        bulletpoint_description text,
        manfacturer_info text,
        product_information text,
        s_dimensions varchar(2056),
        s_weight varchar(2056),
        s_ASIN varchar (2056),
        s_MRA_min varchar(2056),
        s_MRA_max varchar(2056),
        s_MRA_raw varchar(2056),
        s_batteries varchar(2056),
        s_manufacturer varchar(2056),
        s_department varchar(2056),
        s_IMM varchar(2056)


    );""")
    conn.commit()
