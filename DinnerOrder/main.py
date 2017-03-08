from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import hashlib
from database_setup import Base, Restaurant, MenuItem, User, CartItem, Orders, OrderItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///dinnerorder.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

session['Log_in'] = None
# API endpoint
@app.route('/restaurants/JSON')
def showRestaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(restaurants = [r.serialize for r in restaurants])
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(items = [i.serialize for i in items])
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def showItemJSON(restaurant_id,menu_id):
	item = session.query(MenuItem).filter_by(id = menu_id).one()
	return jsonify(item = item.serialize)


@app.route('/',methods = ['GET','POST'])
@app.route('/login/',methods = ['GET','POST'])
def toLogIn():
	if session['Log_in'] != None:
		return redirect(url_for("userPage",user_id = session['Log_in']))
	if request.method == 'POST':
		user = session.query(User).filter_by(name = request.form['name']).one()
		if user:
			if user.password == hashlib.md5(request.form['password']):
				session['Log_in'] = user.id
				flash("Welcome %s") % user.name
				return redirect(url_for("userPage",user_id = user.id))
			else:
				flash("Wrong username or password!")
				return render_template('login.html')
		else:
			flash("Can't find this user!")
			return render_template('login.html')
	else:
		return render_template('login.html')
@app.route('/register/',methods = ['GET','POST'])
def register():
	if request.method =='POST':
		newUser = User(name = request.form['name'],password = hashlib.md5(request.form['password']),city = request.form['city'])
		session.add(newUser)
		session.commit()
		session['Log_in'] = newUser.id
		return redirect(url_for("userPage",user_id = newUser.id))
	else:
		return render_template('register.html')
@app.route('/logout/user/<int:user_id>',methods = ['GET','POST'])
def toLogOut(user_id):
	if request.method == 'POST':
		session['Log_in'] = None
		return redirect("showAllRestaurants")
	else:
		return render_template('logout.html',user_id = user_id)
