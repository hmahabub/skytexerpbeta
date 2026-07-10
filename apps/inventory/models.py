from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

class Fabric(models.Model):
    """Fabric master data"""
    FABRIC_TYPES = [
        ('cotton', 'Cotton'),
        ('polyester', 'Polyester'),
        ('denim', 'Denim'),
        ('silk', 'Silk'),
        ('wool', 'Wool'),
        ('linen', 'Linen'),
        ('blend', 'Blend'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('meter', 'Meter'),
        ('kg', 'Kilogram'),
        ('yard', 'Yard'),
        ('roll', 'Roll'),
    ]
    
    fabric_code = models.CharField(max_length=50, unique=True)
    fabric_name = models.CharField(max_length=200)
    fabric_type = models.CharField(max_length=20, choices=FABRIC_TYPES, default='cotton')
    color = models.CharField(max_length=50)
    gsm = models.IntegerField(help_text="Grams per square meter")
    width = models.DecimalField(max_digits=10, decimal_places=2, help_text="Width in inches")
    supplier = models.ForeignKey('accounts.Supplier', on_delete=models.SET_NULL, null=True, related_name='fabrics')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='meter')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_stock = models.DecimalField(max_digits=10, decimal_places=2, default=99999)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.fabric_code} - {self.fabric_name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level
    
    @property
    def stock_status(self):
        if self.current_stock <= self.reorder_level:
            return 'Low'
        elif self.current_stock >= self.max_stock:
            return 'Overstock'
        else:
            return 'Normal'
    
    class Meta:
        ordering = ['fabric_code']

class FabricRoll(models.Model):
    """Individual fabric rolls with tracking"""
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('issued', 'Issued to Production'),
        ('finished', 'Fully Used'),
        ('damaged', 'Damaged'),
        ('returned', 'Returned to Supplier'),
    ]
    
    roll_number = models.CharField(max_length=50, unique=True)
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE, related_name='rolls')
    lot_number = models.CharField(max_length=50)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    used_length = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_length = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    rack_number = models.CharField(max_length=50, blank=True)
    bin_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_stock')
    received_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    quality_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Inspection'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], default='pending')
    inspector_name = models.CharField(max_length=100, blank=True)
    inspection_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.remaining_length = self.length - self.used_length
        if self.remaining_length <= 0:
            self.status = 'finished'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.roll_number} - {self.fabric.fabric_name} ({self.remaining_length} {self.fabric.unit})"
    
    @property
    def utilization_percentage(self):
        if self.length > 0:
            return (self.used_length / self.length) * 100
        return 0
    
    class Meta:
        ordering = ['-received_date']

