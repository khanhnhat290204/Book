from app.models import User, Book, Bill, Bill_detail, Customer, Comment, Category
from flask_login import current_user
import hashlib
import cloudinary
import cloudinary.uploader
from app import db,app
from sqlalchemy import func
from datetime import datetime

def auth_user(username,password,role=None):
    password=str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),User.password.__eq__(password)).first()

def get_user_by_ID(id):
    return User.query.get(id)

def add_user(name,username,password,avatar=None):
    password=str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u=User(username=username,password=password)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar=res.get('secure_url')
    db.session.add(u)
    db.session.commit()
    id=u.id
    c = Customer(id=id, name=name)
    db.session.add(c)
    db.session.commit()

def load_categories():
    return Category.query.all()

def load_book(id=None,cate_id=None,kw=None,page=1):
    query=Book.query

    if kw:
        return query.filter(Book.name.contains(kw))
    if id:
        return query.get(id)

    page_size=app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    query = query.slice(start,start+page_size)

    return query.all()


def count_book():
    return Book.query.count()

def get_book_quantity(id):
    return Book.query.get(id).quantity

def save_bill(cart,status=None):
    if cart:
        if status:
            b=Bill(customer_id=current_user.id,employee_id=1,status=True)
            db.session.add(b)
        else:
            b = Bill(customer_id=current_user.id, employee_id=1, status=False)
            db.session.add(b)


        for c in cart.values():
            d=Bill_detail(quantity=c['quantity'],price=c['price'],bill=b,book_id=c['id'])
            db.session.add(d)
            print(get_book_quantity(c['id']))
        db.session.commit()

def save_bill_by_em(bill):
    if bill:
        b=Bill(customer_id=2,employee_id=current_user.id,status=True)
        db.session.add(b)

        for c in bill.values():
            d=Bill_detail(quantity=c['quantity'],price=c['price'],bill=b,book_id=c['id'])
            db.session.add(d)
        db.session.commit()

def get_bill(id):
    return Bill.query.get(id)

def load_bill(id=None):
    bill_details=Bill_detail.query.filter(Bill_detail.bill_id==id)
    return bill_details.all()
def get_bookname(book_id):
    book=load_book(book_id)
    return book.name
def add_comment(content, book_id):
    c = Comment(content=content, book_id=book_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c

def load_commments(book_id):
    return Comment.query.filter(Comment.book_id.__eq__(book_id))

def change_bill(book_id):
    bill=get_bill(book_id)
    bill.status=True
    db.session.commit()

def revenue_stats_by_book():
    return db.session.query(Book.id,Book.name, func.sum(Bill_detail.quantity * Bill_detail.price))\
             .join(Bill_detail,Bill_detail.book_id.__eq__(Book.id)).group_by(Book.id).all()

def revenue_stats_by_time(time='month', year=datetime.now().year):
    return db.session.query(func.extract(time, Bill.createdate), func.sum(Bill_detail.quantity * Bill_detail.price))\
             .join(Bill_detail, Bill_detail.bill_id.__eq__(Bill.id)) \
             .group_by(func.extract(time, Bill.createdate)) \
             .filter(func.extract('year', Bill.createdate).__eq__(year)) \
             .order_by(func.extract(time, Bill.createdate)).all()

# def count_book_by_cate():
#     return db.session.query(
#         Category.id,
#         Category.name,
#         func.count(Category_Book.book_id)
#     ).join(
#         Category_Book, Category_Book.category_id.__eq__(Category.id), isouter=True
#     ).group_by(
#         Category.id, Category.name
#     ).all()

# if __name__ == '__main__':
#     with app.app_context():
#         print(count_book_by_cate())







