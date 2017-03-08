import sys
from sqlalchemy import Column,ForeignKey,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
class Restaurant(Base):
	__tablename__ = "restaurant"
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)

	@property
	def serialize(self):
		return {
			'name': self.name,
			'id': self.id,
			}
class MenuItem(Base):
	__tablename__ = "menu_item"
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	description = Column(String(250))
	price = Column(String(8))
	course = Column(String(250))
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	restaurant = relationship(Restaurant)

	@property
	def serialize(self):
		return {
			'name': self.name,
			'id': self.id,
			'description': self.description,
			'price': self.price,
			'course': self.course,
			}
class User(Base):
	__tablename__ = "user"
	name = Column(String(80),nullable = False)
	id = Column(Integer,primary_key = True)
	password = Column(String(80))
	city = Column(String(250))

class CartItem(Base):
	__tablename__ = "cart"
	user_id = Column(Integer, ForeignKey('user'))
	user = relationship(User)
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	restaurant = relationship(Restaurant)
	menu_id = Column(Integer, ForeignKey('menu_item.id'))
	item = relationship(MenuItem)
	price = Column(String(8))
	quantity = Column(Integer)

class Orders(Base):
	__tablename__ = "orders"
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('user'))
	user = relationship(User)
	time = (TIMESTAMP,server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
	status = (String(80))
class OrderItem(Base):
	__tablename__ = "orderitem"
	order_id = Column(Integer, ForeignKey('orders'))
	orderitem = relationship(Orders)
	user_id = Column(Integer, ForeignKey('user'))
	user = relationship(User)
	menu_id = Column(Integer, ForeignKey('menu_item.id'))
	item = relationship(MenuItem)
	quantity = Column(Integer)
		
engine = create_engine("sqlite:///dinnerorder.db")
Base.metadata.create_all(engine)
