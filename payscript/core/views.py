from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.template.loader import get_template
from weasyprint import HTML, CSS
from .models import Sheet, Product, InvoiceMeta, Customer
from decimal import Decimal, InvalidOperation
import datetime
import re
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from .forms import SimpleAuthenticationForm
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied

# Views for the Payscript application

#login view with captcha
@csrf_protect
def custom_login(request):
    try:
        if request.method == 'GET':
            logout(request)  # 🔒 Force logout on every entry to login page
        
        if request.method == 'POST':
            try:
                form = SimpleAuthenticationForm(request, data=request.POST)
                if form.is_valid():
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password')
                    destination = form.cleaned_data.get('destination')
                    user = authenticate(username=username, password=password)
                    
                    if user is not None and user.is_superuser:
                        login(request, user)
                        if destination == 'admin':
                            return redirect('/admin/')
                        return redirect('dashboard')
                    else:
                        form.add_error(None, "Invalid username or password")
            except PermissionDenied:
                # Handle CSRF verification failed cases
                form = SimpleAuthenticationForm(request)
                form.add_error(None, "Security verification failed. Please try logging in again.")
            except Exception as e:
                # Handle any other unexpected errors
                form = SimpleAuthenticationForm(request)
                form.add_error(None, "An error occurred during login. Please try again.")
        else:
            form = SimpleAuthenticationForm(request)
        
        return render(request, 'core/login.html', {'form': form})
    
    except Exception as e:
        # Fallback for any unhandled exceptions
        form = SimpleAuthenticationForm(request)
        form.add_error(None, "A system error occurred. Please contact support if this persists.")
        return render(request, 'core/login.html', {'form': form})

#-------------------------------------------------------------

# Dashboard view to list all sheets
@login_required
def dashboard(request):
    sheets = Sheet.objects.all().order_by('-created_at')
    return render(request, 'core/dashboard.html', {'sheets': sheets})

#-------------------------------------------------------------

# View to delete a sheet
@login_required
def delete_sheet(request, sheet_id):
    try:
        sheet = get_object_or_404(Sheet, id=sheet_id)
        sheet.delete()
        messages.success(request, "Sheet deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting sheet: {str(e)}")
    return redirect('dashboard')

#-------------------------------------------------------------

# View to create a new sheet
@login_required
def create_sheet(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)
        
        if Sheet.objects.filter(title__iexact=title).exists():
            return JsonResponse({'success': False, 'error': 'A sheet with this title already exists'}, status=400)
        
        try:
            sheet = Sheet.objects.create(title=title)
            return JsonResponse({'success': True, 'sheet_id': sheet.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False}, status=405)

#-------------------------------------------------------------

# View to display a specific sheet and its products
@login_required
def view_sheet(request, sheet_id):
    try:
        sheet = get_object_or_404(Sheet, id=sheet_id)
        products = sheet.products.all()
        invoice_meta, _ = InvoiceMeta.objects.get_or_create(sheet=sheet)
        
        context = {
            'sheet': sheet,
            'products': products,
            'invoice': invoice_meta,
        }
        return render(request, 'core/view_sheet.html', context)
    except Exception as e:
        messages.error(request, f"Error loading sheet: {str(e)}")
        return redirect('dashboard')

#-------------------------------------------------------------

# View to add a new product to a sheet
@login_required
@csrf_exempt
def add_product(request, sheet_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        sheet = get_object_or_404(Sheet, id=sheet_id)
        data = request.POST

        required_fields = ['serial_no', 'item', 'quantity', 'rate']
        for field in required_fields:
            if not data.get(field, '').strip():
                return JsonResponse({'success': False, 'error': f'{field.capitalize()} is required'}, status=400)
        
        try:
            quantity = int(data['quantity'])
            rate = Decimal(data['rate'])
            if quantity <= 0 or rate <= 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            return JsonResponse({'success': False, 'error': 'Quantity and Rate must be valid positive numbers'}, status=400)

        checked = 'checked' in data  # Handle checkbox

        product = Product.objects.create(
            sheet=sheet,
            serial_no=data['serial_no'].strip(),
            item=data['item'].strip(),
            quantity=quantity,
            rate=rate,
            warranty=data.get('warranty', '').strip(),
            checked=checked
        )
        return JsonResponse({'success': True, 'product_id': product.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

#-------------------------------------------------------------

# View to delete a product from a sheet
@login_required
def delete_product(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        sheet_id = product.sheet.id
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting product: {str(e)}")
    return redirect('view_sheet', sheet_id=sheet_id)

#-------------------------------------------------------------

# View to edit an existing product in a sheet
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    try:
        data = request.POST
        serial_no = data.get('serial_no', '').strip()
        item = data.get('item', '').strip()
        warranty = data.get('warranty', '').strip()

        if not serial_no or not item:
            messages.error(request, "Serial number and item name cannot be empty.")
            return redirect('view_sheet', sheet_id=product.sheet.id)

        try:
            quantity = int(data.get('quantity', product.quantity))
            rate = Decimal(data.get('rate', product.rate))
            if quantity <= 0 or rate <= 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            messages.error(request, "Quantity and rate must be valid and positive.")
            return redirect('view_sheet', sheet_id=product.sheet.id)

        product.serial_no = serial_no
        product.item = item
        product.quantity = quantity
        product.rate = rate
        product.warranty = warranty
        product.checked = 'checked' in data
        product.save()
        messages.success(request, "Product updated successfully.")
    except Exception as e:
        messages.error(request, f"Error updating product: {str(e)}")

    return redirect('view_sheet', sheet_id=product.sheet.id)

#-------------------------------------------------------------

# View to update invoice meta information
@login_required
def update_invoice_meta(request, sheet_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    try:
        sheet = get_object_or_404(Sheet, id=sheet_id)
        invoice = InvoiceMeta.objects.get_or_create(sheet=sheet)[0]

        try:
            adjustments = request.POST.get('adjustments', '').strip()
            received = request.POST.get('received', '').strip()

            if not adjustments or not received:
                raise ValueError("Both adjustments and received fields are required.")

            invoice.adjustments = Decimal(adjustments)
            invoice.received = Decimal(received)
            invoice.save()
            messages.success(request, "Summary updated successfully.")
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f"Invalid input: {e}")

        return redirect('view_sheet', sheet_id=sheet_id)
    except Exception as e:
        messages.error(request, f"Error updating summary: {str(e)}")
        return redirect('dashboard')

#-------------------------------------------------------------

# View to generate an invoice PDF for a sheet
@login_required
def generate_invoice(request, sheet_id):
    sheet = get_object_or_404(Sheet, id=sheet_id)
    invoice = sheet.invoice_meta

    # Enforce customer info presence
    if not invoice.customer:
        messages.error(request, "Cannot generate invoice: Customer information is missing.")
        return redirect('view_sheet', sheet_id=sheet_id)

    # Enforce at least one product
    products = sheet.products.all()
    if not products.exists():
        messages.error(request, "Cannot generate invoice: At least one product is required.")
        return redirect('view_sheet', sheet_id=sheet_id)

    now = datetime.datetime.now()
    current_date = now.strftime("%d-%b-%Y")
    current_time = now.strftime("%I:%M %p")

    company_info = {
        'name': "Konnect Komputers",
        'email': "konnectkomputers@gmail.com",
        'address': "B422 Block-1 Metroville SITE Karachi 75840, Pakistan",
        'phone': "0333-3025266 | 0330-6669499",
        'social': {
            'facebook': "Konnect Komputers", 
        }
    }

    context = {
        'sheet': sheet,
        'invoice': invoice,
        'products': products,
        'company': company_info,
        'date': current_date,
        'time': current_time,
    }

    template = get_template('core/invoice_template.html')
    html_string = template.render(context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    pdf = html.write_pdf(stylesheets=[
        CSS(string='@page { size: A4; margin: 0mm; }')
    ])

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    return response

#-------------------------------------------------------------

# View to update customer information for a sheet
@login_required
def update_customer_info(request, sheet_id):
    if request.method == 'POST':
        sheet = get_object_or_404(Sheet, id=sheet_id)
        invoice = sheet.invoice_meta

        try:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            address = request.POST.get('address', '').strip()
            phone = request.POST.get('phone', '').strip()

            # Validate presence
            if not name or not email or not address or not phone:
                messages.error(request, "All customer fields are required.")
                return redirect('view_sheet', sheet_id=sheet_id)

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email format.")
                return redirect('view_sheet', sheet_id=sheet_id)

            # Validate phone length (digits only, no + or -)
            cleaned_phone = re.sub(r'\D', '', phone)
            if len(cleaned_phone) < 10 or len(cleaned_phone) > 12:
                messages.error(request, "Phone number must be 10 to 12 digits.")
                return redirect('view_sheet', sheet_id=sheet_id)

            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'address': address,
                    'phone': phone,
                }
            )

            if not created:
                customer.name = name
                customer.address = address
                customer.phone = phone
                customer.save()

            invoice.customer = customer
            invoice.save()

            messages.success(request, "Customer information updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating customer info: {str(e)}")

        return redirect('view_sheet', sheet_id=sheet_id)

    return JsonResponse({'success': False}, status=400)

#-------------------------------------------------------------

# View to display the about page
@login_required
def about(request):
    return render(request, 'core/about.html')

#-------------------------------------------------------------