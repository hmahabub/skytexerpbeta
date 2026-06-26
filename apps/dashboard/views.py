from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from apps.hr.models import Employee, Attendance, Payroll, ProductionOutput
from apps.accounts.models import Style, SalesInvoice, SupplierBill
from apps.inventory.models import Fabric, FabricRoll, Trim

@login_required
def dashboard(request):
    context = {
        'active': 'dashboard',
        'page_title': 'Dashboard Overview',
    }
    
    # HR Statistics
    context['total_employees'] = Employee.objects.filter(is_active=True).count()
    context['total_production_staff'] = Employee.objects.filter(
        is_active=True, 
        skill_category__in=['cutting', 'stitching', 'finishing', 'washing', 'qc']
    ).count()
    
    today = datetime.now().date()
    context['today_attendance'] = Attendance.objects.filter(date=today).count()
    
    # Production Statistics
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_production = ProductionOutput.objects.filter(
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('quantity_produced'))['total'] or 0
    context['monthly_production'] = monthly_production
    
    # Accounts Statistics
    context['active_styles'] = Style.objects.filter(
        status__in=['order', 'production']
    ).count()
    
    context['total_sales'] = SalesInvoice.objects.filter(
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context['pending_payments'] = SupplierBill.objects.filter(
        status='unpaid'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Inventory Statistics
    context['fabric_stock'] = FabricRoll.objects.filter(
        status='in_stock'
    ).aggregate(total=Sum('remaining_length'))['total'] or 0
    
    context['low_stock_items'] = Trim.objects.filter(
        current_stock__lte=models.F('reorder_level')
    ).count()
    
    # Recent Data
    context['recent_employees'] = Employee.objects.order_by('-created_at')[:5]
    context['recent_styles'] = Style.objects.order_by('-created_at')[:5]
    
    # Chart Data
    last_7_days = [datetime.now().date() - timedelta(days=x) for x in range(6, -1, -1)]
    production_data = []
    
    for day in last_7_days:
        daily_production = ProductionOutput.objects.filter(
            date=day
        ).aggregate(total=Sum('quantity_produced'))['total'] or 0
        production_data.append(daily_production)
    
    context['production_labels'] = [day.strftime('%b %d') for day in last_7_days]
    context['production_data'] = production_data
    
    return render(request, 'dashboard/index.html', context)