class Trim(models.Model):
    """Trim items like buttons, zippers, threads, etc."""
    TRIM_TYPES = [
        ('thread', 'Thread'),
        ('button', 'Button'),
        ('zipper', 'Zipper'),
        ('label', 'Label'),
        ('elastic', 'Elastic'),
        ('ribbon', 'Ribbon'),
        ('lace', 'Lace'),
        ('tag', 'Tag'),
        ('hook', 'Hook & Loop'),
        ('other', 'Other'),
    ]
    
    trim_code = models.CharField(max_length=50, unique=True)
    trim_name = models.CharField(max_length=200)
    trim_type = models.CharField(max_length=20, choices=TRIM_TYPES)
    supplier = models.ForeignKey('accounts.Supplier', on_delete=models.SET_NULL, null=True, related_name='trims')
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=500)
    min_stock = models.IntegerField(default=0)
    max_stock = models.IntegerField(default=99999)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.trim_code} - {self.trim_name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level
    
    @property
    def stock_status(self):
        if self.current_stock <= self.reorder_level:
            return 'Low'
        elif self.current_stock >= self.max_stock:
            return 'Overstock'
        else:
            return 'Normal'
    
    class Meta:
        ordering = ['trim_code']

class GoodsReceipt(models.Model):
    """Goods receipt from suppliers"""
    RECEIPT_TYPES = [
        ('fabric', 'Fabric Receipt'),
        ('trim', 'Trim Receipt'),
        ('both', 'Both'),
    ]
    
    QUALITY_STATUS = [
        ('pending', 'Pending Inspection'),
        ('inspected', 'Inspected'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Accepted'),
    ]
    
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_type = models.CharField(max_length=20, choices=RECEIPT_TYPES)
    purchase_order = models.ForeignKey('accounts.PurchaseOrder', on_delete=models.CASCADE, related_name='receipts')
    supplier = models.ForeignKey('accounts.Supplier', on_delete=models.CASCADE, related_name='receipts')
    receipt_date = models.DateField(auto_now_add=True)
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField(null=True, blank=True)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rejected_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accepted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quality_status = models.CharField(max_length=20, choices=QUALITY_STATUS, default='pending')
    inspector_name = models.CharField(max_length=100, blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    inspection_notes = models.TextField(blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_goods')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.receipt_number} - {self.supplier.supplier_name}"
    
    @property
    def acceptance_rate(self):
        if self.total_quantity > 0:
            return (self.accepted_quantity / self.total_quantity) * 100
        return 0
    
    class Meta:
        ordering = ['-receipt_date']

class GoodsReceiptDetail(models.Model):
    """Items in goods receipt"""
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items')
    fabric = models.ForeignKey(Fabric, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipt_items')
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipt_items')
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_accepted = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_rejected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rejection_reason = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity_accepted * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        item_name = self.fabric.fabric_name if self.fabric else self.trim.trim_name if self.trim else "Unknown"
        return f"{self.goods_receipt.receipt_number} - {item_name}"

class ProductionIssue(models.Model):
    """Issue materials to production"""
    issue_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE, related_name='issues')
    issue_date = models.DateField()
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_materials')
    department = models.ForeignKey('hr.Department', on_delete=models.SET_NULL, null=True, related_name='issues')
    production_line = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('partially_used', 'Partially Used'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.issue_number} - {self.style.style_number}"
    
    class Meta:
        ordering = ['-issue_date']

class ProductionIssueDetail(models.Model):
    """Items in production issue"""
    production_issue = models.ForeignKey(ProductionIssue, on_delete=models.CASCADE, related_name='items')
    fabric = models.ForeignKey(Fabric, on_delete=models.SET_NULL, null=True, blank=True, related_name='issue_items')
    fabric_roll = models.ForeignKey(FabricRoll, on_delete=models.SET_NULL, null=True, blank=True, related_name='issue_items')
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True, related_name='issue_items')
    quantity_requested = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_issued = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_returned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waste_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    @property
    def is_completed(self):
        return self.quantity_issued <= (self.quantity_used + self.quantity_returned + self.waste_quantity)
    
    def __str__(self):
        item_name = self.fabric.fabric_name if self.fabric else self.trim.trim_name if self.trim else "Unknown"
        return f"{self.production_issue.issue_number} - {item_name}"

class FinishedGoods(models.Model):
    """Finished goods inventory"""
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE, related_name='finished_goods')
    sku_code = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    quantity_produced = models.IntegerField(default=0)
    quantity_in_stock = models.IntegerField(default=0)
    quantity_dispatched = models.IntegerField(default=0)
    quantity_defective = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse_location = models.CharField(max_length=100)
    rack_location = models.CharField(max_length=50, blank=True)
    bin_location = models.CharField(max_length=50, blank=True)
    minimum_stock = models.IntegerField(default=0)
    maximum_stock = models.IntegerField(default=99999)
    reorder_level = models.IntegerField(default=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sku_code} - {self.style.style_number} ({self.size} - {self.color})"
    
    @property
    def available_stock(self):
        return self.quantity_in_stock
    
    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level
    
    class Meta:
        ordering = ['style__style_number', 'size', 'color']

class FinishedGoodsProduction(models.Model):
    """Production batch for finished goods"""
    batch_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE, related_name='production_batches')
    finished_goods = models.ForeignKey(FinishedGoods, on_delete=models.CASCADE, related_name='production_batches')
    production_date = models.DateField()
    quantity_produced = models.IntegerField()
    quantity_defective = models.IntegerField(default=0)
    quantity_good = models.IntegerField()
    production_line = models.CharField(max_length=50)
    supervisor = models.CharField(max_length=100)
    quality_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending QC'),
        ('passed', 'Passed'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Passed'),
    ], default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='batches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.quantity_good = self.quantity_produced - self.quantity_defective
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.batch_number} - {self.style.style_number}"
    
    @property
    def quality_rate(self):
        if self.quantity_produced > 0:
            return (self.quantity_good / self.quantity_produced) * 100
        return 0
    
    class Meta:
        ordering = ['-production_date']

