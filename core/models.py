from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver


class Book(models.Model):
    AVAILABILITY_CHOICES = [("swap", "Swap"), ("sell", "Sell"), ("both", "Both")]
    CONDITION_CHOICES = [("new", "New"), ("used", "Used")]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default="used")
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="book_covers/", blank=True, null=True)
    availability = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, default="swap")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.author})"



class SwapRequest(models.Model):

    STATUS_CHOICES = [("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_swap_requests") 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_swap_requests") 
    requested_book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="requested_in_swaps") 
    offered_book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="offered_in_swaps", null=True, blank=True) 
    message = models.TextField(blank=True, null=True) 
    mobile_number = models.CharField(max_length=15, blank=True, null=True, help_text="Requester's mobile number for contact")  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")  
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Swap: {self.requester.username} → {self.requested_book.title} [{self.status}]"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("success", "Success"),
        ("failed", "Failed")
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_purchased")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_sold")
    book = models.ForeignKey("core.Book", on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="initiated")
    mobile = models.CharField(max_length=20, blank=True, null=True)  # Added mobile field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} – {self.buyer.username} paid {self.amount} ({self.status})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    gpay_number = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    gpay_qr = models.ImageField(upload_to="gpay_qr/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Sale(models.Model):
    transaction = models.OneToOneField("Transaction", on_delete=models.CASCADE, related_name="sale", null=True, blank=True)
    buyer = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="purchases", null=True, blank=True)
    seller = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="completed_sales", null=True, blank=True)
    book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True, blank=True)
    swap_request = models.ForeignKey("SwapRequest", on_delete=models.SET_NULL, null=True, blank=True, related_name="sale")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.book.title if self.book else 'N/A'} to {self.buyer.user.username if self.buyer else 'N/A'}"




class Payment(models.Model):
    """Stores payment records for book purchases."""

    PAYMENT_METHOD_CHOICES = [("GPay", "Google Pay"), ("PhonePe", "PhonePe"), ("Paytm", "Paytm"), ("Other", "Other")]
    STATUS_CHOICES = [("Pending", "Pending"), ("Verified", "Verified"), ("Rejected", "Rejected")]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", help_text="User who made the payment")
    seller = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="payments_received", help_text="Seller (UserProfile) receiving the payment")
    book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True, blank=True, help_text="Book being purchased")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="The price paid for the book")
    mobile = models.CharField(max_length=15, blank=True, null=True, help_text="Buyer's mobile number for seller contact")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default="GPay", help_text="Selected payment method")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction ID / UPI reference")
    screenshot = models.ImageField(upload_to="payments/screenshots/", blank=True, null=True, help_text="Optional payment screenshot")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending", help_text="Current status of the payment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        book_title = self.book.title if self.book else "Unknown Book"
        return f"{self.buyer.username} → {self.seller.user.username} | {book_title} | {self.status}"

    @property
    def is_verified(self): return self.status == "Verified"

    @property
    def is_pending(self): return self.status == "Pending"

    @property
    def is_rejected(self): return self.status == "Rejected"


class Review(models.Model):
    book = models.ForeignKey(Book, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.book.title} ({self.rating}⭐)"

