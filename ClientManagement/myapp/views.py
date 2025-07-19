from django.shortcuts import render, redirect, get_object_or_404
from myapp.models import Client, Shipments, Provider, Bill
from django.utils import timezone
from django.contrib import messages
import pandas as pd
from datetime import date
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from num2words import num2words
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date



# Create your views here.

def index(request):
    COLOR_CLASSES = ['bg-primary', 'bg-success', 'bg-info', 'bg-warning', 'bg-secondary', 'bg-dark']
    FIXED_COLORS = {
        'shree maruti courier': 'bg-danger',
        'delivery': 'bg-dark',
        'fedex': 'bg-warning'
    }

    # Get from/to dates from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    from_dt = parse_date(from_date) if from_date else None
    to_dt = parse_date(to_date) if to_date else None

    # Apply date range filtering
    shipments = Shipments.objects.all()
    if from_dt and to_dt:
        shipments = shipments.filter(date__range=(from_dt, to_dt))
    elif from_dt:
        shipments = shipments.filter(date__gte=from_dt)
    elif to_dt:
        shipments = shipments.filter(date__lte=to_dt)

    bills = Bill.objects.filter(shipments__in=shipments)

    total_clients = Client.objects.count()
    total_shipments = shipments.count()
    today_shipments = Shipments.objects.filter(date=date.today()).count()
    total_revenue = bills.aggregate(total=Sum('total_amount'))['total'] or 0

    provider_shipments = []
    revenue_by_provider = []
    dynamic_color_index = 0

    for provider in Provider.objects.all():
        name_lc = provider.name.strip().lower()

        shipment_count = shipments.filter(service_provider=provider).count()
        revenue = shipments.filter(service_provider=provider, bill__isnull=True).aggregate(
            total=Sum('cost'))['total'] or 0

        if name_lc in FIXED_COLORS:
            color_class = FIXED_COLORS[name_lc]
        else:
            color_class = COLOR_CLASSES[dynamic_color_index % len(COLOR_CLASSES)]
            dynamic_color_index += 1

        provider_shipments.append({
            'name': provider.name,
            'count': shipment_count,
            'color': color_class
        })

        revenue_by_provider.append({
            'name': provider.name,
            'revenue': revenue,
            'color': color_class
        })

    monthly_trends = (
        Shipments.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    recent_shipments = shipments.select_related('client_name', 'service_provider').order_by('-id')[:5]

    return render(request, 'index.html', {
        'total_clients': total_clients,
        'total_shipments': total_shipments,
        'today_shipments': today_shipments,
        'total_revenue': total_revenue,
        'provider_shipments': provider_shipments,
        'revenue_by_provider': revenue_by_provider,
        'monthly_trends': monthly_trends,
        'recent_shipments': recent_shipments,
        'from_date': from_date,
        'to_date': to_date
    })

def ShowClients(request):
    clients = Client.objects.all()
    today = date.today()
    
    return render(request, 'clients.html', {
        'clients': clients,
        'current_year': today.year,
        'current_month': today.month,
    })

def client_shipments(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    shipment = Shipments.objects.filter(client_name=client)
    return render(request, 'shipments.html', {'client': client, 'shipments': shipment})

def AddClient(request):
    if request.method == "POST":
        name = request.POST['client_name']
        gst_no = request.POST['gst_number']
        email = request.POST['email']
        phone = request.POST['client_phone']
        address = request.POST['address']
        if Client.objects.filter(gst_number=gst_no).exists():
            context = {}
            context['error'] = "gst number must be unique"
            return render(request,'addclient.html',context) 
        
        
        clients = Client.objects.create(name = name, gst_number = gst_no, email = email,phone = phone, address = address)
        
        clients.save()
        
        return redirect('/showclients')
    else:
        return render(request,'addclient.html')
    
def update_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        client.name = request.POST.get('name')
        client.gst_number = request.POST.get('gst_number')
        client.email = request.POST.get('email')
        client.phone = request.POST.get('phone')
        client.address = request.POST.get('address')
        client.fuel_surcharge_percent = request.POST.get('fuel_surcharge_percent') or 0
        client.save()
        return redirect('/showclients')  # replace with your client list route name or '/clients'

    return redirect('/showclients')  # fallback

def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return redirect('/showclients')
    
def ShowShipments(request):
    shipments = Shipments.objects.all()
    clients = Client.objects.all()
    providers = Provider.objects.all()

    # Filters
    if request.GET.get("filter_date"):
        shipments = shipments.filter(date=request.GET.get("filter_date"))

    if request.GET.get("filter_doc"):
        shipments = shipments.filter(document_no__icontains=request.GET.get("filter_doc"))

    if request.GET.get("filter_client"):
        shipments = shipments.filter(client_name__id=request.GET.get("filter_client"))

    if request.GET.get("filter_receiver"):
        shipments = shipments.filter(receiver_name__icontains=request.GET.get("filter_receiver"))

    if request.GET.get("filter_destination"):
        shipments = shipments.filter(destination__icontains=request.GET.get("filter_destination"))

    if request.GET.get("filter_service_type"):
        shipments = shipments.filter(service_type__icontains=request.GET.get("filter_service_type"))

    if request.GET.get("filter_item_type"):
        shipments = shipments.filter(item_type__icontains=request.GET.get("filter_item_type"))

    if request.GET.get("filter_travel_by"):
        shipments = shipments.filter(travel_by__icontains=request.GET.get("filter_travel_by"))

    if request.GET.get("filter_provider"):
        shipments = shipments.filter(service_provider__id=request.GET.get("filter_provider"))

    context = {
        "shipments": shipments,
        "clients": clients,
        "providers": providers,
    }
    return render(request, "shipments.html", context)

def AddShipments(request):
    clients = Client.objects.all()
    providers = Provider.objects.all()

    # Store input data from either POST or GET for form prefill
    input_data = request.POST if request.method == 'POST' else request.GET

    context = {
        'clients': clients,
        'providers': providers,
        'input': input_data,
        'shipments_recent': Shipments.objects.all().order_by('-id')[:5],
    }

    if request.method == 'POST':
        date = request.POST.get('date')
        document_no = request.POST.get('document_no', '').strip()
        client_name = request.POST.get('client')
        provider_id = request.POST.get('service_provider')
        destination = request.POST.get('destination')
        service_type = request.POST.get('service_type')
        item_type = request.POST.get('item_type')
        travel_by = request.POST.get('travel_by')
        receiver_name = request.POST.get('receiver_name')
        weight = request.POST.get('weight')
        pcs = request.POST.get('pcs')
        cost = request.POST.get('cost')

        # Validate number fields
        try:
            weight = float(weight)
            cost = float(cost)
        except ValueError:
            context['error'] = "Please enter valid numeric values for Weight and Cost."
            return render(request, 'addshipment.html', context)

        if not document_no:
            context['error'] = "Document number is required."
            return render(request, 'addshipment.html', context)

        if Shipments.objects.filter(document_no=document_no).exists():
            context['error'] = "This document number already exists."
            return render(request, 'addshipment.html', context)

        if cost < 10:
            context['error'] = "Cost must be greater than ₹10."
            return render(request, 'addshipment.html', context)

        try:
            client = Client.objects.get(name=client_name)
            provider = Provider.objects.get(id=provider_id)
        except (Client.DoesNotExist, Provider.DoesNotExist):
            context['error'] = "Invalid Client or Provider selected."
            return render(request, 'addshipment.html', context)

        # Save to database
        Shipments.objects.create(
            date=date,
            document_no=document_no,
            client_name=client,
            service_provider=provider,
            destination=destination,
            service_type=service_type,
            item_type=item_type,
            travel_by=travel_by,
            receiver_name=receiver_name,
            weight=weight,
            pcs=pcs or 1,
            cost=cost
        )

        # Redirect with success and preserve date
        return redirect(f"/addshipment?success=1&date={date}")

    # If redirected after success
    if request.GET.get('success') == '1':
        messages.success(request, "Shipment added successfully!")

    return render(request, 'addshipment.html', context)

def edit_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipments, id=shipment_id)
    clients = Client.objects.all()
    providers = Provider.objects.all()

    if request.method == 'POST':
        shipment.date = request.POST.get('date')
        shipment.document_no = request.POST.get('document_no')
        shipment.destination = request.POST.get('destination')
        shipment.receiver_name = request.POST.get('receiver_name')
        shipment.service_type = request.POST.get('service_type')
        shipment.item_type = request.POST.get('item_type')
        shipment.travel_by = request.POST.get('travel_by')
        shipment.weight = request.POST.get('weight') or 0
        shipment.pcs = request.POST.get('pcs') or 1
        shipment.cost = request.POST.get('cost') or 0

        # Client and Provider
        client_name = request.POST.get('client')
        provider_id = request.POST.get('service_provider')
        try:
            shipment.client_name = Client.objects.get(name=client_name)
            shipment.service_provider = Provider.objects.get(id=provider_id)
        except:
            messages.error(request, "Invalid Client or Provider")
            return redirect('edit_shipment', shipment_id=shipment.id)

        shipment.save()
        messages.success(request, "Shipment updated successfully!")
        return redirect('/showshipments')  # Replace with your list view name

    return render(request, 'update-shipment.html', {
        'shipment': shipment,
        'clients': clients,
        'providers': providers,
    })

def upload_shipments(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        try:
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                try:
                    # Clean and match client
                    client_name = str(row['client_name']).strip()
                    client = Client.objects.filter(name__iexact=client_name).first()
                    if not client:
                        print(f" Client not found: {client_name}")
                        continue

                    # Clean and match provider
                    provider_name = str(row['service_provider']).strip()
                    provider = Provider.objects.filter(name__iexact=provider_name).first()
                    if not provider:
                        print(f" Provider not found: {provider_name}")
                        continue

                    # Convert date
                    date_val = row['date']
                    if hasattr(date_val, 'date'):
                        date_val = date_val.date()

                    # Optional: calculate cost from rates if needed
                    # zone = get_zone(row['destination'])  # define this if needed
                    # rate = RateSheet.objects.get(client=client, zone=zone).rate_per_kg
                    # cost = rate * float(row['weight'])

                    Shipments.objects.create(
                        date=date_val,
                        document_no=row['document_no'],
                        client_name=client,
                        service_provider=provider,
                        destination=row['destination'],
                        service_type=row['service_type'],
                        item_type=row['item_type'],
                        travel_by=row['travel_by'],
                        receiver_name=row['receiver_name'],
                        weight=row['weight'],
                        pcs=row['pcs'],
                        cost=row['cost']  # or use calculated cost
                    )

                except Exception as row_err:
                    print(f"⚠️ Error with row: {row.to_dict()} | Error: {row_err}")
                    continue

            messages.success(request, "✅ Shipments uploaded successfully.")
        except Exception as e:
            messages.error(request, f" Upload error: {e}")

    return redirect('/showshipments')

def delete_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipments, id=shipment_id)
    shipment.delete()
    return redirect('/showshipments')

def ShowProviders(request):
    if request.method == "POST":
        # Step 1: Get form data and strip spaces
        name = request.POST.get('provider_name', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        # Step 2: Create a dictionary to store validation errors
        errors = {}

        # Step 3: Validate required fields
        if not name:
            errors['provider_name'] = "Provider name is required."
        if not contact_person:
            errors['contact_person'] = "Contact person is required."
        if not phone:
            errors['phone'] = "Phone number is required."
            
        if Provider.objects.filter(name__iexact=name).exists():
            errors['provider_name'] = "This provider already exists."

        # Step 4: If there are errors, re-render the page with previous input + errors
        if errors:
            providers = Provider.objects.all()
            context = {
                'errors': errors,         # Field-specific errors
                'input': request.POST,    # To pre-fill the form with entered data
                'providers': providers    # List to show the table of providers
            }
            return render(request, 'providers.html', context)

        # Step 5: If no errors, save the provider
        provider = Provider.objects.create(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email
        )
        provider.save()

        # Step 6: Redirect to avoid re-submitting the form on refresh
        return redirect('/providers')  # Make sure this matches your URL name

    # Step 7: On GET request, just display the list of providers
    providers = Provider.objects.all()
    return render(request, 'providers.html', {'providers': providers})

def get_shipments_for_client(request):
    client_id = request.GET.get('client_id')
    if not client_id:
        return JsonResponse({'shipments': []})

    billed_ids = Bill.objects.values_list('shipments__id', flat=True)

    # ✅ USE THIS FIELD NAME
    shipments = Shipments.objects.filter(client_name_id=client_id).exclude(id__in=billed_ids)

    data = [{
        'id': s.id,
        'date': s.date.strftime("%d/%m/%Y"),
        'document_no': s.document_no,  # ✅ Ensure correct field
        'destination': s.destination,
        'service_type': s.service_type,
        'cost': float(s.cost)
    } for s in shipments]

    return JsonResponse({'shipments': data})

@require_POST
def create_bill(request):
    client_id = request.POST.get("client_id")
    bill_date = request.POST.get("bill_date")
    bill_period_from = request.POST.get("period_from")
    bill_period_to = request.POST.get("period_to")
    gst_rate = float(request.POST.get("gst_rate", 18))
    shipment_ids = request.POST.getlist("shipment_ids")

    if not shipment_ids:
        messages.error(request, "No shipments selected.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    client = get_object_or_404(Client, id=client_id)
    selected_shipments = Shipments.objects.filter(id__in=shipment_ids)

    bill_no = f"BILL-{timezone.now().strftime('%Y%m%d')}-{get_random_string(4).upper()}"

    # Ensure all numbers are float
    subtotal = sum(float(s.cost) for s in selected_shipments)
    fuel_percent = float(client.fuel_surcharge_percent or 0)
    fuel_charge = round((subtotal * fuel_percent) / 100, 2)
    gst_amount = round(((subtotal + fuel_charge) * gst_rate) / 100, 2)
    total_amount = round(subtotal + fuel_charge + gst_amount, 2)

    bill = Bill.objects.create(
    bill_no=bill_no,
    client=client,
    date=bill_date,
    bill_period_from=bill_period_from,
    bill_period_to=bill_period_to,
    gst_rate=gst_rate,
    subtotal=subtotal,
    fuel_charge=fuel_charge,
    gst_amount=gst_amount,
    total_amount=total_amount,
)

    bill.shipments.set(selected_shipments)
    messages.success(request, f"Bill {bill.bill_no} created successfully.")
    return redirect("/showbill")

def get_client_fuel_percent(request):
    client_id = request.GET.get('client_id')
    try:
        client = Client.objects.get(id=client_id)
        return JsonResponse({'fuel_percent': float(client.fuel_surcharge_percent)})
    except Client.DoesNotExist:
        return JsonResponse({'fuel_percent': 0})

def ShowBill(request):
    clients = Client.objects.all()
    shipments = Shipments.objects.filter(bill__isnull=True)
    bills = Bill.objects.select_related('client').prefetch_related('shipments').all()
    
    return render(request, 'bill.html', {
        'clients': clients,
        'shipments': shipments,
        'bills': bills,
    })

def show_bill_preview(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    # Optional: calculate taxable amount, CGST, SGST in view (if needed)
    taxable_amount = bill.subtotal + bill.fuel_charge + bill.additional_charges
    cgst = round((bill.gst_amount / 2), 2)
    sgst = round((bill.gst_amount / 2), 2)

    # Convert total amount to words (using `num2words`)
    try:
        amount_in_words = num2words(bill.total_amount, to='currency', lang='en_IN').replace('euro', 'rupees').title()
    except:
        amount_in_words = ""

    # Optional: Signature image URL (if stored statically or in media)
    signature_image_url = '/static/images/signature.png'  # Update path as per your project

    context = {
        'bill': bill,
        'cgst': cgst,
        'sgst': sgst,
        'taxable_amount': taxable_amount,
        'amount_in_words': amount_in_words,
        'signature_image_url': signature_image_url
    }

    return render(request, 'bill-preview.html', context)

