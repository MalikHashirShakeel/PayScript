from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
import json

#-------------------------------------------------------------

class Sheet(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

#-------------------------------------------------------------

class Customer(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20, validators=[phone_regex])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
#-------------------------------------------------------------

class Product(models.Model):
    sheet = models.ForeignKey(Sheet, related_name='products', on_delete=models.CASCADE)
    serial_no = models.CharField(max_length=100)
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity must be at least 1"
    )
    rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Rate must be positive"
    )
    warranty = models.CharField(max_length=100, blank=True, null=True)
    checked = models.BooleanField(default=False)
    item_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        editable=False,
        default=0.00
    )

    def save(self, *args, **kwargs):
        self.item_total = Decimal(self.quantity) * Decimal(self.rate)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item} (x{self.quantity})"
    
    @property
    def json_data(self):
        return json.dumps({
            'id': self.id,
            'serial_no': self.serial_no,
            'item': self.item,
            'quantity': str(self.quantity),
            'rate': str(self.rate),
            'warranty': self.warranty or '',
            'checked': self.checked,
            'item_total': str(self.item_total),
        })
    
#-------------------------------------------------------------

class InvoiceMeta(models.Model):
    sheet = models.OneToOneField(
        Sheet, 
        related_name='invoice_meta', 
        on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        Customer,
        related_name='invoices',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    date = models.DateField(default=timezone.now)
    terms = models.TextField(
    default="""No Burn and Damage Warranty
No Replacement after Warranty Time
INT = international warranty. Buyer will be the responsible
No warranty for "artifacts", "No display", "Burn", "Damage" for Used GPUs"""
)

    note = models.TextField(
        default="Please verify all items upon receipt. Any discrepancies must be reported immediately."
    )
    
    # Computed fields
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        editable=False
    )
    adjustments = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )
    receivable = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        editable=False
    )
    received = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )
    final_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        editable=False
    )

    def save(self, *args, **kwargs):
        # Calculate subtotal from all products
        self.subtotal = sum(
            Decimal(p.item_total) for p in self.sheet.products.all()
        )
        
        # Calculate other fields
        self.receivable = Decimal(self.subtotal) + Decimal(self.adjustments)
        self.final_balance = Decimal(self.receivable) - Decimal(self.received)

        # Auto-generate invoice number if not set
        if not self.invoice_number:
            last_invoice = InvoiceMeta.objects.order_by('-id').first()
            last_number = int(last_invoice.invoice_number.split('-')[1]) if last_invoice and '-' in last_invoice.invoice_number else 0
            self.invoice_number = f"KK-{str(last_number + 1).zfill(4)}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number
    
#-------------------------------------------------------------