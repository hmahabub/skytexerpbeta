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
    Fabric, FabricRoll, Trim, GoodsReceipt, GoodsReceiptDetail,
    ProductionIssue, ProductionIssueDetail, FinishedGoods,
    FinishedGoodsProduction, Dispatch, DispatchDetail,
    StockMovement, StockAdjustment
)
from .forms import (
    FabricForm, FabricRollForm, TrimForm, GoodsReceiptForm,
    GoodsReceiptDetailForm, ProductionIssueForm, ProductionIssueDetailForm,
    FinishedGoodsForm, DispatchForm, DispatchDetailForm, StockAdjustmentForm
)

def is_inventory_or_admin(user):
    return user.is_superuser or user.groups.filter(name='Inventory').exists()

@login_required
def inventory_dashboard(request):
    """Inventory Dashboard Overview"""
    context = {
        'active': 'inventory',
        'page_title': 'Inventory Dashboard',
    }
    
    # Summary Statistics
    context['total_fabrics'] = Fabric.objects.filter(is_active=True).count()
    context['total_trims'] = Trim.objects.filter(is_active=True).count()
    context['total_finished_goods'] = FinishedGoods.objects.filter(is_active=True).count()
    
    # Stock Status
    fabric_stock = Fabric.objects.aggregate(total=Sum('current_stock'))['total'] or 0
    trim_stock = Trim.objects.aggregate(total=Sum('current_stock'))['total'] or 0
    finished_stock = FinishedGoods.objects.aggregate(total=Sum('quantity_in_stock'))['total'] or 0
    
    context['total_fabric_stock'] = fabric_stock
    context['total_trim_stock'] = trim_stock
    context['total_finished_stock'] = finished_stock
    
    # Low Stock Items
    context['low_fabric_count'] = Fabric.objects.filter(
        current_stock__lte=100,  # Adjust based on reorder level
        is_active=True
    ).count()
    
    context['low_trim_count'] = Trim.objects.filter(
        current_stock__lte=500,  # Adjust based on reorder level
        is_active=True
    ).count()
    
    # Recent Receipts
    context['recent_receipts'] = GoodsReceipt.objects.select_related('supplier').order_by('-receipt_date')[:5]
    
    # Recent Dispatches
    context['recent_dispatches'] = Dispatch.objects.select_related('buyer', 'style').order_by('-dispatch_date')[:5]
    
    # Stock Movement Chart Data
    last_7_days = [date.today() - timedelta(days=x) for x in range(6, -1, -1)]
    movement_data = []
    
    for day in last_7_days:
        count = StockMovement.objects.filter(movement_date=day).count()
        movement_data.append(count)
    
    context['movement_labels'] = [day.strftime('%b %d') for day in last_7_days]
    context['movement_data'] = movement_data
    
    # Top Items by Stock Value
    top_fabrics = Fabric.objects.filter(is_active=True).order_by('-current_stock')[:5]
    top_trims = Trim.objects.filter(is_active=True).order_by('-current_stock')[:5]
    
    context['top_fabrics'] = top_fabrics
    context['top_trims'] = top_trims
    
    return render(request, 'inventory/dashboard.html', context)

@login_required
def fabric_list(request):
    """List all fabrics"""
    fabrics = Fabric.objects.filter(is_active=True).select_related('supplier')
    
    # Search
    search = request.GET.get('search')
    if search:
        fabrics = fabrics.filter(
            Q(fabric_code__icontains=search) |
            Q(fabric_name__icontains=search) |
            Q(color__icontains=search)
        )
    
    # Filter by fabric type
    fabric_type = request.GET.get('type')
    if fabric_type:
        fabrics = fabrics.filter(fabric_type=fabric_type)
    
    # Filter by stock status
    stock_status = request.GET.get('stock_status')
    if stock_status == 'low':
        fabrics = fabrics.filter(current_stock__lte=100)
    elif stock_status == 'normal':
        fabrics = fabrics.filter(current_stock__gt=100, current_stock__lt=1000)
    elif stock_status == 'overstock':
        fabrics = fabrics.filter(current_stock__gte=1000)
    
    # Pagination
    paginator = Paginator(fabrics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active': 'inventory',
        'page_title': 'Fabric Management',
        'fabrics': page_obj,
        'fabric_types': Fabric.FABRIC_TYPES,
        'search': search,
        'current_type': fabric_type,
        'current_stock_status': stock_status,
    }
    return render(request, 'inventory/fabric_list.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_fabric(request):
    """Add new fabric"""
    if request.method == 'POST':
        form = FabricForm(request.POST)
        if form.is_valid():
            fabric = form.save()
            messages.success(request, f'Fabric "{fabric.fabric_name}" added successfully!')
            return redirect('inventory:fabric_list')
    else:
        form = FabricForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Fabric',
        'form': form,
    }
    return render(request, 'inventory/fabric_form.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def edit_fabric(request, pk):
    """Edit fabric"""
    fabric = get_object_or_404(Fabric, pk=pk)
    if request.method == 'POST':
        form = FabricForm(request.POST, instance=fabric)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fabric "{fabric.fabric_name}" updated successfully!')
            return redirect('inventory:fabric_list')
    else:
        form = FabricForm(instance=fabric)
    
    context = {
        'active': 'inventory',
        'page_title': 'Edit Fabric',
        'form': form,
        'fabric': fabric,
    }
    return render(request, 'inventory/fabric_form.html', context)

@login_required
def trim_list(request):
    """List all trims"""
    trims = Trim.objects.filter(is_active=True).select_related('supplier')
    
    # Search
    search = request.GET.get('search')
    if search:
        trims = trims.filter(
            Q(trim_code__icontains=search) |
            Q(trim_name__icontains=search)
        )
    
    # Filter by trim type
    trim_type = request.GET.get('type')
    if trim_type:
        trims = trims.filter(trim_type=trim_type)
    
    context = {
        'active': 'inventory',
        'page_title': 'Trim Management',
        'trims': trims,
        'trim_types': Trim.TRIM_TYPES,
        'search': search,
        'current_type': trim_type,
    }
    return render(request, 'inventory/trim_list.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_trim(request):
    """Add new trim"""
    if request.method == 'POST':
        form = TrimForm(request.POST)
        if form.is_valid():
            trim = form.save()
            messages.success(request, f'Trim "{trim.trim_name}" added successfully!')
            return redirect('inventory:trim_list')
    else:
        form = TrimForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Trim',
        'form': form,
    }
    return render(request, 'inventory/trim_form.html', context)

@login_required
def goods_receipts(request):
    """List all goods receipts"""
    receipts = GoodsReceipt.objects.select_related('supplier', 'purchase_order').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        receipts = receipts.filter(quality_status=status)
    
    context = {
        'active': 'inventory',
        'page_title': 'Goods Receipts',
        'receipts': receipts,
        'statuses': GoodsReceipt.QUALITY_STATUS,
        'current_status': status,
    }
    return render(request, 'inventory/goods_receipts.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_goods_receipt(request):
    """Add new goods receipt"""
    if request.method == 'POST':
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.received_by = request.user
            receipt.save()
            
            # Handle receipt details
            fabric_ids = request.POST.getlist('fabric_ids[]')
            trim_ids = request.POST.getlist('trim_ids[]')
            quantities_received = request.POST.getlist('quantities_received[]')
            quantities_accepted = request.POST.getlist('quantities_accepted[]')
            quantities_rejected = request.POST.getlist('quantities_rejected[]')
            unit_prices = request.POST.getlist('unit_prices[]')
            
            total_accepted = 0
            total_rejected = 0
            
            for i in range(len(quantities_received)):
                if quantities_received[i]:
                    fabric_id = fabric_ids[i] if i < len(fabric_ids) else None
                    trim_id = trim_ids[i] if i < len(trim_ids) else None
                    
                    detail = GoodsReceiptDetail.objects.create(
                        goods_receipt=receipt,
                        fabric_id=fabric_id if fabric_id else None,
                        trim_id=trim_id if trim_id else None,
                        quantity_received=Decimal(quantities_received[i]),
                        quantity_accepted=Decimal(quantities_accepted[i] or quantities_received[i]),
                        quantity_rejected=Decimal(quantities_rejected[i] or 0),
                        unit_price=Decimal(unit_prices[i] or 0)
                    )
                    
                    total_accepted += detail.quantity_accepted
                    total_rejected += detail.quantity_rejected
                    
                    # Update stock
                    if detail.fabric:
                        fabric = detail.fabric
                        fabric.current_stock += detail.quantity_accepted
                        fabric.save()
                    elif detail.trim:
                        trim = detail.trim
                        trim.current_stock += int(detail.quantity_accepted)
                        trim.save()
            
            receipt.total_quantity = total_accepted + total_rejected
            receipt.accepted_quantity = total_accepted
            receipt.rejected_quantity = total_rejected
            
            if total_rejected == 0:
                receipt.quality_status = 'accepted'
            elif total_accepted > 0:
                receipt.quality_status = 'partial'
            else:
                receipt.quality_status = 'rejected'
            
            receipt.save()
            
            messages.success(request, f'Goods receipt "{receipt.receipt_number}" created successfully!')
            return redirect('inventory:goods_receipts')
    else:
        form = GoodsReceiptForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Goods Receipt',
        'form': form,
        'fabrics': Fabric.objects.filter(is_active=True),
        'trims': Trim.objects.filter(is_active=True),
    }
    return render(request, 'inventory/goods_receipt_form.html', context)

@login_required
def production_issues(request):
    """List all production issues"""
    issues = ProductionIssue.objects.select_related('style', 'department', 'issued_by').all()
    
    context = {
        'active': 'inventory',
        'page_title': 'Production Issues',
        'issues': issues,
    }
    return render(request, 'inventory/production_issues.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_production_issue(request):
    """Add new production issue"""
    if request.method == 'POST':
        form = ProductionIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.issued_by = request.user
            issue.save()
            
            # Handle issue details
            fabric_ids = request.POST.getlist('fabric_ids[]')
            fabric_roll_ids = request.POST.getlist('fabric_roll_ids[]')
            trim_ids = request.POST.getlist('trim_ids[]')
            quantities_issued = request.POST.getlist('quantities_issued[]')
            
            for i in range(len(quantities_issued)):
                if quantities_issued[i]:
                    detail = ProductionIssueDetail.objects.create(
                        production_issue=issue,
                        fabric_id=fabric_ids[i] if i < len(fabric_ids) and fabric_ids[i] else None,
                        fabric_roll_id=fabric_roll_ids[i] if i < len(fabric_roll_ids) and fabric_roll_ids[i] else None,
                        trim_id=trim_ids[i] if i < len(trim_ids) and trim_ids[i] else None,
                        quantity_issued=Decimal(quantities_issued[i]),
                        quantity_requested=Decimal(quantities_issued[i])
                    )
                    
                    # Update stock
                    if detail.fabric:
                        fabric = detail.fabric
                        fabric.current_stock -= detail.quantity_issued
                        fabric.save()
                    elif detail.trim:
                        trim = detail.trim
                        trim.current_stock -= int(detail.quantity_issued)
                        trim.save()
                    
                    # Update fabric roll if used
                    if detail.fabric_roll:
                        roll = detail.fabric_roll
                        roll.used_length += detail.quantity_issued
                        roll.save()
            
            issue.status = 'issued'
            issue.save()
            
            messages.success(request, f'Production issue "{issue.issue_number}" created successfully!')
            return redirect('inventory:production_issues')
    else:
        form = ProductionIssueForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Production Issue',
        'form': form,
        'fabrics': Fabric.objects.filter(is_active=True),
        'fabric_rolls': FabricRoll.objects.filter(status='in_stock'),
        'trims': Trim.objects.filter(is_active=True),
    }
    return render(request, 'inventory/production_issue_form.html', context)

@login_required
def finished_goods_list(request):
    """List all finished goods"""
    finished_goods = FinishedGoods.objects.select_related('style').filter(is_active=True)
    
    # Search
    search = request.GET.get('search')
    if search:
        finished_goods = finished_goods.filter(
            Q(sku_code__icontains=search) |
            Q(style__style_number__icontains=search)
        )
    
    context = {
        'active': 'inventory',
        'page_title': 'Finished Goods',
        'finished_goods': finished_goods,
        'search': search,
    }
    return render(request, 'inventory/finished_goods.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_finished_goods(request):
    """Add new finished goods"""
    if request.method == 'POST':
        form = FinishedGoodsForm(request.POST)
        if form.is_valid():
            finished = form.save()
            messages.success(request, f'Finished goods "{finished.sku_code}" added successfully!')
            return redirect('inventory:finished_goods_list')
    else:
        form = FinishedGoodsForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Finished Goods',
        'form': form,
    }
    return render(request, 'inventory/finished_goods_form.html', context)

@login_required
def dispatches(request):
    """List all dispatches"""
    dispatches = Dispatch.objects.select_related('buyer', 'style', 'created_by').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        dispatches = dispatches.filter(status=status)
    
    context = {
        'active': 'inventory',
        'page_title': 'Dispatches',
        'dispatches': dispatches,
        'statuses': Dispatch._meta.get_field('status').choices,
        'current_status': status,
    }
    return render(request, 'inventory/dispatches.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_dispatch(request):
    """Add new dispatch"""
    if request.method == 'POST':
        form = DispatchForm(request.POST)
        if form.is_valid():
            dispatch = form.save(commit=False)
            dispatch.created_by = request.user
            dispatch.save()
            
            # Handle dispatch details
            finished_goods_ids = request.POST.getlist('finished_goods_ids[]')
            quantities = request.POST.getlist('quantities[]')
            carton_numbers = request.POST.getlist('carton_numbers[]')
            
            total_quantity = 0
            
            for i in range(len(quantities)):
                if quantities[i]:
                    detail = DispatchDetail.objects.create(
                        dispatch=dispatch,
                        finished_goods_id=finished_goods_ids[i] if i < len(finished_goods_ids) else None,
                        quantity=int(quantities[i]),
                        carton_number=carton_numbers[i] if i < len(carton_numbers) else f"CTN-{i+1:04d}"
                    )
                    
                    total_quantity += detail.quantity
                    
                    # Update finished goods stock
                    if detail.finished_goods:
                        fg = detail.finished_goods
                        fg.quantity_in_stock -= detail.quantity
                        fg.quantity_dispatched += detail.quantity
                        fg.save()
            
            dispatch.total_quantity = total_quantity
            dispatch.save()
            
            messages.success(request, f'Dispatch "{dispatch.dispatch_number}" created successfully!')
            return redirect('inventory:dispatches')
    else:
        form = DispatchForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Dispatch',
        'form': form,
        'finished_goods': FinishedGoods.objects.filter(is_active=True, quantity_in_stock__gt=0),
    }
    return render(request, 'inventory/dispatch_form.html', context)

@login_required
def stock_adjustments(request):
    """List all stock adjustments"""
    adjustments = StockAdjustment.objects.select_related('created_by', 'approved_by').all()
    
    context = {
        'active': 'inventory',
        'page_title': 'Stock Adjustments',
        'adjustments': adjustments,
    }
    return render(request, 'inventory/stock_adjustments.html', context)

@login_required
@user_passes_test(is_inventory_or_admin)
def add_stock_adjustment(request):
    """Add new stock adjustment"""
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.created_by = request.user
            adjustment.save()
            
            # Update stock
            if adjustment.fabric:
                if adjustment.adjustment_type in ['damage', 'expired', 'qc_failure']:
                    adjustment.fabric.current_stock -= adjustment.quantity
                else:
                    adjustment.fabric.current_stock += adjustment.quantity
                adjustment.fabric.save()
            elif adjustment.trim:
                if adjustment.adjustment_type in ['damage', 'expired', 'qc_failure']:
                    adjustment.trim.current_stock -= int(adjustment.quantity)
                else:
                    adjustment.trim.current_stock += int(adjustment.quantity)
                adjustment.trim.save()
            elif adjustment.finished_goods:
                if adjustment.adjustment_type in ['damage', 'expired', 'qc_failure']:
                    adjustment.finished_goods.quantity_in_stock -= int(adjustment.quantity)
                else:
                    adjustment.finished_goods.quantity_in_stock += int(adjustment.quantity)
                adjustment.finished_goods.save()
            
            messages.success(request, f'Stock adjustment "{adjustment.adjustment_number}" created successfully!')
            return redirect('inventory:stock_adjustments')
    else:
        form = StockAdjustmentForm()
    
    context = {
        'active': 'inventory',
        'page_title': 'Add Stock Adjustment',
        'form': form,
        'fabrics': Fabric.objects.filter(is_active=True),
        'trims': Trim.objects.filter(is_active=True),
        'finished_goods': FinishedGoods.objects.filter(is_active=True),
    }
    return render(request, 'inventory/stock_adjustment_form.html', context)

@login_required
def stock_report(request):
    """Generate stock report"""
    context = {
        'active': 'inventory',
        'page_title': 'Stock Report',
    }
    
    # Fabric Stock Report
    fabrics = Fabric.objects.filter(is_active=True)
    fabric_data = []
    for fabric in fabrics:
        fabric_data.append({
            'code': fabric.fabric_code,
            'name': fabric.fabric_name,
            'color': fabric.color,
            'stock': fabric.current_stock,
            'reorder_level': fabric.reorder_level,
            'status': fabric.stock_status,
        })
    context['fabric_data'] = fabric_data
    
    # Trim Stock Report
    trims = Trim.objects.filter(is_active=True)
    trim_data = []
    for trim in trims:
        trim_data.append({
            'code': trim.trim_code,
            'name': trim.trim_name,
            'stock': trim.current_stock,
            'reorder_level': trim.reorder_level,
            'status': trim.stock_status,
        })
    context['trim_data'] = trim_data
    
    # Finished Goods Report
    finished = FinishedGoods.objects.filter(is_active=True)
    finished_data = []
    for fg in finished:
        finished_data.append({
            'sku': fg.sku_code,
            'style': fg.style.style_number,
            'size': fg.size,
            'color': fg.color,
            'in_stock': fg.quantity_in_stock,
            'dispatched': fg.quantity_dispatched,
            'reorder_level': fg.reorder_level,
            'status': 'Low' if fg.is_low_stock else 'Normal',
        })
    context['finished_data'] = finished_data
    
    return render(request, 'inventory/stock_report.html', context)