@app.route('/user/<int:user_id>/')
def userPage(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return render_template('userpage.html',user = user)

@app.route('/restaurant/')
def showAllRestaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html',restaurants = restaurants)
@app.route('/restaurant/<string:keyword>')
def searchedRestaurant(keyword):
	restaurants = session.query(Restaurant).filter_by(name.like("%"+keyword"%")).all()
	if restaurants:
		return render_template('searchedRestaurant.html',restaurants = restaurants,keyword = keyword)
	else:
		flash("No such restaurants!")
		return redirect(url_for("showAllRestaurants"))
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
	# return "This page is the menu for %s restaurant" % restaurant_id
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return render_template('menu.html',restaurant = restaurant,items = items)

@app.route('/user/<int:user_id>/cart/')
def myCart(user_id):
	cartItems = session.query(CartItem).filter_by(user_id = user_id).all()
	return render_template('myCart.html',user_id = user_id,cartitems = cartItems)
@app.route('/user/<int:user_id>/cart/item/<int:menu_id>/add')
def addToCart(user_id,menu_id):
	item = session.query(MenuItem).filter_by(id = menu_id).one()
	newCartItem = CartItem(user_id = user_id, menu_id = menu_id, price = item.price, quantity = 1)
	session.add(newCartItem)
	session.commit()
	flash("Successfully add %s to cart!" % item.name)
	return redirect(url_for('myCart',user_id = user_id))
@app.route('/user/<int:user_id>/cart/item/<int:menu_id>/edit/',methods = ['GET','POST'])
def editCartItem(user_id,menu_id):
	menuitem = session.query(MenuItem).filter_by(menu_id = menu_id).one()
	itemToEdit = session.query(CartItem).filter_by(user_id = user_id, menu_id = menu_id).one()
	if request.method == 'POST':
		if request.form['quantity']:
			if request.form['quantity'] == 0:
				session.delete(itemToEdit)
				session.commit()
				flash("Item %s has been successfully deleted!" % itemToEdit.name)
			else:
				itemToEdit.quantity = request.form['quantity']
				session.add(itemToEdit)
				session.commit()
				flash("Item %s has been successfully edited!" % itemToEdit.name)
			return redirect("myCart",user_id = user_id)
	else:
		return render_template("editCartItem.html",user_id = user_id,menuitem = menuitem, item = itemToEdit)
@app.route('/user/<int:user_id>/cart/item/<int:menu_id>/delete/',methods = ['GET','POST'])
def deleteCartItem(user_id,menu_id):
	itemToDelete = session.query(CartItem).filter_by(user_id = user_id, menu_id = menu_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("Item %s has been successfully deleted!" % itemToDelete.name)
		return redirect("myCart",user_id = user_id)
	else:
		return render_template('deleteCartItem.html',item = itemToDelete)
@app.route('/user/<int:user_id>/cart/addtoorder/',methods = ['GET','POST'])
def addToOrder(user_id):
	if request.method == 'POST':
		newOrder = Orders(user_id = user_id, time = CURRENT_TIMESTAMP, status = "not started")
		session.add(newOrder)
		session.commit()
		itemsToAdd = session.query(CartItem).filter_by(user_id = user_id).all()
		for i in itemsToAdd:
			newOrderItem = OrderItem(order_id = newOrder.id, user_id = user_id, menu_id = i.menu_id, price = i.price, quantity = request.form['quantity'])
			session.delete(i)
			session.add(newOrderItem)
			session.commit()
		return redirect(url_for("listOrders",user_id = user_id))
	else:
		return render_template('addToOrder.html',user_id = user_id)
@app.route('/user/<int:user_id>/orders/')
def listOrders(user_id):
	orders = session.query(Orders).filter_by(user_id = user_id).all()
	orderItems = session.query(OrderItem).filter_by(user_id = user_id).all()
	menuitems = session.query(MenuItem).all()
	return render_template('listOrders.html',user = user, orders = orders, orderitems = orderItems, menuitems = menuitems)
# "not started" can edit item; "not started" and "pending" can only be cancelled; "delievering"; "finished" and "cancelled"can be removed form database;
@app.route('/user/<int:user_id>/orders/<int:order_id>/view/',methods = ['GET','POST'])
def viewOrder(user_id,order_id):
	order = session.query(Orders).filter_by(id = order_id).one()
	orderitems = session.query(OrderItem).filter_by(order_id = order_id).all()
	menuitems = session.query(MenuItem).all()
	return render_template('viewOrder.html',order = order,orderitems = orderitems,menuitems = menuitems)
@app.route('/user/<int:user_id>/orders/<int:order_id>/orderAgian/',methods = ['GET','POST'])
def orderAgain(user_id,order_id):
	lastOrder = session.query(Order).filter_by(id = order_id).one()
	lastitems = session.query(OrderItem).filter_by(order_id).all()
	menuitems = session.query(MenuItem).all()
	if request.method = 'POST':
		newOrder = Orders(user_id = user_id,time = CURRENT_TIMESTAMP, status = "not started")
		session.add(newOrder)
		session.commit()
		for l in lastitems:
			newItem = OrderItem(order_id = newOrder.id, user_id = user_id,menu_id = l.menu_id,quantity = l.quantity)
			session.add(newItem)
			session.commit()
		flash("Successfully add to order!")
		return redirect(url_for("listOrders",user_id = user_id))
	else:
		return render_template('orderAgain.html', user_id = user_id, order_id = order_id, orderitems = lastitems, menuitems = menuitems)
@app.route('/user/<int:user_id>/orders/<int:order_id>/cancel/',methods = ['GET','POST'])
def cancelOrder(user_id,order_id):
	orderToCancel = session.query(Orders).filter_by(id = order_id).one()
	if request.method == 'POST':
		orderToCancel.status = "Cancelled"
		session.add(orderToCancel)
		session.commit()
		flash("Order successfully cancelled!")
		return redirect(url_for("listOrders",user_id = user_id))
	else:
		return render_template('cancelOrder.html',user_id = user_id,order_id = order_id)
@app.route('/user/<int:user_id>/orders/<int:order_id>/delete/',methods = ['GET','POST'])
def removeOrder(user_id,order_id):
	orderToRemove = session.query(Orders).filter_by(id = order_id).one()
	itemsToRemove = session.query(OrderItem).filter_by(id = order_id).all()
	if request.method == 'POST':
		session.delete(orderToRemove)
		session.delete(itemsToRemove)
		session.commit()
		flash("Order successfully removed!")
		return redirect(url_for("listOrders",user_id = user_id))
	else:
		return render_template('removeOrder.html',usr_id,order_id)
@app.route('/user/<int:user_id>/orders/<int:order_id>/item/<int:menu_id>/edit/',methods = ['GET','POST'])
def editOrderItem(user_id,order_id,menu_id):
	itemToEdit = session.query(OrderItem).filter_by(order_id = order_id, menu_id = menu_id).one()
	menuitem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		if request.form['quantity']:
			if request.form['quantity'] == 0:
				session.delete(itemToEdit)
				session.commit()
				flash("Item %s has been successfully deleted!" % menuitem.name)
			else:
				itemToEdit.quantity = request.form['quantity']
				session.add(itemToEdit)
				session.commit()
				flash("Item %s has been successfully edited!" % menuitem.name)
			return redirect("viewOrder",user_id = user_id,order_id = order_id)
	else:
		return render_template("editOrderItem.html",user_id = user_id,menuitem = menuitem, item = itemToEdit)

if __name__ == "__main__":
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = "0.0.0.0", port = 5000)