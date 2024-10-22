from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine
from datetime import datetime

# ბაზის შექმნა
Base = declarative_base()

# Product კლასი
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity_in_stock = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.price}, quantity_in_stock={self.quantity_in_stock})>"

# CartItems კლასი
class CartItems(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<CartItem(product_id={self.product_id}, quantity={self.quantity})>"

# Order კლასი
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Order(id={self.id}, order_date={self.order_date}, total_amount={self.total_amount})>"

# OrderItem კლასი
class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)

    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity}, price_per_item={self.price_per_item})>"

# მონაცემთა ბაზის შექმნა და სესიის კონფიგურაცია
user = "postgres"
password = "1234"
host = "localhost"
port = "5432"
database = "postgres"

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# პროდუქტების შეყვანა
def add_products():
    product1 = Product(name="Laptop", price=999.99, quantity_in_stock=10)
    product2 = Product(name="Smartphone", price=499.99, quantity_in_stock=20)
    product3 = Product(name="Headphones", price=99.99, quantity_in_stock=50)
    
    session.add_all([product1, product2, product3])
    session.commit()

    print("პროდუქტები დაემატა მონაცემთა ბაზაში.")

# მომხმარებელზე ორიენტირებული მენიუ
def menu():
    while True:
        print("\n--- მენიუ ---")
        print("1. კალათის ნახვა")
        print("2. პროდუქტების დამატება კალათაში")
        print("3. პროდუქტების ამოშლა კალათიდან")
        print("4. ორდერის გახორციელება")
        print("5. ორდერების ნახვა")
        print("6. პროგრამიდან გასვლა")

        choice = input("აირჩიეთ მოქმედება (1-6): ")

        if choice == '1':
            view_cart()
        elif choice == '2':
            add_to_cart()
        elif choice == '3':
            remove_from_cart()
        elif choice == '4':
            place_order()
        elif choice == '5':
            view_orders()
        elif choice == '6':
            print("პროგრამიდან გასვლა...")
            break
        else:
            print("არასწორი არჩევანი, გთხოვთ სცადოთ თავიდან")

# კალათის ნახვა
def view_cart():
    cart_items = session.query(CartItems).all()
    if not cart_items:
        print("კალათა ცარიელია.")
    else:
        for item in cart_items:
            product = session.query(Product).filter_by(id=item.product_id).first()
            print(f"პროდუქტი: {product.name}, რაოდენობა: {item.quantity}, ფასი: {product.price}")

# პროდუქტების დამატება კალათაში
def add_to_cart():
    product_id = int(input("შეიყვანეთ პროდუქტის ID: "))
    quantity = int(input("შეიყვანეთ რაოდენობა: "))

    product = session.query(Product).filter_by(id=product_id).first()
    if product and product.quantity_in_stock >= quantity:
        cart_item = session.query(CartItems).filter_by(product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItems(product_id=product_id, quantity=quantity)
            session.add(cart_item)
        session.commit()
        print("პროდუქტი დაემატა კალათაში.")
    else:
        print("პროდუქტი არ არის საკმარისი რაოდენობით ან არასწორია ID.")

# პროდუქტების ამოშლა კალათიდან
def remove_from_cart():
    product_id = int(input("შეიყვანეთ პროდუქტის ID ამოსაშლელად: "))
    cart_item = session.query(CartItems).filter_by(product_id=product_id).first()
    if cart_item:
        session.delete(cart_item)
        session.commit()
        print("პროდუქტი ამოღებულია კალათიდან.")
    else:
        print("პროდუქტი ვერ მოიძებნა კალათაში.")

# ორდერის გახორციელება
def place_order():
    cart_items = session.query(CartItems).all()
    if not cart_items:
        print("კალათა ცარიელია.")
        return

    total_amount = 0
    for item in cart_items:
        product = session.query(Product).filter_by(id=item.product_id).first()
        total_amount += product.price * item.quantity

    new_order = Order(total_amount=total_amount)
    session.add(new_order)
    session.commit()

    for item in cart_items:
        product = session.query(Product).filter_by(id=item.product_id).first()
        order_item = OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity, price_per_item=product.price)
        session.add(order_item)

        product.quantity_in_stock -= item.quantity
        session.delete(item)

    session.commit()
    print("ორდერი წარმატებით შეიქმნა.")

# ორდერების ნახვა
def view_orders():
    orders = session.query(Order).all()
    if not orders:
        print("არ არის ორდერები.")
    else:
        for order in orders:
            print(f"ორდერი ID: {order.id}, თარიღი: {order.order_date}, ჯამი: {order.total_amount}")

# პროგრამის გაშვება
if __name__ == "__main__":
    add_products()  
    menu()
