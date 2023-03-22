from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import datetime
import json

# Create your views here.
def store(request):

    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
        cartItems=order['get_cart_items']
    products=Product.objects.all() 
    context={'products':products,'cartItems':cartItems}
    return render(request,'store/store.html',context)

def cart(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        try:
            cart =json.loads(request.COOKIES['cart'])
        except:
            cart ={}
        print('Cart:',cart)
        items=[]
        order={'get_cart_total':0,'get_cart_items':0}
        cartItems=order['get_cart_items']
        for i in cart:
            cartItems+=cart[i]['quantity']

            product =Product.objects.get(id=i)
            total=(product.price*cart[i]['quantity'])

            order['get_cart_total']+=total
            order['get_cart_items']+=cart[i]['quantity']



    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        
        items=[]
        order={'get_cart_total':0,'get_cart_items':0}
        cartItems=order['get_cart_items']
    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/checkout.html',context)


def updateItem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']

    print('Action:',action)
    print('productId:',productId)


    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order,created=Order.objects.get_or_create(customer=customer,complete=False)

    orderItem,created=OrderItem.objects.get_or_create(order=order,product=product)
    if action=='add':
        orderItem.quantity+=1

    elif action=='remove':
        orderItem.quantity-=1
    orderItem.save()
    
    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse('Item added',safe=False)


def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    # print('Data:',request.body)
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        total=float(data['form']['total'])
        order.transaction_id=transaction_id

        if total==float(order.get_cart_total):
            order.complete=True
        order.save()

        if order.shipping ==True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )


    else:
        print('User is not logged in')
    return JsonResponse('Payment Completed...',safe=False)