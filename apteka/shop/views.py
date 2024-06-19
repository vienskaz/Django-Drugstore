import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .models import *
from .forms import *
from django.views import View
from django.views.generic import ListView
import random
from . utils import *
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
import csv



def home(request):
    items = Item.objects.all()
    random_items = random.sample(list(items), 3)

    context = {"random_items": random_items}

    return render(request, "shop/home.html", context)


def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('account')
            else:
                return redirect('login')
        else:
            return render(request, "shop/login.html")
    else:
        return render(request, "shop/account.html")


def logout_user(request):
    logout(request)
    return redirect('login')


class Account(View):
    def get(self, request):
        user = request.user
        context = {'user': user}

        return render(request, "shop/account.html", context)


def register_view(request):
    if request.method == "POST":
        form = CustomRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            customer, created = Customer.objects.get_or_create(user=user)
            customer.first_name = first_name
            customer.last_name = last_name
            customer.email = email
            customer.save()

            login(request, user)
            return redirect('account')
    else:
        form = CustomRegistrationForm()

    return render(request, 'shop/register.html', {'form': form})


class ItemsView(ListView):
    model = Item
    template_name = "shop/products.html"
    context_object_name = "all_items"
    form_class = ItemSearchForm
    paginate_by = 10  
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')  
        form = self.form_class(self.request.GET)
        
        if form.is_valid():
            query = form.cleaned_data.get('szukaj')
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(active_drug__name__icontains=query) |
                    Q(price__icontains=query)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form_class(self.request.GET)
        return context
    

class SingleItem(View):
    def get(self, request, slug):
        item = Item.objects.get(slug=slug)

        context = {
            "item": item
        }
        return render(request, "shop/item-detail.html", context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order}
    return render(request, 'shop/cart.html', context)



@csrf_exempt
def checkout(request):
    data = cartData(request)
    print("Debug: cartData:", data)  
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    requires_prescription = any(
        item.item.prescription if request.user.is_authenticated else item['item']['prescription'] for item in items
    )

    conflicts_map = {}

    for cart_item in items:
        try:
            if request.user.is_authenticated:
                product_name = cart_item.item.name
                active_drug = cart_item.item.active_drug
            else:
                product_name = cart_item['item']['name']
                print(f"Debug: cart_item['item'] = {cart_item['item']}")
                active_drug_name = cart_item['item'].get('active_drug')
                print(f"Debug: active_drug_name = {active_drug_name}")

                if active_drug_name:
                    active_drug = ActiveDrug.objects.get(name=active_drug_name)
                    print(f"Debug: active_drug = {active_drug}")
                else:
                    active_drug = None

            if active_drug:
                conflicts_query = ActiveDrug.objects.filter(
                    Q(id__in=active_drug.conflicts.all()) | Q(conflicts=active_drug)
                )
                product_conflicts = list(conflicts_query.values_list('name', flat=True))
                print(f"Debug: product_conflicts for {active_drug.name} = {product_conflicts}")

                if product_conflicts:
                    conflicts_map[active_drug.name] = product_conflicts

        except (AttributeError, KeyError, ActiveDrug.DoesNotExist) as e:
            print(f"Debug: Exception = {str(e)}")

 
    conflict_found = any(
        key in conflicts_map and any(key in values for values in conflicts_map.values())
        for key in conflicts_map.keys()
    )

    if conflict_found:
        print("Znaleziono konflikt!")
    else:
        print("Nie znaleziono konfliktów.")
    print(conflicts_map)

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'requires_prescription': requires_prescription,
        'conflicts_map': conflicts_map,
        'conflict_found': conflict_found
    }

    return render(request, 'shop/checkout.html', context)





def updateItem(request):
    data = json.loads(request.body)
    itemId = data['itemId']
    action = data['action']
    print('Action:', action)
    print('Item:', itemId)

    customer = request.user.customer
    item = Item.objects.get(id=itemId)
    order, created = Order.objects.get_or_create(
        customer=customer,complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, item=item)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
        order.save()


        address = Address.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            country=data['shipping']['country']
        )

        address.save()


        return JsonResponse('Payment complete', safe=False)
    else:
        return JsonResponse('Payment failed - total mismatch', status=400)




def upload_prescription(request):
    if request.method == 'POST' and request.FILES['pdf_prescription']:
        pdf_file = request.FILES['pdf_prescription']
        order_id = request.POST.get('order_id')
    
        try:
            order = Order.objects.get(id=order_id)
            new_prescription = Prescription(pdf_prescription=pdf_file, order=order)
            new_prescription.save()
            return JsonResponse({'message': 'Recepta została pomyślnie przesłana.'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Nie znaleziono zamówienia o podanym ID.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Wystąpił błąd podczas przesyłania recepty.'}, status=400)
    




def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leki.csv"'
    writer = csv.writer(response)
    records = Item.objects.all()
    writer.writerow(['name', 'active_drug', 'price'])  
    for record in records:
        writer.writerow([record.name, record.active_drug, record.price])  

    return response





