from multiprocessing import context
from django.shortcuts import render, redirect, reverse
from django.db import connection

# Create your views here.

def categoryList():
    cursor = connection.cursor()
    sql = "SELECT CATEGORY_ID, CATEGORY_NAME FROM CATEGORY"
    
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    catList = []

    for r in result:
        cat_id = r[0]
        cat_name = r[1]

        row = {'cat_id':cat_id, 'cat_name':cat_name}
        catList.append(row)

    return catList

def returnAddProduct(request):
    isLoggedIn = True
    catList = categoryList()
    seller_email= request.session['seller_email']

    cursor = connection.cursor()
    sql = "SELECT CATEGORY_NAME FROM CATEGORY"
    cursor.execute(sql)
    result = cursor.fetchall()
    cat_list=[]
    for r in result:
        cat_list.append(r[0])

    cursor = connection.cursor()
    sql = "SELECT SELLER_ID FROM SELLER WHERE EMAIL_ID=:email_id"
    cursor.execute(sql,{'email_id':seller_email})
    result = cursor.fetchone()
    cursor.close()
    seller_id = result[0]

    if request.method == 'POST':
        prod_name = request.POST.get('prod_name')
        cat_name = request.POST.get('cat_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        quantity = int(quantity)
        exp_time_del = request.POST.get('exp_del_time')
        description = request.POST.get('description')

        pname = prod_name.lower()
        cursor = connection.cursor()
        sql = 'SELECT COUNT(*) FROM PRODUCT WHERE LOWER(NAME) = :pname'
        cursor.execute(sql,{'pname': pname})
        result = cursor.fetchone()
        cursor.close()
        if result[0]>0:
            context = {'isLoggedIn':isLoggedIn, 'status':"Product already exist!", 'acType':"seller"}
            return render(request, 'products/add_product.html', context)

        cursor = connection.cursor()
        sql = 'SELECT MAX(PRODUCT_ID) FROM PRODUCT'
        cursor.execute(sql)
        
        last_id = cursor.fetchone()
        last_id = last_id[0]
        if last_id is not  None:
            prod_id = last_id + 1
        else:
            prod_id = 1

        cursor = connection.cursor()
        sql = "SELECT CATEGORY_ID FROM CATEGORY WHERE CATEGORY_NAME = :cat"
        cursor.execute(sql,{'cat':cat_name})
        cat_id = cursor.fetchone()
        cat_id = cat_id[0]

        cursor = connection.cursor()
        sql = "INSERT INTO PRODUCT VALUES(%s,%s,%s,%s,%s,%s,%s)"

        print(prod_id, seller_id, prod_name, cat_id, description, exp_time_del, price)
        cursor.execute(sql,[prod_id, seller_id, prod_name, cat_id, description, exp_time_del, price])
        connection.commit()
        cursor.close()

        
        for i in range(quantity):
            cursor = connection.cursor()
            sql = "INSERT INTO PRODUCT_UNIT VALUES(%s,%s,%s,%s)"
            item_no = i+1
            cursor.execute(sql,[prod_id, seller_id, item_no, "not sold"])
            connection.commit
            cursor.close()
        return redirect('registration:seller_products')

    context = {
        'cat_list':cat_list, 'isLoggedIn':isLoggedIn, 'catList':catList,'acType':"seller"
    }
    return render(request, 'products/add_product.html', context)


def returnProductCat(request, cat_pk):

    isLoggedIn=False
    acType=""
    if request.session.has_key('cus_email'):
        isLoggedIn=True
        acType="customer"
    if request.session.has_key('seller_email'):
        isLoggedIn=True
        acType="seller"
    
    cursor = connection.cursor()
    sql = "SELECT CATEGORY_NAME FROM CATEGORY WHERE CATEGORY_ID = :cat_id"
    catList = categoryList()
    
    cursor.execute(sql,{'cat_id': cat_pk})
    result = cursor.fetchall()
    cursor.close()
    cat_name = result[0][0]

    cursor = connection.cursor()
    sql = "SELECT NAME, DESCRIPTION, PRICE FROM PRODUCT WHERE CATEGORY_ID= :cat_id"
    
    cursor.execute(sql,{'cat_id': cat_pk})
    result = cursor.fetchall()
    cursor.close()

    prod_list = []

    for r in result:
        prod_name = r[0]
        prod_des = r[1]
        prod_price = r[2]
        row = {'prod_name':prod_name, 'prod_des':prod_des, 'prod_price': prod_price}
        prod_list.append(row)

    context = {
        'isLoggedIn':isLoggedIn, 'acType':acType,
        'cat_name':cat_name, 'prod_list':prod_list, 'catList':catList
    }
    
    return render(request, 'products/product_cat.html', context)