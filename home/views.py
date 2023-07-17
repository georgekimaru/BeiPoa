from django.http.request import HttpHeaders
from django.shortcuts import redirect, render,HttpResponse,redirect
from .models import ProductDetails, ProductDetailsJiji
from bs4 import BeautifulSoup
import requests
from django.contrib import  messages
import logging
from home.models import Contact,Feedback
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from operator import attrgetter
from amazon_paapi import AmazonApi
#from .helpers import getInfoFromFlipKart, getInfoFromAmazon, getInfoFromShopClues, getInfoFromSnapDeal, getInfoFromAjio, getInfoFromMyntra

# Create your views here.
def index(request):
   return render(request,'home/home.html')

    #return HttpResponse("This is home page")


def contact(request):
    contactPage=["Feel free to contact us","Send a message","Leave your message here..."]
    if request.method=="POST":
        # Extract form data using get() with default values 
        # Using default values in request.POST.get() to avoid potential None values in case the form fields are missing in the request.
        firstName=request.POST.get('firstName', '')
        lastName=request.POST.get('lastName', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        message=request.POST.get('message', '')
        
        # Create and save Contact model instance
        contact=Contact(firstName=firstName,lastName=lastName,email=email,phone=phone,message=message)
        contact.save()
        
        messages.success(request, "Thank You ! 🙂")
        
    return render(request,'home/contactInfo.html',{'info':contactPage})
    #return HttpResponse("this is contact page")

def feedback(request):
    feedbackPage=["Your Feedback","We would like your feedback to improve our website.","Leave your valuable feedback here..."]
    if request.method=="POST":
        # Extract form data using get() with default values
        name=request.POST.get('name')
        email=request.POST.get('email')
        message=request.POST.get('message')
        
        # Create and save Feedback model instance
        feedback=Feedback(name=name,email=email,message=message)
        feedback.save()
        messages.success(request, " Thank You ! We admire Your Valuable feedback !")
    return render(request,'home/feedback.html',{'info':feedbackPage})
    #return HttpResponse("This is feedback section")

def register(request):
        return render(request,"home/registeration.html")
    

def signup(request):
    if request.method == 'POST':
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        
        # Check if username contains only letters and numbers
        if not username.isalnum():
            messages.error(request,"User name contains only letters and numbers!")
            return redirect('signin')
            
        # Check if username length is within a valid range    
        if len(username)>10:
            messages.error(request,"user name too long !")
            return redirect('register')
        
        # Check if passwords match
        if pass1!=pass2:
            messages.error(request,"Password are not matching 😰 !")
            return render(request,'home/signIn.html')
            
        # Create a new user and save it
        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.save()
        messages.success(request,"Registered Successfully !💯")
        return render(request,"home/signIn.html")
    else:
        return HttpResponse("inside Signup else")

def userlogin(request):
     if request.method == 'POST':
        loginusername=request.POST['loginusername']
        loginpassword=request.POST['loginpassword']
        
        # Authenticate user credentials
        user = authenticate(request,username = loginusername,password = loginpassword)
        
        if user is not None:
             # Log in the user and display success message
            login(request, user)
            messages.success(request,"Successfully logged In 🙃")
            return render(request,'userLogin/userDashboard.html',{'userName':request.user})
        else:
            # Display error message for invalid credentials
            messages.error(request,"Invalid Credentials 😔 , please try Again !")
            return render(request,"home/signIn.html")

def userlogout(request):
    # Display a success message to the user
    messages.success(request,"Logged Out !")
    # Perform user logout
    logout(request)
    # Redirect the user to the home page
    return redirect('home')

def userDashboard(request):
    # Render the user dashboard template
    return render(request, "userDashboard.html")

def login1(request):
    # Render the login page
    # messages.success(request,"Login Portal")
    return render(request,'home/signIn.html')
    #return HttpResponse("This is login section")


def subscribe(ls):
    pass


def search(request):
    if request.method == "POST":
        webList = request.POST.getlist('websites')
        q = request.POST.get('search')
        view = request.POST.get('view')
        
        if(q == "" or len(webList) == 0):
            if request.user.is_authenticated:
                return render(request,'userLogin/userDashboard.html',{'error':True,'search':q,'weblist':webList,'userName':request.user})
            else:
                return render(request,'home/searchProduct.html',{'error':True,'search':q,'weblist':webList})
            
        AllWebProductList=[]
        jumiaList=[]
        avechiList=[]
        jijiList=[]
        FlipkartList=[]
        AmazonList=[]
        shopcluesList=[]
        snapdealList=[]
        MyntraList=[]
        
        if 'jumia' in webList:
            jumiaList=getInfoFromJumia(q)
            AllWebProductList.append(jumiaList)

        if 'jiji' in webList:
            jijiList=getInfoFromJiji(q)
            AllWebProductList.append(jijiList)

        if 'avechi' in webList:
            avechiList=getInfoFromavechi(q)
            AllWebProductList.append(avechiList)
            
        if 'flipkart' in webList:
            FlipkartList=getInfoFromFlipkart(q)
            AllWebProductList.append(FlipkartList)
            #return render(request,'home/searchProduct.html',{'lists':productObj})
            
        if 'amazon' in webList:
            AmazonList=getInfoFormAmazon(q) # Scrapping
            AllWebProductList.append(AmazonList)
            
        if 'shopclues' in webList:
            shopcluesList=getInfoFromShopClues(q)
            AllWebProductList.append(shopcluesList)
            
        if 'snapdeal' in webList:
            snapdealList=getInfoFromSnapDeal(q)
            print ("welcome in snapdeal")
            
        if 'ajio' in webList:
            ajioList=getInfoFromAjio(q)
            
        if 'myntra' in webList:
            MyntraList=getInfoFromMyntra(q)
            AllWebProductList.append(MyntraList)
            print(" welcome in myntra")
            
        #sorting(AllWebProductList)
        mergeList=FlipkartList+AmazonList+shopcluesList+snapdealList+MyntraList+jumiaList
        # sorting(mergeList,asc)
        # print(request.user.is_authenticated)
        if request.user.is_authenticated :
            return render(request,'userLogin/userDashboard.html',{'lists':mergeList,'val':view,'search':q,'weblist':webList,'userName':request.user})
        else:
            return render(request,'home/searchProduct.html',{'lists':mergeList,'val':view,'search':q,'weblist':webList})
        #messages.warning(request,name)
    return render(request,'home/searchProduct.html')


def result(request):
    # Return a simple HTTP response
    return HttpResponse("kjghil")



def sorting(PList,asc):
    # Sort the list of objects based on the 'price' attribute
    PList.sort(key=attrgetter('price'),reverse=asc)

'''
form(getAlert)
getAlert->click->fucn->form
name = ge
fomr(action=/subscribe)
'''





#BY PAPI AMAZON
def getInfoAmazon(product):
    try:
        amazon = AmazonApi('','','','IN') # Replace with your access keys
        search_result = amazon.search_items(keywords=product)
        AmazonList=[]
        # print(search_result.items)
        
        for item in search_result.items:
            obj = ProductDetails()
            obj.link = item.detail_page_url
            obj.img = item.images.primary.medium.url
            # print(item.item_info.by_line_info.brand)
            # print(item.item_info.features)
            obj.desc = item.item_info.title.display_value
            obj.price = item.offers.listings[0].price.amount
            AmazonList.append(obj)
    except:
        pass
    return AmazonList

def extract_url(url):

    if url.find("www.amazon.in") != -1:
        index = url.find("/dp/")
        if index != -1:
            index2 = index + 14
            url = "https://www.amazon.in" + url[index:index2]
        else:
            index = url.find("/gp/")
            if index != -1:
                index2 = index + 22
                url = "https://www.amazon.in" + url[index:index2]
            else:
                url = None
    else:
        url = None
    return url
    
# By SCRAPPING from AMAZON
def getInfoFormAmazon(productName):
    headers = {
        "Host": "www.amazon.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        }
    try:
        url="https://www.amazon.com/s?k="
        productName=productName.replace(" ", "+")
        #print(url+q+'&ref=nb_sb_noss_1')
        resp = requests.get(url +productName+'&ref=nb_sb_noss_1',headers=headers)
        # print(resp.status_code)
        AmaSoup=BeautifulSoup(resp.text,'html.parser')
        # print(AmaSoup)
        items=AmaSoup.find_all('div',attrs={'data-component-type':'s-search-result'})
        # print(len(items))
        AmazonList1=[]
        if len(items)>0:
            for item in items:
                obj=ProductDetails() 
                if item.find('span',attrs={'data-a-color':'price'}):
                    obj.price=item.find('span',attrs={'data-a-color':'price'}).contents[0].text
                    #temp1=''.join(char for char in temp if char.isdigit())
                    #obj.price=temp1
                else:
                    continue
                obj.id=item.get('data-asin')
                if item.find('span',attrs={'data-a-color':'secondary'}):
                    obj.originalPrice=item.find('span',attrs={'data-a-color':'secondary'}).contents[0].get_text()
                #obj.price=item.find('span',attrs={"class":'a-offscreen'}).text
                #obj.desc=item.find('span',attrs={'class':'a-size-medium a-color-base a-text-normal'}).get_text()
                obj.desc=item.find('a',attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).contents[0].get_text()
                if item.find('h5',attrs={'class':'s-line-clamp-1'}):
                    obj.brand=item.find('h5',attrs={'class':'s-line-clamp-1'}).contents[0].get_text()
                obj.img=item.find('img',attrs={'class':'s-image'}).get('src')
                obj.id=item.get('data-asin')
                #  print(obj.id)
                # print(item.find('a',attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).get('href'))
                url="https://www.amazon.in"+item.find('a',attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).get('href')
                obj.link=url
                obj.website="amazon"

                AmazonList1.append(obj)
    except:
        pass
    return AmazonList1


# BY SCRAPPING FLIPKART
def getInfoFromFlipkart(productName):
    try:
        url = "https://flipkart.com/search?q="
        productName = productName.replace(" ", "+")
        resp = requests.get(url + productName)
        if resp.status_code !=200:
            print("Sorry can't fetch data for this product right now")
        flipSoup=BeautifulSoup(resp.text,'html.parser')
        # allRelated=flipSoup.find('div',{'class':'_1YokD2 _3Mn1Gg'})
        # children=allRelated.findChildren('div',recursive=False)
        # print(children)
        FlipkartList=[]
        # temp=flipSoup.find_all('div',attrs={'class':'_13oc-S'})
        # print(len(temp))
        # for itemlist in temp:
        #     for item in itemlist:
        #         obj=productDetails()
        #         obj.website='flipkart'
        #         # FOR DISCOUNTED PRICE
        #         if item.find('div',attrs={'class':'_30jeq3 _1_WHN1'}):
        #             obj.price=item.find('div',attrs={'class':'_30jeq3 _1_WHN1'}).text
        #         elif item.find('div',attrs={'class':'_30jeq3'}):
        #             obj.price=obj.price=item.find('div',attrs={'class':'_30jeq3'}).text
        #         # FOR ORIGINAL PRICE
        #         if item.find('div',attrs={'class':'_3I9_wc _27UcVY'}):
        #             obj.originalPrice=item.find('div',attrs={'class':'_3I9_wc _27UcVY'}).text
        #         elif item.find('div',attrs={'class':'_3I9_wc'}):
        #             obj.originalPrice=item.find('div',attrs={'class':'_3I9_wc'}).text
        #         #FOR ITEM DESCRIPTION
        #         if item.find('div',attrs={'class':'_4rR01T'}):
        #             obj.desc=item.find('div',attrs={'class':'_4rR01T'}).text
        #         elif item.find('a',attrs={'class':'s1Q9rs'}):
        #             obj.desc=item.find('a',attrs={'class':'s1Q9rs'}).get('title')
        #         #FOR ITEM IMAGE
        #         if item.find('img',attrs={'class':'_396cs4 _3exPp9'}):
        #             obj.img=item.find('img',attrs={'class':'_396cs4 _3exPp9'}).get('src')
        #         elif item.find('img',attrs={'class':'_396cs4 _3exPp9'}):
        #             obj.img=item.find('img',attrs={'class':'_396cs4 _3exPp9'}).get('src')
        #         #FOR ITEM LINK
        #         if item.find('a',attrs={'class':'_1fQZEK'}):
        #             obj.link="https://www.flipkart.com"+product.get('href')
        #         elif item.find('a',attrs={'class':'s1Q9rs'}):
        #             obj.link="https://www.flipkart.com"+product.find('a',attrs={'class':'s1Q9rs'}).get('href')
        #         elif item.find('a',attrs={'class':'_2UzuFa'}):
        #             obj.link="https://www.flipkart.com"+product.find('a',attrs={'class':'_2UzuFa'}).get('href')
        #         FlipkartList.append(obj)
        #     print(len(item))

        electronics1=flipSoup.find_all('a',attrs={'class':'_1fQZEK'})
        electronics2=flipSoup.find_all('div',attrs={'class':'_4ddWXP'})
        cloth=flipSoup.find_all('div',attrs={'class':'_1xHGtK _373qXS'})

        if len(electronics1)> 0 :
            for product in electronics1:
                obj=ProductDetails()
                obj.website="flipkart"
                obj.price=product.find('div',attrs={'class':'_30jeq3 _1_WHN1'}).text
                print("jfqkl")
                try:
                    obj.id=product.parent.parent.get('data-id')
                except:
                    pass
                if product.find('div',attrs={'class':'_3I9_wc _27UcVY'}):
                    obj.originalPrice=product.find('div',attrs={'class':'_3I9_wc _27UcVY'}).text
                if product.find('div',attrs={'class':'_3Ay6Sb'}):
                    obj.discount=product.find('div',attrs={'class':'_3Ay6Sb'}).contents[0].get_text()
                obj.desc=product.find('div',attrs={'class':'_4rR01T'}).text
                obj.img=product.find('img',attrs={'class':'_396cs4 _3exPp9'}).get('src')
                obj.link="https://www.flipkart.com"+product.get('href')
                FlipkartList.append(obj)
        elif len(electronics2)>0:
            for product in electronics2:
                obj=ProductDetails()
                #print(len(product.contents))
                obj.website="flipkart"
                obj.price=product.find('div',attrs={'class':'_30jeq3'}).text
                #temp1=''.join(char for char in temp if char.isdigit())
                #obj.price=temp1
                try:
                    obj.id=product.parent.get('data-id')
                except:
                    pass
                if product.find('div',attrs={'class':'_3I9_wc'}):
                    obj.originalPrice=product.find('div',attrs={'class':'_3I9_wc'}).text
                if product.find('div',attrs={'class':'_3Ay6Sb'}):
                    obj.discount=product.find('div',attrs={'class':'_3Ay6Sb'}).contents[0].get_text()
                obj.desc=product.find('a',attrs={'class':'s1Q9rs'}).get('title')
                obj.img=product.find('img',attrs={'class':'_396cs4 _3exPp9'}).get('src')
                obj.link="https://www.flipkart.com"+product.find('a',attrs={'class':'s1Q9rs'}).get('href')
                FlipkartList.append(obj)
        elif len(cloth)>0:
            for product in cloth:
                obj=ProductDetails()
                #print(len(product.contents))
                obj.website="flipkart"
                if product.find('div',attrs={'class':'_30jeq3'}):
                    obj.price=product.find('div',attrs={'class':'_30jeq3'}).text
                    #temp1=''.join(char for char in temp if char.isdigit())
                    #obj.price=temp1
                else:
                    continue
                try:
                    obj.id=product.parent.get('data-id')
                except:
                    pass
                obj.desc=product.find('a',attrs={'class':'IRpwTa'}).get('title')
                if product.find('div',attrs={'class':'_3I9_wc'}):
                    obj.originalPrice=product.find('div',attrs={'class':'_3I9_wc'}).text
                if product.find('div',attrs={'class':'_3Ay6Sb'}):
                    obj.discount=product.find('div',attrs={'class':'_3Ay6Sb'}).contents[0].get_text()
                img=product.find('div',attrs={'class':'_312yBx SFzpgZ'}).find('img')['src']
                # print(img.find('img').attrs['src'])
                obj.img=product.find('img',attrs={'class':'_2r_T1I'}).get('src')
                # print(obj.img)
                obj.brand=product.find('div',attrs={'class':'_2WkVRV'}).text
                obj.link="https://www.flipkart.com"+product.find('a',attrs={'class':'_2UzuFa'}).get('href')
                FlipkartList.append(obj)        
    except:
        pass
    return FlipkartList
    
# By Scrapping from Shopclues
def getInfoFromShopClues(productName):
    try:
        url="https://www.shopclues.com/search?q="
        # productName=productName.replace(" ","%")
        shopcluesList=[]
        # print(url+productName)
        resp=requests.get(url+productName)
        shopcluesSoup=BeautifulSoup(resp.text,'html.parser')
        items=shopcluesSoup.find_all('div',attrs={'class','column col3 search_blocks'})
        # print(len(items))
        if len(items)>0:
            for item in items:
                obj=ProductDetails()
                obj.website="shopclues"
                obj.desc=item.find('h2').text
                obj.price=item.find('div',attrs={'class':'ori_price'}).span.string
                obj.discount=item.find('div',attrs={'class':'ori_price'}).span.next_sibling.string
                # obj.originalPrice=item.find('div',attrs={'class':'old_prices'}).span.string
                obj.link=item.find('a').get('href')
                obj.img=item.find('div',attrs={'class':'img_section'}).img.get('src')
                #print(temp.find('span',attrs={'class':'p_price'}))
                #temp1=item.find('div',attrs={'class':'old_price'})
                #print(temp1.find('span',attrs={'class':'p_price'}))
                #obj.originalPrice=item.find('span')
                shopcluesList.append(obj)
                #print(shopcluesList)
    except:
        pass
    return shopcluesList



# SCRAPING FROM JUMIA
def getInfoFromJumia(productName):
    try:
        url = "https://www.jumia.co.ke/catalog/?q="
        jumiaList = []
        #print(url+productName)
        resp = requests.get(url + productName)
        jumiaSoup = BeautifulSoup(resp.text, 'html.parser')
        items = jumiaSoup.find_all('article', attrs={'class','prd _fb col c-prd'})
        #print(len(items))
        if len(items) > 0:
            for item in items:
                obj = ProductDetails()
                obj.website = "jumia"
                obj.desc = item.find('h3').text
                obj.price = item.find('div', class_='prc').text
                #print(obj.price)
                obj.discount = item.find('div', class_='old').text
                #print(obj.discount)
                obj.link = item.find('a').get('href')
                #print(obj.link)
                obj.img=item.find('div',attrs={'class':'img-c'}).img.get('src')
                #print(obj.img)
                jumiaList.append(obj)
    except:
        pass
    return jumiaList

# SCRAPING FROM JIJI
def getInfoFromJiji(productName):
    try:
        url = "https://jiji.co.ke/search?query="
        jijiList = []
        #print(url+productName)
        resp = requests.get(url + productName)
        jijiSoup = BeautifulSoup(resp.text, 'html.parser')
        items = jijiSoup.find_all('div', attrs={'class','b-list-advert__item-wrapper b-list-advert__item-wrapper--base'})
        #print(len(items))
        if len(items) > 0:
            for item in items:
                obj = ProductDetails()
                obj.website = "jiji"
                obj.desc = item.find('div', class_='b-advert-title-inner qa-advert-title b-advert-title-inner--div').text
                obj.price = item.find('div', class_='qa-advert-price').text
                #print(obj.price)
                obj.discount = item.find('div', class_='qa-advert-price').text
                #print(obj.discount)
                obj.link = item.find('a').get('href')
                #print(obj.link)
                obj.img="jiji.co.ke"
                #print(obj.img)
                jijiList.append(obj)
                #print(jijiList)
    except:
        pass
    return jijiList
   

# SCRAPING FROM avechi
def getInfoFromavechi(productName):
    try:
        url = "https://avechi.co.ke/?s="
        avechiList = []
        #print(url+productName)
        resp = requests.get(url + productName)
        avechiSoup = BeautifulSoup(resp.text, 'html.parser')
        items = avechiSoup.find_all('article', attrs={'class','col_item offer_grid rehub-sec-smooth offer_grid_com mobile_compact_grid no_btn_enabled offer_act_enabled'})
        #print(len(items))
        if len(items) > 0:
            for item in items:
                obj = ProductDetails()
                obj.website = "avechi"
                obj.desc = item.find('h3').text
                #print(obj.desc)
                obj.price = item.find('div', class_='prc').text
                #print(obj.price)
        #        obj.discount = item.find('div', class_='old').text
                #print(obj.discount)
                obj.link = item.find('a').get('href')
                #print(obj.link)
        #        obj.img=item.find('div',attrs={'class':'img-c'}).img.get('src')
                #print(obj.img)

                avechiList.append(obj)

    except:
        pass
    return avechiList


# By Scrapping from SNAPDEAL
def getInfoFromSnapDeal(productName):
    try:
        headers = {
            "Host": "www.snapdeal.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        url="https://m.snapdeal.com/search?keyword="
        productName=productName.replace(" ","%")
        snapdealList=[]
        print(url+productName)
        resp=requests.get(url+productName,headers=headers)
        print(resp.status_code)
        snapdealSoup=BeautifulSoup(resp.text,'lxml')
        # print(snapdealSoup)
        items=snapdealSoup.find_all('div',attrs={'class':'col-xs-6  favDp product-tuple-listing js-tuple '})
    except:
        pass
    print(len(items))


#BY SCRAPPING FROM AJIO
def getInfoFromAjio(productName):
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
        url="https://www.ajio.com/search/?text="
        productName = productName.replace(" ", "%")
        resp = requests.get(url + productName,headers=headers)
        requests.session().close()
        AjioSoup=BeautifulSoup(resp.text,'html.parser')
        items=AjioSoup.find_all('div',attrs={'class':'item rilrtl-products-list__item item'})
        print(AjioSoup)
        print(len(items))
        if(len(items)>0):
            for item in items:
                obj=ProductDetails()
                obj.websites="Ajio"
                print(item.find('div',attrs={'class':'nameCls'}))
                # print(item.find('img',attrs={'class':'rilrtl-lazy-img  rilrtl-lazy-img-loaded'}))

    except:
        pass



# BY SCRAPPING FROM MYNTRA
def getInfoFromMyntra(productName):
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
        url="https://www.myntra.com/"
        productName= productName.replace(" ", "-")
        # print(url+productName)
        MyntraList=[]
        resp = requests.get(url + productName,headers=headers)
        requests.session().close()
        MyntraSoup=BeautifulSoup(resp.text,'html.parser')
        items=MyntraSoup.find_all('div',attrs={'id':'desktopSearchResults'})
        print(len(items))
        if len(items)>0:
            for item in items:
                obj=ProductDetails()
                obj.brand=item.find('h3',attrs={'class':'product-brand'})
                obj.desc=item.find('h4',attrs={'class':'product-produc'})
                #obj.img=item.find('img').get('src')
                # obj.link=item.find('a').get('href')
                MyntraList.append(obj)
    except:
        pass
    return MyntraList
