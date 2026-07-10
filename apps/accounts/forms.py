from django import forms
from django.contrib.auth.models import User
from .models import (
    ChartOfAccount, Buyer, Supplier, Style, PurchaseOrder, PurchaseOrderItem,
    SalesInvoice, SalesInvoiceItem, Payment, JournalEntry, JournalDetail,
    CostSheet, BankAccount, BankTransaction
)
from datetime import date

class ChartOfAccountForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccount
        fields = ['account_code', 'account_name', 'account_type', 'account_category', 
                 'parent_account', 'opening_balance', 'description']
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1010'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Name'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'account_category': forms.Select(attrs={'class': 'form-select'}),
            'parent_account': forms.Select(attrs={'class': 'form-select'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_account_code(self):
        code = self.cleaned_data.get('account_code')
        if ChartOfAccount.objects.filter(account_code=code).exists():
            if self.instance and self.instance.pk:
                if self.instance.account_code != code:
                    raise forms.ValidationError('Account code already exists.')
            else:
                raise forms.ValidationError('Account code already exists.')
        return code

class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ['buyer_code', 'buyer_name', 'country', 'email', 'phone', 
                 'address', 'credit_limit', 'credit_days']
        widgets = {
            'buyer_code': forms.TextInput(attrs={'class': 'form-control'}),
            'buyer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'credit_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_code', 'supplier_name', 'supplier_type', 'email', 
                 'phone', 'address', 'bank_name', 'bank_account', 'credit_days']
        widgets = {
            'supplier_code': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        fields = ['style_number', 'buyer', 'description', 'order_quantity', 
                 'unit_price', 'cm_charge', 'agent_commission', 'lc_number', 
                 'lc_date', 'order_date', 'delivery_date', 'status']
        widgets = {
            'style_number': forms.TextInput(attrs={'class': 'form-control'}),
            'buyer': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cm_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'agent_commission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lc_number': forms.TextInput(attrs={'class': 'form-control'}),
            'lc_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'supplier', 'style', 'order_date', 'delivery_date',
                 'total_amount', 'discount', 'tax', 'notes']
        widgets = {
            'po_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'style': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        fields = ['invoice_number', 'style', 'buyer', 'invoice_date', 'due_date',
                 'amount', 'discount', 'tax', 'lc_number', 'exchange_rate', 
                 'currency', 'shipping_terms', 'shipping_cost', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'style': forms.Select(attrs={'class': 'form-select'}),
            'buyer': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lc_number': forms.TextInput(attrs={'class': 'form-control'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_number', 'payment_type', 'payment_method', 'buyer',
                 'sales_invoice', 'supplier', 'purchase_order', 'amount',
                 'payment_date', 'reference_number', 'notes']
        widgets = {
            'payment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'buyer': forms.Select(attrs={'class': 'form-select'}),
            'sales_invoice': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'purchase_order': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        
        if payment_type == 'receivable':
            if not cleaned_data.get('buyer') or not cleaned_data.get('sales_invoice'):
                raise forms.ValidationError('For receivable payments, both Buyer and Sales Invoice are required.')
        elif payment_type == 'payable':
            if not cleaned_data.get('supplier') or not cleaned_data.get('purchase_order'):
                raise forms.ValidationError('For payable payments, both Supplier and Purchase Order are required.')
        
        return cleaned_data

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['entry_number', 'journal_type', 'entry_date', 'description', 'reference']
        widgets = {
            'entry_number': forms.TextInput(attrs={'class': 'form-control'}),
            'journal_type': forms.Select(attrs={'class': 'form-select'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

class JournalDetailForm(forms.ModelForm):
    class Meta:
        model = JournalDetail
        fields = ['account', 'debit_amount', 'credit_amount', 'notes']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'debit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'credit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CostSheetForm(forms.ModelForm):
    class Meta:
        model = CostSheet
        fields = ['style', 'cost_date', 'fabric_cost', 'trim_cost', 'packaging_cost',
                 'cutting_labor', 'stitching_labor', 'finishing_labor', 'qc_labor',
                 'factory_overhead', 'administrative_cost', 'selling_cost',
                 'selling_price', 'notes']
        widgets = {
            'style': forms.Select(attrs={'class': 'form-select'}),
            'cost_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fabric_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'trim_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'packaging_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cutting_labor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stitching_labor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'finishing_labor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'qc_labor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'factory_overhead': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'administrative_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['account_name', 'account_number', 'bank_name', 'branch_name',
                 'account_type', 'opening_balance', 'notes']
        widgets = {
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BankTransactionForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ['bank_account', 'transaction_type', 'amount', 'transaction_date',
                 'reference', 'description']
        widgets = {
            'bank_account': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transaction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }