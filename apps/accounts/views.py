from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
import csv
from decimal import Decimal

from .models import (
    ChartOfAccount, Buyer, Supplier, Style, PurchaseOrder, PurchaseOrderItem,
    SalesInvoice, SalesInvoiceItem, Payment, JournalEntry, JournalDetail,
    CostSheet, BankAccount, BankTransaction
)
from .forms import (
    ChartOfAccountForm, BuyerForm, SupplierForm, StyleForm, PurchaseOrderForm,
    SalesInvoiceForm, PaymentForm, JournalEntryForm, JournalDetailForm,
    CostSheetForm, BankAccountForm, BankTransactionForm
)

# Helper function for role-based access
def is_accounts_or_admin(user):
    return user.is_superuser or user.groups.filter(name='Accounts').exists()

@login_required
def accounts_dashboard(request):
    """Accounts Dashboard Overview"""
    context = {
        'active': 'accounts',
        'page_title': 'Accounts Dashboard',
    }
    
    # Financial Summary
    context['total_buyers'] = Buyer.objects.filter(is_active=True).count()
    context['total_suppliers'] = Supplier.objects.filter(is_active=True).count()
    context['total_styles'] = Style.objects.filter(is_active=True).count()
    
    # Sales Summary
    current_month = date.today().month
    current_year = date.today().year
    
    monthly_sales = SalesInvoice.objects.filter(
        invoice_date__month=current_month,
        invoice_date__year=current_year,
        status='paid'
    ).aggregate(total=Sum('net_amount'))['total'] or 0
    context['monthly_sales'] = monthly_sales
    
    # Receivables
    receivables = SalesInvoice.objects.filter(
        status__in=['pending', 'partial', 'overdue']
    ).aggregate(total=Sum('net_amount') - Sum('paid_amount'))['total'] or 0
    context['receivables'] = receivables
    
    # Payables
    payables = PurchaseOrder.objects.filter(
        status__in=['approved', 'received']
    ).aggregate(total=Sum('net_amount') - Sum('advance_paid'))['total'] or 0
    context['payables'] = payables
    
    # Cash Balance
    context['cash_balance'] = BankAccount.objects.aggregate(
        total=Sum('current_balance')
    )['total'] or 0
    
    # Recent Transactions
    context['recent_invoices'] = SalesInvoice.objects.select_related('buyer').order_by('-created_at')[:5]
    context['recent_payments'] = Payment.objects.select_related('buyer', 'supplier').order_by('-created_at')[:5]
    
    # Chart Data - Monthly Sales
    monthly_sales_data = []
    months = []
    for i in range(5, -1, -1):
        month = date.today().month - i
        year = date.today().year
        if month <= 0:
            month += 12
            year -= 1
        total = SalesInvoice.objects.filter(
            invoice_date__month=month,
            invoice_date__year=year,
            status='paid'
        ).aggregate(total=Sum('net_amount'))['total'] or 0
        monthly_sales_data.append(float(total))
        months.append(date(year, month, 1).strftime('%B'))
    
    context['monthly_sales_data'] = monthly_sales_data
    context['months'] = months
    
    # Overdue Invoices
    overdue_invoices = SalesInvoice.objects.filter(
        status='overdue'
    ).count()
    context['overdue_invoices'] = overdue_invoices
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def chart_of_accounts(request):
    """Chart of Accounts management"""
    accounts = ChartOfAccount.objects.filter(is_active=True).select_related('parent_account')
    
    # Filter by type
    account_type = request.GET.get('type')
    if account_type:
        accounts = accounts.filter(account_type=account_type)
    
    context = {
        'active': 'accounts',
        'page_title': 'Chart of Accounts',
        'accounts': accounts,
        'account_types': ChartOfAccount.ACCOUNT_TYPES,
        'current_type': account_type,
    }
    return render(request, 'accounts/chart_of_accounts.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_account(request):
    """Add new account"""
    if request.method == 'POST':
        form = ChartOfAccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Account "{account.account_name}" created successfully!')
            return redirect('accounts:chart_of_accounts')
    else:
        form = ChartOfAccountForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Account',
        'form': form,
    }
    return render(request, 'accounts/account_form.html', context)

