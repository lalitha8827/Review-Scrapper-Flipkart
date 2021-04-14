# doing necessary imports

from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)  # initialising the flask app with the name 'app'




@app.route('/',methods=['POST','GET']) # route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            #dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
            #db = dbConn['crawlerDB'] # connecting to the database called crawlerDB
            #reviews = db[searchString].find({}) # searching the collection with the name same as the keyword
            #if reviews.count() > 0: # if there is a collection with searched keyword and it has records in it
            #    return render_template('results.html',reviews=reviews) # show the results to user
            #else:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            reviews = []
            i = 0
            try:
                whole_rating = prod_html.find_all('div', {'class': "_2d4LTz"})[0].text
            except:
                whole_rating = "No ratings yet"
            try:
                prod_name = prod_html.find_all('span', {"class": "B_NuCI"})[0].text
            except:
                prod_name = searchString
            try:
                price = prod_html.find_all('div', {'class': '_30jeq3'})[0].text
            except:
                price = "Zero"
            for commentbox in commentboxes[:]:
                i += 1
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'Anonymous'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'
                mydict = {"i": i, "Product Name": prod_name, "Product Price": price,"Overall Rating": whole_rating, "Customer Name": name,
                          "Customer Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            try:
                k = prod_html.find_all('div', {"class": "col JOpGWq"})[0].find_all('a', {"class": ""})[-1].get("href")
            except:
                k = ""
            if (k == '' or len(reviews) < 10):
                return render_template('results.html', reviews=reviews)
            else:
                ans = "https://www.flipkart.com" + k
                sec = requests.get(ans)
                prod_sec = bs(sec.text, "html.parser")
                x2 = []
                for i1 in prod_sec.find_all('nav', {"class": "yFHi8N"})[0].find_all('a'):
                    x2.append(i1.get("href"))
                l = []
                for c in range(len(x2) - 1):
                    l.append(prod_sec.find_all('nav', {"class": "yFHi8N"})[0].find_all('a', {"class": "ge-49M"})[c].get(
                        "href"))
                k = 0
                if (len(l) != 0):
                    for j in l:
                        ans = "https://www.flipkart.com" + j
                        sec = requests.get(ans)
                        prod_sec = bs(sec.text, "html.parser")
                        x = prod_sec.find_all("div", {"class": "_27M-vq"})
                        for i in x:
                            k += 1
                            try:
                                name = i.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                            except:
                                name = 'Anonymous'

                            try:
                                rating = i.div.div.div.div.text

                            except:
                                rating = 'No Rating'

                            try:
                                commentHead = i.div.div.div.p.text
                            except:
                                commentHead = 'No Comment Heading'
                            try:
                                comtag = i.div.div.find_all('div', {'class': ''})
                                custComment = comtag[0].div.text
                            except:
                                custComment = 'No Customer Comment'
                            mydict = {"i": k, "Product Name": prod_name, "Product Price": price,
                                      "Overall Rating": whole_rating, "Customer Name": name, "Customer Rating": rating,
                                      "CommentHead": commentHead,
                                      "Comment": custComment}
                            reviews.append(mydict)
                return render_template('results.html', reviews=reviews[11:])

        except:
            return 'something is wrong'
         
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(port=8000,debug=True) # running the app on the local machine on port 8000
