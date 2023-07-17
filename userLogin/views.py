from lib2to3.pytree import convert
from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from home.views import subscribe
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.conf import settings
from .models import Product
from home.models import ProductDetails
from django.core.mail import send_mail
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import requests
import string


from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

#Generate a PDF file for products
@user_passes_test(lambda user: user.is_superuser, login_url='/error')
def report(request):
    #Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    #Create canvas
    c = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    #Create textobject
    textobject = c.beginText()
    textobject.setTextOrigin(inch, inch)
    textobject.setFont("Helvetica", 14)

    #Write text
    #lines = [
    #    "Hello, this is a test",
    #    "I hope you enjoy it!",
    #    "This is line 3",
    #]

    #Designate The Model
    products = Product.objects.all()
    print(products)

    #Create a blank list
    lines = []
    
    for product in products:
        lines.append(product.product_name)
        lines.append("------------------------------------------------------------------------------------------------------------------------------------")
        
    print(lines)
    

    #Loop over lines
    for line in lines:  
        textobject.textLine(line)

    #Finish up
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)

    #Get the value of the BytesIO buffer and write it to the response.
    return FileResponse(buffer, as_attachment=True, filename='Subscribedproducts.pdf')

# def userLogged(request):
#     return render(request,'userLogin/userDashboard.html')

def getAllProduct(request):
    # allitems=product.objects.all()
    # print("*********************************"*3)
    # print(request.user.id)
    allitems=Product.objects.filter(users=request.user)
    # print(allitems)
    return render(request,'userLogin/subscribedProduct.html',{'lists':allitems})

def userlogout(request):
    logout(request)
    return render(request,'home/home.html')


def refresh(request,item_id):
    print("refresh")
    proObj=Product.objects.get(id=item_id)
    price=proObj.curr_price
    if proObj.website=='amazon':
        getInfoFormAmazon(proObj.link)
    elif proObj.website=='flipkart':
        price=getFromFlipkart(proObj.link)
    elif proObj.website=='shopclues':
         price=getFromShopclues(proObj.link)
    elif proObj.website=='jumia':
        price=getFromJumia(proObj.link) 
    elif proObj.website=='avechi':
        price=getFromavechi(proObj.link)
    elif proObj.website=='jiji':
        price=getFromJiji(proObj.link)
    proObj.curr_price=price
    proObj.save()
    allitems=Product.objects.filter(users=request.user)
    return render(request,'userLogin/subscribedProduct.html',{'lists':allitems})

def delete(request,item_id):
    x = Product.objects.get(id= item_id)
    userObj=User.objects.get(id=request.user.id)
    x.users.remove(userObj)
    allitems=Product.objects.filter(users=request.user)
    return render(request,'userLogin/subscribedProduct.html',{'lists':allitems})
    
def userhome(request):
    return render(request,'userLogin/userDashboard.html')

def sendmail(receivers,link):
    print("sending mail")
    subject='Your product''s price has now reduced!!'
    message=f"Hey dear ,your product\n {link} \nhas reduce price,click to checkout the product.\n\n\nRegrads BeiPoa Team.\n\n This is system generated e-mail please don't reply"
    email_from=settings.EMAIL_HOST_USER 
    recipient_list=receivers
    send_mail(subject, message,email_from,receivers)

@login_required(login_url='login')
def save(request):
    if request.user.is_authenticated:
        print("valid")
        title=request.POST.get('title')
        price=request.POST.get('price')
        price=price_convertor(price)
        link=request.POST.get('link')
        prod_id=request.POST.get('id')
        website=request.POST.get('website')
        userObj=User.objects.get(id=request.user.id)
        is_exist=Product.objects.filter(product_id=prod_id)
        if len(is_exist) == 0 :
            obj=Product.objects.create(product_id=prod_id,product_name=title,link=link,curr_price=price,old_price=price,website=website)
            obj.users.add(userObj)
            obj.save()
        else:
            for item in is_exist:
                item.users.add(userObj)
        return HttpResponse("added")
    else:
        return render(request,'home/signIn.html')
    
def checkPrice():
    print("checking price")
    url_list=Product.objects.all()
    for item in url_list:
        if(item.website=='flipkart'):
            curr_price=getFromFlipkart(item.link)
            if curr_price<item.curr_price:
                get_all_user(item)
        if(item.website=='amazon'):
            curr_price=getInfoFormAmazon(item.link)
            if curr_price<item.curr_price:
                get_all_user(item)
           
def get_all_user(item):
    receivers=[]
    print("all user")
    proObj=Product.objects.filter(product_id=item.product_id)
    for item in proObj :
        all_user=item.users.all()
        for user in all_user:
            receivers.append(user.email)
        sendmail(receivers,item.link)  

def price_convertor(price):
    price_ls=price[1:].split(',')
    price="".join(price_ls)
    print(price)
    price=float(price)
    return price

def getFromFlipkart(url):
    try:
        resp = requests.get(url)
        flipSoup=BeautifulSoup(resp.text,'html.parser')
        curr_price=flipSoup.find('div',attrs={'class':'_30jeq3 _16Jk6d'}).get_text()
        # print(curr_price)
        return price_convertor(curr_price)
    except:
        pass
    return 0

def getInfoFormAmazon(url):
    print(url)
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
    resp=requests.get(url,headers=headers)
    AmaSoup=BeautifulSoup(resp.content,'html.parser')
    # print(AmaSoup)
    curr_price=AmaSoup.find('span',attrs={'class':'a-offscreen'}).get_text()
    print(curr_price)
    return price_convertor(curr_price)

def getFromShopclues(url):
    print(url)
    url='https://bazaar.shopclues.com/combo-of-2-black-navy-blue-stylatract-solid-t-shirt-for-men-152223514.html'
    resp=requests.get(url)
    shopSoup=BeautifulSoup(resp.text,'html.parser')
    curr_price=shopSoup.find('span',attrs={'class':'f-price'})
    return price_convertor(curr_price)

def getFromJumia(url):
    print(url)
    resp=requests.get(url)
    jumiaSoup=BeautifulSoup(resp.text,'html.parser')
    curr_price=jumiaSoup.find('span',attrs={'class':'price-box ri'})
    return price_convertor(curr_price)
 
def getFromavechi(url):
    print(url)
    resp=requests.get(url)
    avechiSoup=BeautifulSoup(resp.text,'html.parser')
    curr_price=avechiSoup.find('span',attrs={'class':'price-box ri'})
    return price_convertor(curr_price)

def getFromJiji(url):
    print(url)
    resp=requests.get(url)
    jijiSoup=BeautifulSoup(resp.text,'html.parser')
    curr_price=jijiSoup.find('span',attrs={'class':'price-box ri'})
    return price_convertor(curr_price)


def start():
    scheduler=BackgroundScheduler()
    scheduler.add_job(checkPrice,'interval',minutes=5)

    # scheduler.start()