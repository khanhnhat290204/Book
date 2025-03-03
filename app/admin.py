from sqlalchemy.testing import exclude
from unicodedata import category

from app.models import (Category, Book, User, UserRole, Author)
# , Category_Book)
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from flask_admin._backwards import ObsoleteAttr



class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')
                           # , stats3=dao.count_book_by_cate())



admin = Admin(app=app, name='Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class CategoryView(AdminView):
    column_list = ['name', 'book']


class AuthorView(AdminView):
    column_list = ['name', 'book']

class BookView(AdminView):
    column_list = ['name', 'category', 'author', 'publishinghouse']
    form_columns = ['name', 'image', 'category', 'author', 'price', 'publisher', 'quantity']

class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):

        return self.render('admin/stats.html',
                           stats=dao.revenue_stats_by_book(),
                           stats2=dao.revenue_stats_by_time())


admin.add_view(AuthorView(Author, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(BookView(Book, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
