# Import the Decimal class from the decimal module to handle precise decimal arithmetic
from decimal import Decimal

# Import the 'settings' module from 'django.conf' to access project settings
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

# Define a function named 'bag_contents' that takes a 'request' as a parameter
def bag_contents(request):

    # Initialize an empty list to store bag items
    bag_items = []
    
    # Initialize variables for total cost, total product count, and grand total
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            total += item_data * product.price
            product_count += item_data
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            product = get_object_or_404(Product, pk=item_id)
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                })


    # Check if the total cost is less than the FREE_DELIVERY_THRESHOLD from project settings
    if total < settings.FREE_DELIVERY_THRESHOLD:
        # Calculate the delivery cost based on a percentage of the total
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # Calculate the remaining amount for free delivery
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        # If the total is equal or exceeds the FREE_DELIVERY_THRESHOLD, set delivery cost and delta to zero
        delivery = 0
        free_delivery_delta = 0
    
    # Calculate the grand total by adding delivery cost to the total
    grand_total = delivery + total
    
    # Create a context dictionary containing relevant information
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    # Return the context dictionary
    return context