@login_required
def buyers_list(request):
    """List all buyers"""
    buyers = Buyer.objects.filter(is_active=True)
    
    search = request.GET.get('search')
    if search:
        buyers = buyers.filter(
            Q(buyer_name__icontains=search) |
            Q(buyer_code__icontains=search) |
            Q(country__icontains=search)
        )
    
    context = {
        'active': 'accounts',
        'page_title': 'Buyers',
        'buyers': buyers,
        'search': search,
    }
    return render(request, 'accounts/buyers_list.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_buyer(request):
    """Add new buyer"""
    if request.method == 'POST':
        form = BuyerForm(request.POST)
        if form.is_valid():
            buyer = form.save()
            messages.success(request, f'Buyer "{buyer.buyer_name}" added successfully!')
            return redirect('accounts:buyers_list')
    else:
        form = BuyerForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Buyer',
        'form': form,
    }
    return render(request, 'accounts/buyer_form.html', context)

@login_required
def suppliers_list(request):
    """List all suppliers"""
    suppliers = Supplier.objects.filter(is_active=True)
    
    search = request.GET.get('search')
    if search:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=search) |
            Q(supplier_code__icontains=search)
        )
    
    context = {
        'active': 'accounts',
        'page_title': 'Suppliers',
        'suppliers': suppliers,
        'search': search,
    }
    return render(request, 'accounts/suppliers_list.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_supplier(request):
    """Add new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.supplier_name}" added successfully!')
            return redirect('accounts:suppliers_list')
    else:
        form = SupplierForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Supplier',
        'form': form,
    }
    return render(request, 'accounts/supplier_form.html', context)

@login_required
def styles_list(request):
    """List all styles"""
    styles = Style.objects.select_related('buyer').all()
    
    status = request.GET.get('status')
    if status:
        styles = styles.filter(status=status)
    
    buyer = request.GET.get('buyer')
    if buyer:
        styles = styles.filter(buyer_id=buyer)
    
    context = {
        'active': 'accounts',
        'page_title': 'Styles',
        'styles': styles,
        'statuses': Style.STATUS_CHOICES,
        'buyers': Buyer.objects.filter(is_active=True),
        'current_status': status,
        'current_buyer': buyer,
    }
    return render(request, 'accounts/styles_list.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_style(request):
    """Add new style"""
    if request.method == 'POST':
        form = StyleForm(request.POST)
        if form.is_valid():
            style = form.save()
            messages.success(request, f'Style "{style.style_number}" created successfully!')
            return redirect('accounts:styles_list')
    else:
        form = StyleForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Style',
        'form': form,
    }
    return render(request, 'accounts/style_form.html', context)

@login_required
def invoices_list(request):
    """List all invoices"""
    invoices = SalesInvoice.objects.select_related('buyer', 'style').all()
    
    status = request.GET.get('status')
    if status:
        invoices = invoices.filter(status=status)
    
    buyer = request.GET.get('buyer')
    if buyer:
        invoices = invoices.filter(buyer_id=buyer)
    
    context = {
        'active': 'accounts',
        'page_title': 'Sales Invoices',
        'invoices': invoices,
        'statuses': SalesInvoice.STATUS_CHOICES,
        'buyers': Buyer.objects.filter(is_active=True),
        'current_status': status,
        'current_buyer': buyer,
    }
    return render(request, 'accounts/invoices_list.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_invoice(request):
    """Add new invoice"""
    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            
            # Create journal entry
            create_sales_journal_entry(invoice)
            
            messages.success(request, f'Invoice "{invoice.invoice_number}" created successfully!')
            return redirect('accounts:invoice_detail', pk=invoice.pk)
    else:
        form = SalesInvoiceForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Create Invoice',
        'form': form,
    }
    return render(request, 'accounts/invoice_form.html', context)

@login_required
def invoice_detail(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    
    context = {
        'active': 'accounts',
        'page_title': f'Invoice - {invoice.invoice_number}',
        'invoice': invoice,
        'balance': invoice.get_balance(),
    }
    return render(request, 'accounts/invoice_detail.html', context)

@login_required
def payments_list(request):
    """List all payments"""
    payments = Payment.objects.select_related('buyer', 'supplier').all()
    
    payment_type = request.GET.get('type')
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    
    context = {
        'active': 'accounts',
        'page_title': 'Payments',
        'payments': payments,
        'payment_types': Payment.PAYMENT_TYPES,
        'current_type': payment_type,
    }
    return render(request, 'accounts/payments_list.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_payment(request):
    """Add new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            
            # Process the payment
            payment.process_payment()
            
            # Create journal entry
            create_payment_journal_entry(payment)
            
            messages.success(request, f'Payment "{payment.payment_number}" processed successfully!')
            return redirect('accounts:payments_list')
    else:
        form = PaymentForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Payment',
        'form': form,
    }
    return render(request, 'accounts/payment_form.html', context)

@login_required
def journal_entries(request):
    """List all journal entries"""
    entries = JournalEntry.objects.select_related('created_by').all()
    
    entry_type = request.GET.get('type')
    if entry_type:
        entries = entries.filter(journal_type=entry_type)
    
    context = {
        'active': 'accounts',
        'page_title': 'Journal Entries',
        'entries': entries,
        'journal_types': JournalEntry.JOURNAL_TYPES,
        'current_type': entry_type,
    }
    return render(request, 'accounts/journal_entries.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_journal_entry(request):
    """Add new journal entry"""
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
            
            # Handle journal details from form
            account_ids = request.POST.getlist('account_ids[]')
            debit_amounts = request.POST.getlist('debit_amounts[]')
            credit_amounts = request.POST.getlist('credit_amounts[]')
            notes = request.POST.getlist('notes[]')
            
            for i in range(len(account_ids)):
                if account_ids[i]:
                    JournalDetail.objects.create(
                        journal_entry=entry,
                        account_id=int(account_ids[i]),
                        debit_amount=Decimal(debit_amounts[i] or 0),
                        credit_amount=Decimal(credit_amounts[i] or 0),
                        notes=notes[i] if i < len(notes) else ''
                    )
            
            if entry.is_balanced():
                messages.success(request, f'Journal entry "{entry.entry_number}" created successfully!')
            else:
                messages.warning(request, 'Journal entry created but is not balanced!')
            
            return redirect('accounts:journal_entries')
    else:
        form = JournalEntryForm()
    
    accounts = ChartOfAccount.objects.filter(is_active=True)
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Journal Entry',
        'form': form,
        'accounts': accounts,
    }
    return render(request, 'accounts/journal_entry_form.html', context)

@login_required
def cost_sheets(request):
    """List all cost sheets"""
    cost_sheets = CostSheet.objects.select_related('style', 'created_by').all()
    
    style = request.GET.get('style')
    if style:
        cost_sheets = cost_sheets.filter(style_id=style)
    
    context = {
        'active': 'accounts',
        'page_title': 'Cost Sheets',
        'cost_sheets': cost_sheets,
        'styles': Style.objects.filter(is_active=True),
        'current_style': style,
    }
    return render(request, 'accounts/cost_sheets.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_cost_sheet(request):
    """Add new cost sheet"""
    if request.method == 'POST':
        form = CostSheetForm(request.POST)
        if form.is_valid():
            cost_sheet = form.save(commit=False)
            cost_sheet.created_by = request.user
            cost_sheet.save()
            cost_sheet.calculate_totals()
            
            messages.success(request, f'Cost sheet for "{cost_sheet.style.style_number}" created successfully!')
            return redirect('accounts:cost_sheets')
    else:
        form = CostSheetForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Cost Sheet',
        'form': form,
    }
    return render(request, 'accounts/cost_sheet_form.html', context)

@login_required
def banks_list(request):
    """List all bank accounts"""
    banks = BankAccount.objects.filter(is_active=True)
    
    context = {
        'active': 'accounts',
        'page_title': 'Bank Accounts',
        'banks': banks,
    }
    return render(request, 'accounts/banks_list.html', context)

@login_required
@user_passes_test(is_accounts_or_admin)
def add_bank(request):
    """Add new bank account"""
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank = form.save()
            messages.success(request, f'Bank account "{bank.account_name}" added successfully!')
            return redirect('accounts:banks_list')
    else:
        form = BankAccountForm()
    
    context = {
        'active': 'accounts',
        'page_title': 'Add Bank Account',
        'form': form,
    }
    return render(request, 'accounts/bank_form.html', context)

@login_required
def financial_reports(request):
    """Financial reports dashboard"""
    context = {
        'active': 'accounts',
        'page_title': 'Financial Reports',
    }
    
    # Income Statement
    current_month = date.today().month
    current_year = date.today().year
    
    # Revenue
    total_revenue = SalesInvoice.objects.filter(
        status='paid',
        invoice_date__month=current_month,
        invoice_date__year=current_year
    ).aggregate(total=Sum('net_amount'))['total'] or 0
    
    # Cost of Goods Sold
    total_cogs = CostSheet.objects.filter(
        cost_date__month=current_month,
        cost_date__year=current_year
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    # Gross Profit
    gross_profit = total_revenue - total_cogs
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    context['total_revenue'] = total_revenue
    context['total_cogs'] = total_cogs
    context['gross_profit'] = gross_profit
    context['gross_margin'] = gross_margin
    
    # Balance Sheet
    total_assets = ChartOfAccount.objects.filter(
        account_type='asset'
    ).aggregate(total=Sum('current_balance'))['total'] or 0
    
    total_liabilities = ChartOfAccount.objects.filter(
        account_type='liability'
    ).aggregate(total=Sum('current_balance'))['total'] or 0
    
    total_equity = ChartOfAccount.objects.filter(
        account_type='equity'
    ).aggregate(total=Sum('current_balance'))['total'] or 0
    
    context['total_assets'] = total_assets
    context['total_liabilities'] = total_liabilities
    context['total_equity'] = total_equity
    
    return render(request, 'accounts/financial_reports.html', context)

# Helper Functions

def create_sales_journal_entry(invoice):
    """Create journal entry for sales invoice"""
    entry_number = f"JE-S{invoice.id:06d}"
    
    entry = JournalEntry.objects.create(
        entry_number=entry_number,
        journal_type='sale',
        entry_date=invoice.invoice_date,
        description=f"Sales invoice {invoice.invoice_number} - {invoice.buyer.buyer_name}",
        reference=invoice.invoice_number,
        reference_id=invoice.id,
        created_by=invoice.created_by
    )
    
    # Get accounts
    receivable_account = ChartOfAccount.objects.get(account_code='1200')  # Accounts Receivable
    revenue_account = ChartOfAccount.objects.get(account_code='4000')  # Sales Revenue
    
    # Create journal details
    JournalDetail.objects.create(
        journal_entry=entry,
        account=receivable_account,
        debit_amount=invoice.net_amount,
        credit_amount=0,
        notes=f"Invoice {invoice.invoice_number}"
    )
    
    JournalDetail.objects.create(
        journal_entry=entry,
        account=revenue_account,
        debit_amount=0,
        credit_amount=invoice.net_amount,
        notes=f"Invoice {invoice.invoice_number}"
    )
    
    return entry

def create_payment_journal_entry(payment):
    """Create journal entry for payment"""
    entry_number = f"JE-P{payment.id:06d}"
    
    entry = JournalEntry.objects.create(
        entry_number=entry_number,
        journal_type='payment',
        entry_date=payment.payment_date,
        description=f"Payment {payment.payment_number}",
        reference=payment.payment_number,
        reference_id=payment.id,
        created_by=payment.created_by
    )
    
    if payment.payment_type == 'receivable':
        # For receivable payments
        cash_account = ChartOfAccount.objects.get(account_code='1100')  # Cash
        receivable_account = ChartOfAccount.objects.get(account_code='1200')  # Accounts Receivable
        
        JournalDetail.objects.create(
            journal_entry=entry,
            account=cash_account,
            debit_amount=payment.amount,
            credit_amount=0,
            notes=f"Payment {payment.payment_number}"
        )
        
        JournalDetail.objects.create(
            journal_entry=entry,
            account=receivable_account,
            debit_amount=0,
            credit_amount=payment.amount,
            notes=f"Payment {payment.payment_number}"
        )
    
    elif payment.payment_type == 'payable':
        # For payable payments
        cash_account = ChartOfAccount.objects.get(account_code='1100')  # Cash
        payable_account = ChartOfAccount.objects.get(account_code='2200')  # Accounts Payable
        
        JournalDetail.objects.create(
            journal_entry=entry,
            account=payable_account,
            debit_amount=payment.amount,
            credit_amount=0,
            notes=f"Payment {payment.payment_number}"
        )
        
        JournalDetail.objects.create(
            journal_entry=entry,
            account=cash_account,
            debit_amount=0,
            credit_amount=payment.amount,
            notes=f"Payment {payment.payment_number}"
        )
    
    return entry