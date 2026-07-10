from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Dashboard
    path('', views.accounts_dashboard, name='accounts_dashboard'),
    
    # Chart of Accounts
    path('chart-of-accounts/', views.chart_of_accounts, name='chart_of_accounts'),
    path('chart-of-accounts/add/', views.add_account, name='add_account'),
    
    # Buyers
    path('buyers/', views.buyers_list, name='buyers_list'),
    path('buyers/add/', views.add_buyer, name='add_buyer'),
    
    # Suppliers
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    
    # Styles
    path('styles/', views.styles_list, name='styles_list'),
    path('styles/add/', views.add_style, name='add_style'),
    
    # Sales Invoices
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    
    # Payments
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/add/', views.add_payment, name='add_payment'),
    
    # Journal Entries
    path('journal-entries/', views.journal_entries, name='journal_entries'),
    path('journal-entries/add/', views.add_journal_entry, name='add_journal_entry'),
    
    # Cost Sheets
    path('cost-sheets/', views.cost_sheets, name='cost_sheets'),
    path('cost-sheets/add/', views.add_cost_sheet, name='add_cost_sheet'),
    
    # Bank Accounts
    path('banks/', views.banks_list, name='banks_list'),
    path('banks/add/', views.add_bank, name='add_bank'),
    
    # Reports
    path('reports/', views.financial_reports, name='financial_reports'),
]