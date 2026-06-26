from django.db import models
# No import from accounts.models - use string references

class Fabric(models.Model):
    fabric_code = models.CharField(max_length=50, unique=True)
    fabric_name = models.CharField(max_length=200)
    color = models.CharField(max_length=50)
    gsm = models.IntegerField()
    width = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey('accounts.Supplier', on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=20, choices=[
        ('meter', 'Meter'),
        ('kg', 'Kilogram'),
        ('yard', 'Yard')
    ], default='meter')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    
    def __str__(self):
        return f"{self.fabric_code} - {self.fabric_name}"

class FabricRoll(models.Model):
    roll_number = models.CharField(max_length=50, unique=True)
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    lot_number = models.CharField(max_length=50)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    used_length = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_length = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('in_stock', 'In Stock'),
        ('issued', 'Issued'),
        ('finished', 'Finished')
    ], default='in_stock')
    received_date = models.DateField()
    
    def save(self, *args, **kwargs):
        self.remaining_length = self.length - self.used_length
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.roll_number

class Trim(models.Model):
    trim_code = models.CharField(max_length=50, unique=True)
    trim_name = models.CharField(max_length=200)
    trim_type = models.CharField(max_length=50, choices=[
        ('thread', 'Thread'),
        ('button', 'Button'),
        ('zipper', 'Zipper'),
        ('label', 'Label'),
        ('elastic', 'Elastic'),
        ('others', 'Others')
    ])
    supplier = models.ForeignKey('accounts.Supplier', on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=500)
    
    def __str__(self):
        return f"{self.trim_code} - {self.trim_name}"

class GoodsReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey('accounts.PurchaseOrder', on_delete=models.CASCADE)
    receipt_date = models.DateField(auto_now_add=True)
    supplier = models.ForeignKey('accounts.Supplier', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rejected_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accepted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quality_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('inspected', 'Inspected'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted')
    ], default='pending')
    inspector_name = models.CharField(max_length=100, blank=True)
    inspection_notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.receipt_number

class GoodsReceiptDetail(models.Model):
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items')
    fabric = models.ForeignKey(Fabric, on_delete=models.SET_NULL, null=True, blank=True)
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    accepted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rejected_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rejection_reason = models.TextField(blank=True)

class ProductionIssue(models.Model):
    issue_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE)
    issue_date = models.DateField()
    issued_by = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.issue_number

class ProductionIssueDetail(models.Model):
    production_issue = models.ForeignKey(ProductionIssue, on_delete=models.CASCADE, related_name='items')
    fabric = models.ForeignKey(Fabric, on_delete=models.SET_NULL, null=True, blank=True)
    fabric_roll = models.ForeignKey(FabricRoll, on_delete=models.SET_NULL, null=True, blank=True)
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2)

class FinishedGoods(models.Model):
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE)
    sku_code = models.CharField(max_length=50, unique=True)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    quantity_produced = models.IntegerField(default=0)
    quantity_in_stock = models.IntegerField(default=0)
    quantity_dispatched = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse_location = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.sku_code} - {self.style.style_number}"

class Dispatch(models.Model):
    dispatch_number = models.CharField(max_length=50, unique=True)
    style = models.ForeignKey('accounts.Style', on_delete=models.CASCADE)
    dispatch_date = models.DateField()
    buyer = models.ForeignKey('accounts.Buyer', on_delete=models.CASCADE)
    total_cartons = models.IntegerField()
    total_quantity = models.IntegerField()
    shipping_line = models.CharField(max_length=200)
    vessel_name = models.CharField(max_length=200, blank=True)
    container_number = models.CharField(max_length=50, blank=True)
    bl_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    ], default='pending')
    
    def __str__(self):
        return self.dispatch_number

class DispatchDetail(models.Model):
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE, related_name='items')
    finished_goods = models.ForeignKey(FinishedGoods, on_delete=models.CASCADE)
    carton_number = models.CharField(max_length=50)
    quantity = models.IntegerField()