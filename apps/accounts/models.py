from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

class ChartOfAccount(models.Model):
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
        ('cogs', 'Cost of Goods Sold'),
    ]
    
    ACCOUNT_CATEGORIES = [
        ('current_asset', 'Current Asset'),
        ('fixed_asset', 'Fixed Asset'),
        ('current_liability', 'Current Liability'),
        ('long_term_liability', 'Long Term Liability'),
        ('income', 'Income'),
        ('direct_expense', 'Direct Expense'),
        ('indirect_expense', 'Indirect Expense'),
    ]
    
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_category = models.CharField(max_length=20, choices=ACCOUNT_CATEGORIES, default='current_asset')
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    def get_balance(self):
        return self.current_balance
    
    def update_balance(self):
        """Update current balance based on journal entries"""
        from .models import JournalDetail
        debit_total = JournalDetail.objects.filter(account=self).aggregate(
            total=models.Sum('debit_amount')
        )['total'] or 0
        
        credit_total = JournalDetail.objects.filter(account=self).aggregate(
            total=models.Sum('credit_amount')
        )['total'] or 0
        
        self.current_balance = self.opening_balance + debit_total - credit_total
        self.save()
        return self.current_balance
    
    class Meta:
        ordering = ['account_code']

class Buyer(models.Model):
    buyer_code = models.CharField(max_length=20, unique=True)
    buyer_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_days = models.IntegerField(default=30)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.buyer_code} - {self.buyer_name}"
    
    def get_outstanding(self):
        """Calculate outstanding balance from invoices"""
        total_invoiced = self.sales_invoices.filter(
            status__in=['pending', 'partial']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        total_paid = self.sales_invoices.filter(
            status='paid'
        ).aggregate(total=models.Sum('paid_amount'))['total'] or 0
        
        self.outstanding_balance = total_invoiced - total_paid
        self.save()
        return self.outstanding_balance

class Supplier(models.Model):
    SUPPLIER_TYPES = [
        ('fabric', 'Fabric Supplier'),
        ('trim', 'Trim Supplier'),
        ('both', 'Both'),
        ('service', 'Service Provider'),
    ]
    
    supplier_code = models.CharField(max_length=20, unique=True)
    supplier_name = models.CharField(max_length=200)
    supplier_type = models.CharField(max_length=20, choices=SUPPLIER_TYPES)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.supplier_code} - {self.supplier_name}"
    
    def get_outstanding(self):
        """Calculate outstanding balance from bills"""
        total_bills = self.purchase_orders.filter(
            status__in=['approved', 'received']
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0
        
        total_paid = self.purchase_orders.filter(
            status='completed'
        ).aggregate(total=models.Sum('advance_paid'))['total'] or 0
        
        self.outstanding_balance = total_bills - total_paid
        self.save()
        return self.outstanding_balance

class Style(models.Model):
    STATUS_CHOICES = [
        ('quotation', 'Quotation'),
        ('order', 'Order Confirmed'),
        ('production', 'In Production'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    style_number = models.CharField(max_length=50, unique=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='styles')
    description = models.TextField()
    order_quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    cm_charge = models.DecimalField(max_digits=10, decimal_places=2)
    agent_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Cost breakdown
    fabric_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    trim_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overhead_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # LC Information
    lc_number = models.CharField(max_length=100, blank=True)
    lc_date = models.DateField(null=True, blank=True)
    lc_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Dates
    order_date = models.DateField()
    delivery_date = models.DateField()
    shipped_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='quotation')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.style_number} - {self.buyer.buyer_name}"
    
    def calculate_profit(self):
        self.total_cost = self.fabric_cost + self.trim_cost + self.labor_cost + self.overhead_cost
        self.profit_margin = ((self.total_value - self.total_cost) / self.total_value) * 100
        self.save()
        return self.profit_margin
    
    class Meta:
        ordering = ['-created_at']

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('received', 'Partially Received'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')
    order_date = models.DateField()
    delivery_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.po_number
    
    def calculate_net_amount(self):
        self.net_amount = self.total_amount - self.discount + self.tax
        self.save()
        return self.net_amount
    
    class Meta:
        ordering = ['-created_at']

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item_description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.item_description}"

class SalesInvoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('pending', 'Pending Payment'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey(Style, on_delete=models.CASCADE, related_name='invoices')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='sales_invoices')
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # LC Information
    lc_number = models.CharField(max_length=100, blank=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    currency = models.CharField(max_length=3, default='USD')
    
    # Shipping
    shipping_terms = models.CharField(max_length=100, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.invoice_number
    
    def calculate_net_amount(self):
        self.net_amount = self.amount - self.discount + self.tax
        self.save()
        return self.net_amount
    
    def is_overdue(self):
        if self.status not in ['paid', 'cancelled'] and date.today() > self.due_date:
            self.status = 'overdue'
            self.save()
            return True
        return False
    
    def get_balance(self):
        return self.net_amount - self.paid_amount
    
    class Meta:
        ordering = ['-created_at']

class SalesInvoiceItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='items')
    item_description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.item_description}"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('receivable', 'Accounts Receivable'),
        ('payable', 'Accounts Payable'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('lc', 'Letter of Credit'),
        ('online', 'Online Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # For Receivables (from buyers)
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments_received')
    sales_invoice = models.ForeignKey(SalesInvoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # For Payables (to suppliers)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments_made')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"
    
    def process_payment(self):
        """Process the payment and update related records"""
        if self.status == 'completed':
            return False
        
        if self.payment_type == 'receivable' and self.sales_invoice:
            self.sales_invoice.paid_amount += self.amount
            if self.sales_invoice.paid_amount >= self.sales_invoice.net_amount:
                self.sales_invoice.status = 'paid'
            else:
                self.sales_invoice.status = 'partial'
            self.sales_invoice.save()
            
            # Update buyer outstanding
            self.buyer.outstanding_balance -= self.amount
            self.buyer.save()
            
        elif self.payment_type == 'payable' and self.purchase_order:
            self.purchase_order.advance_paid += self.amount
            if self.purchase_order.advance_paid >= self.purchase_order.net_amount:
                self.purchase_order.status = 'completed'
            self.purchase_order.save()
            
            # Update supplier outstanding
            self.supplier.outstanding_balance -= self.amount
            self.supplier.save()
        
        self.status = 'completed'
        self.save()
        return True
    
    class Meta:
        ordering = ['-created_at']

class JournalEntry(models.Model):
    JOURNAL_TYPES = [
        ('sale', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('adjustment', 'Adjustment'),
        ('opening', 'Opening Balance'),
        ('closing', 'Closing Entry'),
    ]
    
    entry_number = models.CharField(max_length=50, unique=True)
    journal_type = models.CharField(max_length=20, choices=JOURNAL_TYPES)
    entry_date = models.DateField()
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)  # ID of related document
    is_reversed = models.BooleanField(default=False)
    reversed_entry = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='journal_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.entry_number
    
    def is_balanced(self):
        """Check if debit equals credit"""
        total_debit = self.details.aggregate(total=models.Sum('debit_amount'))['total'] or 0
        total_credit = self.details.aggregate(total=models.Sum('credit_amount'))['total'] or 0
        return total_debit == total_credit
    
    class Meta:
        ordering = ['-entry_date', '-created_at']

class JournalDetail(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='details')
    account = models.ForeignKey(ChartOfAccount, on_delete=models.CASCADE)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.account_name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update account balance
        self.account.update_balance()

class CostSheet(models.Model):
    style = models.ForeignKey(Style, on_delete=models.CASCADE, related_name='cost_sheets')
    cost_date = models.DateField()
    
    # Raw Materials
    fabric_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    trim_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    packaging_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Labor
    cutting_labor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    stitching_labor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    finishing_labor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    qc_labor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Overhead
    factory_overhead = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    administrative_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    selling_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Total
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cost_sheets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cost Sheet - {self.style.style_number} - {self.cost_date}"
    
    def calculate_totals(self):
        material_cost = self.fabric_cost + self.trim_cost + self.packaging_cost
        labor_cost = self.cutting_labor + self.stitching_labor + self.finishing_labor + self.qc_labor
        overhead_cost = self.factory_overhead + self.administrative_cost + self.selling_cost
        
        self.total_cost = material_cost + labor_cost + overhead_cost
        self.profit = self.selling_price - self.total_cost
        self.profit_margin = (self.profit / self.selling_price) * 100 if self.selling_price > 0 else 0
        self.save()
        return self.total_cost
    
    class Meta:
        ordering = ['-created_at']

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('fixed', 'Fixed Deposit'),
    ]
    
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_name} - {self.account_number}"

class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
    ]
    
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    is_reconciled = models.BooleanField(default=False)
    reconciliation_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bank_account.account_name} - {self.transaction_type} - {self.amount}"
    
    def process_transaction(self):
        """Update bank account balance"""
        if self.transaction_type in ['deposit', 'receipt']:
            self.bank_account.current_balance += self.amount
        else:
            self.bank_account.current_balance -= self.amount
        self.bank_account.save()