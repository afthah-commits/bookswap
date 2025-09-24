from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, SwapRequest, Transaction, Review, Sale
from django.db.models import Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile
from .models import Payment
from .forms import BookForm, ReviewForm, SwapRequestForm, UserProfileForm 



def home(request):
    latest_books = Book.objects.order_by('-created_at')[:5]
    return render(request, 'core/home.html', {'latest_books': latest_books})


def book_list(request):
    books = Book.objects.all()
    return render(request, 'core/book_list.html', {'books': books})


def book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    average_rating = book.reviews.aggregate(Avg('rating'))['rating__avg']
    reviews = book.reviews.all()
    
    if request.method == 'POST' and 'review_submit' in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.reviewer = request.user
            review.save()
            messages.success(request, "Review added!")
            return redirect('book_details', book_id=book_id)
    else:
        form = ReviewForm()
    
    context = {'book': book, 'reviews': reviews, 'average_rating': average_rating, 'form': form}
    return render(request, 'core/book_details.html', context)



@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            messages.success(request, "Book added successfully!")
            return redirect('my_books')
    else:
        form = BookForm()
    return render(request, 'core/book_form.html', {'form': form, })


@login_required
def edit_book(request, id):
    book = get_object_or_404(Book, id=id, owner=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('book_detail', id=id)
    else:
        form = BookForm(instance=book)
    return render(request, 'core/book_form.html', {'form': form, 'title': 'Edit Book'})


@login_required
def delete_book(request, id):
    book = get_object_or_404(Book, id=id, owner=request.user)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('book_list')


@login_required
def request_swap(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = SwapRequestForm(request.POST)
        if form.is_valid():
            swap_request = form.save(commit=False)
            swap_request.requester = request.user
            swap_request.owner = book.owner
            swap_request.requested_book = book
            swap_request.save()
            messages.success(request, "Swap request sent!")
            return redirect('book_detail', id=book_id)
    else:
        form = SwapRequestForm()
    return render(request, 'core/swap_request_form.html', {'form': form, 'book': book})


@login_required
def dashboard(request):
    my_books = Book.objects.filter(owner=request.user)
    my_swaps_sent = SwapRequest.objects.filter(requester=request.user)
    my_swaps_received = SwapRequest.objects.filter(owner=request.user)
    my_purchases = Transaction.objects.filter(buyer=request.user)
    my_sales = Transaction.objects.filter(seller=request.user)
    context = {
        'my_books': my_books,
        'my_swaps_sent': my_swaps_sent,
        'my_swaps_received': my_swaps_received,
        'my_purchases': my_purchases,
        'my_sales': my_sales,
    }
    return render(request, 'core/dashboard.html',{"my_books": my_books})



def user_login(request):
    spans = range(150)  

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('success')  
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'core/login.html', {'spans': spans})




def user_logout(request):
    logout(request) 
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        gpay_number = request.POST.get('gpay_number')
        place = request.POST.get('place')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)

        profile = user.userprofile
        profile.gpay_number = gpay_number
        profile.place = place
        profile.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'core/signup.html')


@login_required
def success(request):
    books = Book.objects.all().order_by('-id')  
    return render(request, 'core/success.html', {'books': books})

@login_required
def my_books(request):
    books = Book.objects.filter(owner=request.user)  
    return render(request, "core/my_books.html", {"books": books})


def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        book.title = request.POST.get("title", book.title)
        book.author = request.POST.get("author", book.author)
        book.genre = request.POST.get("genre", book.genre)
        book.condition = request.POST.get("condition", book.condition)
        book.description = request.POST.get("description", book.description)
        book.availability = request.POST.get("availability", book.availability)

        price = request.POST.get("price")
        book.price = float(price) if price else 0

        if "cover" in request.FILES:
            book.cover = request.FILES["cover"]

        book.save()
        return redirect("my_books")  

    return render(request, "core/edit_book.html", {"book": book})



def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect("my_books")



@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            return redirect('my_books')
    else:
        form = BookForm()
    return render(request, 'core/add_book.html', {'form': form})



@login_required
def swap_request_view(request):
    if request.method == "POST":
        requested_book_id = request.POST.get("requested_book")
        offered_book_id = request.POST.get("offered_book") 
        message = request.POST.get("message", "").strip()

        requested_book = get_object_or_404(Book, id=requested_book_id)

        offered_book = None
        if offered_book_id:
            try:
                offered_book = Book.objects.get(id=int(offered_book_id))
            except (Book.DoesNotExist, ValueError, TypeError):
                offered_book = None 

        SwapRequest.objects.create(
            requester=request.user,
            owner=requested_book.owner,
            requested_book=requested_book,
            offered_book=offered_book,
            message=message
        )

        return redirect("swap_request_view") 

    swap_requests = SwapRequest.objects.filter(requester=request.user).order_by("-created_at")
    user_books = Book.objects.filter(owner=request.user)
    available_books = Book.objects.filter(availability__in=["swap", "both"]).exclude(owner=request.user)

    context = {
        "swap_requests": swap_requests,
        "user_books": user_books,
        "available_books": available_books,
    }
    return render(request, "core/swap_request.html", context)


@login_required
def swap_requests_sent(request):
    swap_requests = SwapRequest.objects.filter(
        requester=request.user
    ).order_by("-created_at")

    return render(request, "core/swap_requests_sent.html", {
        "swap_requests": swap_requests
    })


@login_required
def swap_requests_received(request):
    swap_requests = SwapRequest.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(request, "core/swap_requests_received.html", {
        "swap_requests": swap_requests
    })


@login_required
def swap(request):
    books = Book.objects.filter(availability__in=["swap", "both"]).exclude(owner=request.user)
    return render(request, "core/swap.html", {"books": books})

@login_required
def request_swap(request, book_id):
    requested_book = get_object_or_404(Book, id=book_id)

    user_books = Book.objects.filter(owner=request.user)

    if request.method == "POST":
        offered_book_id = request.POST.get("offered_book")
        message = request.POST.get("message", "").strip()
        mobile_number = request.POST.get("mobile", "").strip() 

        if not offered_book_id:
            messages.error(request, "⚠️ Please select a book to offer for swap.")
            return redirect("request_swap", book_id=book_id)

        offered_book = get_object_or_404(Book, id=offered_book_id, owner=request.user)

        if not mobile_number.isdigit() or not (10 <= len(mobile_number) <= 15):
            messages.error(request, "⚠️ Please enter a valid mobile number.")
            return redirect("request_swap", book_id=book_id)

        SwapRequest.objects.create(
            requester=request.user,
            owner=requested_book.owner,
            requested_book=requested_book,
            offered_book=offered_book,
            message=message if message else None,
            mobile_number=mobile_number,
            status="pending"
        )

        messages.success(request, f"✅ Swap request sent for '{requested_book.title}'!")
        return redirect("swap")

    context = {
        "requested_book": requested_book,
        "user_books": user_books,
    }
    return render(request, "core/request_swap.html", context)


@login_required
def accept_swap(request, swap_id):
    swap = get_object_or_404(SwapRequest, id=swap_id, owner=request.user)

    swap.status = "accepted"
    swap.save()

    if swap.offered_book:
        swap.offered_book.is_sold = True
        swap.offered_book.save()

    buyer_profile, _ = UserProfile.objects.get_or_create(user=swap.requester)
    seller_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    transaction = Transaction.objects.create(
        buyer=swap.requester,
        seller=request.user,
        book=swap.requested_book,
        amount=swap.requested_book.price if swap.requested_book else 0,
        mobile=buyer_profile.gpay_number,
        status="success"
    )

    Sale.objects.create(
        swap_request=swap,
        buyer=buyer_profile,      
        seller=seller_profile,    
        book=swap.requested_book,
        transaction=transaction
    )

    messages.success(request, "Swap accepted successfully!")
    return redirect('swap_requests_received')


@login_required
def reject_swap(request, swap_id):
    swap = get_object_or_404(SwapRequest, id=swap_id, owner=request.user)
    swap.status = "rejected"
    swap.save()
    messages.info(request, "Swap request rejected.")
    return redirect("swap_requests_received")

@login_required
def sell_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user   
            book.availability = "sell" 
            book.save()
            messages.success(request, "✅ Your book has been listed for sale!")
            return redirect('dashboard')  
    else:
        form = BookForm()

    return render(request, "core/sell_book.html", {"form": form})


@login_required
def settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        username = request.POST.get('username'); email = request.POST.get('email'); password = request.POST.get('password')
        if username: request.user.username = username
        if email: request.user.email = email
        if password: request.user.set_password(password); update_session_auth_hash(request, request.user)
        request.user.save()

        profile.gpay_number = request.POST.get('gpay_number'); profile.upi_id = request.POST.get('upi_id'); profile.place = request.POST.get('place')
        avatar = request.FILES.get('avatar'); gpay_qr = request.FILES.get('gpay_qr')
        if avatar: profile.avatar = avatar
        if gpay_qr: profile.gpay_qr = gpay_qr

        profile.save()

        return redirect('settings') 
    context = {'profile': profile}
    return render(request, 'core/settings.html', context)


