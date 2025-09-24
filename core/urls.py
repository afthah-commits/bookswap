from django.urls import path
from . import views
from core import views as core_views


urlpatterns = [
    
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_details, name='book_details'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:id>/', views.delete_book, name='delete_book'),
    path('books/<int:book_id>/swap/', views.request_swap, name='request_swap'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('signup/',views.signup,name='signup'),
    path('success/', views.success, name='success'),
    path('my-books/', views.my_books, name='my_books'),
    path("edit_book/<int:book_id>/", views.edit_book, name="edit_book"),
    path("delete_book/<int:book_id>/", views.delete_book, name="delete_book"),
    path('add-book/', views.add_book, name='add_book'),
    path("swap/history/", views.swap_request_view, name="swap_request"),
    path("swap-requests/sent/", views.swap_requests_sent, name="swap_requests_sent"),
    path("swap/received/", views.swap_requests_received, name="swap_requests_received"),
    path("swap/accept/<int:swap_id>/", views.accept_swap, name="accept_swap"),
    path("swap/reject/<int:swap_id>/", views.reject_swap, name="reject_swap"),
    path("sell-book/", views.sell_book, name="sell_book"),
    path("settings/", views.settings, name="settings"),
    path("review/", views.review, name="review"),
    path('purchases/', views.purchases, name='purchases'),
    path('sales/', views.sales, name='sales'),
    path("purchase/", views.purchase, name="purchase"),
    path('purchase/<int:id>/', views.purchase_book, name='purchase_book'),
    path("buy/<int:id>/", views.buy_book, name="buy_book"),
    path("swap/", views.swap, name="swap"),
    path('swap/<int:book_id>/', views.request_swap, name='request_swap'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path("checkout/<int:seller_id>/", views.checkout, name="checkout"),
    path("payments/success/", core_views.payment_success, name="payment_success"),
    path("payments/seller/", core_views.seller_payments, name="seller_payments"),
    path("payments/verify/<int:payment_id>/", views.verify_payment, name="verify_payment"),
    path("payments/success/", views.payment_success, name="payment_success"),
    




]

