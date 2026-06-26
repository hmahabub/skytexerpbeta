from django.db import models
from django.contrib.auth.models import User

class ChartOfAccount(models.Model):
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
        ('cogs', 'Cost of Goods Sold'),
    ]
    
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"

class Buyer(models.Model):
    buyer_code = models.CharField(max_length=20, unique=True)
    buyer_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return self.buyer_name

class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20, unique=True)
    supplier_name = models.CharField(max_length=200)
    supplier_type = models.CharField(max_length=50, choices=[
        ('fabric', 'Fabric'),
        ('trim', 'Trim'),
        ('both', 'Both')
    ])
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_days = models.IntegerField(default=30)
    
    def __str__(self):
        return self.supplier_name

class Style(models.Model):
    style_number = models.CharField(max_length=50, unique=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    description = models.TextField()
    order_quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    cm_charge = models.DecimalField(max_digits=10, decimal_places=2)
    agent_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fabric_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    trim_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overhead_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lc_number = models.CharField(max_length=100, blank=True)
    lc_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('quotation', 'Quotation'),
        ('order', 'Order Confirmed'),
        ('production', 'In Production'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    ], default='quotation')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.style_number} - {self.buyer.buyer_name}"

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True)
    order_date = models.DateField()
    delivery_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('received', 'Partially Received'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    
    def __str__(self):
        return self.po_number

class SupplierBill(models.Model):
    bill_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], default='unpaid')
    
    def __str__(self):
        return self.bill_number

class SalesInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    lc_number = models.CharField(max_length=100)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], default='pending')
    
    def __str__(self):
        return self.invoice_number

class JournalEntry(models.Model):
    entry_number = models.CharField(max_length=50, unique=True)
    entry_date = models.DateField()
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='journal_entries'  # Add unique related_name
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.entry_number

class JournalDetail(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='details')
    account = models.ForeignKey(ChartOfAccount, on_delete=models.CASCADE)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)