@login_required
def review(request):
    books = Book.objects.all()
    reviews = Review.objects.select_related("book", "reviewer").order_by("-created_at")

    if request.method == "POST":
        book_id = request.POST.get("book")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if book_id and rating:
            book = Book.objects.get(id=book_id)
            Review.objects.create(
                reviewer=request.user,
                book=book,
                rating=rating,
                comment=comment
            )
            messages.success(request, "✅ Your review has been submitted!")
            return redirect("reviews")

    return render(request, "core/review.html", {"books": books, "reviews": reviews})



@login_required
def purchases(request):
    user_purchases = (
        Payment.objects.filter(
            buyer=request.user,
            status="Verified"
        )
        .select_related("book", "seller__user")  # optimize joins
        .order_by("-created_at")
    )

    context = {
        "purchases": user_purchases
    }
    return render(request, "core/purchases.html", context)



@login_required
def sales(request):
    profile = request.user.profile
    sales = Payment.objects.filter(
        seller=profile,
        status="Verified"
    ).select_related("book", "buyer").order_by("-created_at")

    return render(request, "core/sales.html", {"sales": sales})


@login_required
def verify_payment(request, payment_id):
    seller_profile = request.user.profile
    payment = get_object_or_404(Payment, id=payment_id, seller=seller_profile)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "verify":
            seller_mobile = request.POST.get("mobile", "").strip()

            if not seller_mobile:
                return render(
                    request,
                    "core/verify_payment.html",
                    {
                        "payment": payment,
                        "error": "Please enter your mobile number before verifying."
                    }
                )

            payment.status = "Verified"
            payment.mobile = seller_mobile  

            if payment.book:
                if not payment.amount:
                    payment.amount = payment.book.price
                payment.book.is_sold = True
                payment.book.save()

            payment.save()

            Transaction.objects.create(
                buyer=payment.buyer,
                seller=request.user,   
                book=payment.book,
                amount=payment.amount if payment.amount else 0,
                mobile=payment.mobile,
                status="success"
            )

        elif action == "reject":
            payment.status = "Rejected"
            payment.save()

        return redirect("sales")  

    return render(request, "core/verify_payment.html", {"payment": payment})




@login_required
def purchase(request):
    query = request.GET.get('q', '')  
    books = Book.objects.exclude(owner=request.user)

    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)

    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'core/purchase.html', context)


@login_required
def purchase_book(request, id):
    book = get_object_or_404(Book, id=id)

    if book.owner == request.user:
        messages.error(request, "You cannot purchase your own book!")
        return redirect("core/purchase")

    messages.success(request, f"You have successfully purchased '{book.title}' 🎉")
    return redirect("core/purchase")


@login_required
def buy_book(request, id):
    book = get_object_or_404(Book, id=id)
    seller_profile = getattr(book.owner, "profile", None)

    if book.owner == request.user:
        messages.error(request, "❌ You cannot purchase your own book!")
        return redirect("purchase")  

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        transaction_id = request.POST.get("transaction_id")
        screenshot = request.FILES.get("screenshot")
        mobile = request.user.profile.gpay_number 

        Payment.objects.create(
            buyer=request.user,
            seller=seller_profile,
            book=book,
            payment_method=payment_method,
            transaction_id=transaction_id,
            screenshot=screenshot,
            amount=book.price,
            mobile=mobile,
            status="Pending", 
        )

        messages.success(
            request,
            f"✅ Payment submitted for '{book.title}'. Awaiting seller verification."
        )
        return redirect("payment_success")  

    context = {
        "book": book,
        "seller_profile": seller_profile
    }
    return render(request, "core/buy.html", context)




@login_required
def update_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('settings')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'core/update_profile.html', {'form': form, 'profile': profile})


@login_required
def checkout(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    seller_profile = book.owner.profile  

    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id")
        screenshot = request.FILES.get("screenshot")

        payment = Payment.objects.create(
            buyer=request.user,
            seller=seller_profile,
            book=book,
            upi_id=seller_profile.upi_id,
            gpay_qr=seller_profile.gpay_qr,
            transaction_id=transaction_id,
            screenshot=screenshot,
            status="Pending"
        )
        return redirect("payment_success")

    return render(request, "core/checkout.html", {
        "book": book,
        "seller_profile": seller_profile
    })


@login_required
def seller_payments(request):
    profile = request.user.profile 
    payments = Payment.objects.filter(seller=profile, status="Pending")

    return render(request, "core/seller_payments.html", {
        "payments": payments
    })



@login_required
def payment_success(request):
    return render(request, "core/payment_success.html")





