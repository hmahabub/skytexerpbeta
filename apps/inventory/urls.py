from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='inventory_dashboard'),
    
    # Fabric Management
    path('fabrics/', views.fabric_list, name='fabric_list'),
    path('fabrics/add/', views.add_fabric, name='add_fabric'),
    path('fabrics/<int:pk>/edit/', views.edit_fabric, name='edit_fabric'),
    
    # Trim Management
    path('trims/', views.trim_list, name='trim_list'),
    path('trims/add/', views.add_trim, name='add_trim'),
    
    # Goods Receipt
    path('receipts/', views.goods_receipts, name='goods_receipts'),
    path('receipts/add/', views.add_goods_receipt, name='add_goods_receipt'),
    
    # Production Issues
    path('issues/', views.production_issues, name='production_issues'),
    path('issues/add/', views.add_production_issue, name='add_production_issue'),
    
    # Finished Goods
    path('finished-goods/', views.finished_goods_list, name='finished_goods_list'),
    path('finished-goods/add/', views.add_finished_goods, name='add_finished_goods'),
    
    # Dispatches
    path('dispatches/', views.dispatches, name='dispatches'),
    path('dispatches/add/', views.add_dispatch, name='add_dispatch'),
    
    # Stock Adjustments
    path('adjustments/', views.stock_adjustments, name='stock_adjustments'),
    path('adjustments/add/', views.add_stock_adjustment, name='add_stock_adjustment'),
    
    # Reports
    path('reports/', views.stock_report, name='stock_report'),
]