class Dispatch(models.Model):
    """Dispatch finished goods to buyers"""
    dispatch_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE, related_name='dispatches')
    buyer = models.ForeignKey('accounts.Buyer', on_delete=models.CASCADE, related_name='dispatches')
    dispatch_date = models.DateField()
    total_cartons = models.IntegerField()
    total_quantity = models.IntegerField()
    shipping_line = models.CharField(max_length=200)
    vessel_name = models.CharField(max_length=200, blank=True)
    vessel_number = models.CharField(max_length=100, blank=True)
    container_number = models.CharField(max_length=50, blank=True)
    container_size = models.CharField(max_length=20, blank=True)
    bl_number = models.CharField(max_length=100, blank=True)
    bl_date = models.DateField(null=True, blank=True)
    ex_factory_date = models.DateField(null=True, blank=True)
    shipping_agent = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dispatches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.dispatch_number} - {self.buyer.buyer_name}"
    
    class Meta:
        ordering = ['-dispatch_date']

class DispatchDetail(models.Model):
    """Items in dispatch"""
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE, related_name='items')
    finished_goods = models.ForeignKey(FinishedGoods, on_delete=models.CASCADE, related_name='dispatch_items')
    carton_number = models.CharField(max_length=50)
    quantity = models.IntegerField()
    carton_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    carton_dimensions = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.dispatch.dispatch_number} - {self.finished_goods.sku_code}"

class StockMovement(models.Model):
    """Track all stock movements"""
    MOVEMENT_TYPES = [
        ('receipt', 'Goods Receipt'),
        ('issue', 'Production Issue'),
        ('return', 'Return to Store'),
        ('adjustment', 'Stock Adjustment'),
        ('transfer', 'Transfer Between Locations'),
        ('dispatch', 'Dispatch to Buyer'),
    ]
    
    movement_number = models.CharField(max_length=50, unique=True)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference_number = models.CharField(max_length=100)
    reference_id = models.IntegerField()
    fabric = models.ForeignKey(Fabric, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    fabric_roll = models.ForeignKey(FabricRoll, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    finished_goods = models.ForeignKey(FinishedGoods, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    from_location = models.CharField(max_length=100, blank=True)
    to_location = models.CharField(max_length=100, blank=True)
    movement_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.movement_number} - {self.movement_type}"

class StockAdjustment(models.Model):
    """Stock adjustments for inventory correction"""
    ADJUSTMENT_TYPES = [
        ('damage', 'Damage Write-off'),
        ('expired', 'Expired Stock'),
        ('qc_failure', 'QC Failure'),
        ('recount', 'Recount Adjustment'),
        ('return', 'Return to Supplier'),
        ('other', 'Other'),
    ]
    
    adjustment_number = models.CharField(max_length=50, unique=True)
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    fabric = models.ForeignKey(Fabric, on_delete=models.SET_NULL, null=True, blank=True, related_name='adjustments')
    fabric_roll = models.ForeignKey(FabricRoll, on_delete=models.SET_NULL, null=True, blank=True, related_name='adjustments')
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True, related_name='adjustments')
    finished_goods = models.ForeignKey(FinishedGoods, on_delete=models.SET_NULL, null=True, blank=True, related_name='adjustments')
    adjustment_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_adjustments')
    approved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_adjustments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.adjustment_number} - {self.adjustment_type}"