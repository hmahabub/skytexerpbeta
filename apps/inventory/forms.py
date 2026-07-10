from django import forms
from .models import (
    Fabric, FabricRoll, Trim, GoodsReceipt, GoodsReceiptDetail,
    ProductionIssue, ProductionIssueDetail, FinishedGoods,
    FinishedGoodsProduction, Dispatch, DispatchDetail,
    StockMovement, StockAdjustment
)
from datetime import date

class FabricForm(forms.ModelForm):
    class Meta:
        model = Fabric
        fields = ['fabric_code', 'fabric_name', 'fabric_type', 'color', 'gsm',
                 'width', 'supplier', 'unit', 'unit_price', 'reorder_level',
                 'min_stock', 'max_stock', 'description']
        widgets = {
            'fabric_code': forms.TextInput(attrs={'class': 'form-control'}),
            'fabric_name': forms.TextInput(attrs={'class': 'form-control'}),
            'fabric_type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'gsm': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FabricRollForm(forms.ModelForm):
    class Meta:
        model = FabricRoll
        fields = ['roll_number', 'fabric', 'lot_number', 'length', 'location',
                 'rack_number', 'bin_number', 'received_date', 'expiry_date']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'fabric': forms.Select(attrs={'class': 'form-select'}),
            'lot_number': forms.TextInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bin_number': forms.TextInput(attrs={'class': 'form-control'}),
            'received_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class TrimForm(forms.ModelForm):
    class Meta:
        model = Trim
        fields = ['trim_code', 'trim_name', 'trim_type', 'supplier', 'unit',
                 'unit_price', 'reorder_level', 'min_stock', 'max_stock',
                 'color', 'size', 'description']
        widgets = {
            'trim_code': forms.TextInput(attrs={'class': 'form-control'}),
            'trim_name': forms.TextInput(attrs={'class': 'form-control'}),
            'trim_type': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['receipt_number', 'receipt_type', 'purchase_order', 'supplier',
                 'invoice_number', 'invoice_date', 'inspector_name', 'notes']
        widgets = {
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_type': forms.Select(attrs={'class': 'form-select'}),
            'purchase_order': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inspector_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class GoodsReceiptDetailForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptDetail
        fields = ['fabric', 'trim', 'quantity_received', 'quantity_accepted',
                 'quantity_rejected', 'rejection_reason', 'unit_price']
        widgets = {
            'fabric': forms.Select(attrs={'class': 'form-select'}),
            'trim': forms.Select(attrs={'class': 'form-select'}),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_accepted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_rejected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ProductionIssueForm(forms.ModelForm):
    class Meta:
        model = ProductionIssue
        fields = ['issue_number', 'style', 'issue_date', 'department',
                 'production_line', 'notes']
        widgets = {
            'issue_number': forms.TextInput(attrs={'class': 'form-control'}),
            'style': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'production_line': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProductionIssueDetailForm(forms.ModelForm):
    class Meta:
        model = ProductionIssueDetail
        fields = ['fabric', 'fabric_roll', 'trim', 'quantity_requested',
                 'quantity_issued', 'notes']
        widgets = {
            'fabric': forms.Select(attrs={'class': 'form-select'}),
            'fabric_roll': forms.Select(attrs={'class': 'form-select'}),
            'trim': forms.Select(attrs={'class': 'form-select'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_issued': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FinishedGoodsForm(forms.ModelForm):
    class Meta:
        model = FinishedGoods
        fields = ['style', 'sku_code', 'size', 'color', 'unit_price',
                 'warehouse_location', 'rack_location', 'bin_location',
                 'minimum_stock', 'maximum_stock', 'reorder_level', 'description']
        widgets = {
            'style': forms.Select(attrs={'class': 'form-select'}),
            'sku_code': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'warehouse_location': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_location': forms.TextInput(attrs={'class': 'form-control'}),
            'bin_location': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DispatchForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ['dispatch_number', 'style', 'buyer', 'dispatch_date',
                 'total_cartons', 'shipping_line', 'vessel_name', 'vessel_number',
                 'container_number', 'container_size', 'bl_number', 'bl_date',
                 'ex_factory_date', 'shipping_agent', 'notes']
        widgets = {
            'dispatch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'style': forms.Select(attrs={'class': 'form-select'}),
            'buyer': forms.Select(attrs={'class': 'form-select'}),
            'dispatch_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_cartons': forms.NumberInput(attrs={'class': 'form-control'}),
            'shipping_line': forms.TextInput(attrs={'class': 'form-control'}),
            'vessel_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vessel_number': forms.TextInput(attrs={'class': 'form-control'}),
            'container_number': forms.TextInput(attrs={'class': 'form-control'}),
            'container_size': forms.TextInput(attrs={'class': 'form-control'}),
            'bl_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bl_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ex_factory_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shipping_agent': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DispatchDetailForm(forms.ModelForm):
    class Meta:
        model = DispatchDetail
        fields = ['finished_goods', 'carton_number', 'quantity',
                 'carton_weight', 'carton_dimensions', 'notes']
        widgets = {
            'finished_goods': forms.Select(attrs={'class': 'form-select'}),
            'carton_number': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'carton_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carton_dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['adjustment_number', 'adjustment_type', 'fabric', 'fabric_roll',
                 'trim', 'finished_goods', 'adjustment_date', 'quantity',
                 'reason', 'notes']
        widgets = {
            'adjustment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'adjustment_type': forms.Select(attrs={'class': 'form-select'}),
            'fabric': forms.Select(attrs={'class': 'form-select'}),
            'fabric_roll': forms.Select(attrs={'class': 'form-select'}),
            'trim': forms.Select(attrs={'class': 'form-select'}),
            'finished_goods': forms.Select(attrs={'class': 'form-select'}),
            'adjustment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }