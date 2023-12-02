from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """A view that renders the bag contents page"""

    return render(request, "bag/bag.html")


# Define a function that adds a quantity of a product to a shopping bag
def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the shopping bag"""

    # Get the quantity of the product from the user's input
    quantity = int(request.POST.get("quantity"))

    # Get the URL to redirect to after updating the bag
    redirect_url = request.POST.get("redirect_url")
    size = None
    # Check if 'product_size' is present in the user's input (from a form submission)
    if "product_size" in request.POST:
    # If 'product_size' is present, get its value
        size = request.POST["product_size"]

    # Get the current shopping bag from the user's session, or create an empty one if not present
    bag = request.session.get("bag", {})
    # Check if a size is specified for the product
    if size:
        # Check if the product is already in the bag
        if item_id in list(bag.keys()):
            # Check if the specified size is already in the product's sizes in the bag
            if size in bag[item_id]["items_by_size"].keys():
                # If yes, increase the quantity of the product with the specified size in the bag
                bag[item_id]["items_by_size"][size] += quantity
            else:
                # If the size is not present for the product, add a new entry for the size with the specified quantity
                bag[item_id]["items_by_size"][size] = quantity
        else:
            # If the product is not in the bag, create a new entry with the specified size and quantity
            bag[item_id] = {"items_by_size": {size: quantity}}
    else:
        # If no size is specified, check if the product is already in the bag
        if item_id in list(bag.keys()):
            # If yes, increase its quantity in the bag
            bag[item_id] += quantity
        else:
            # If not, add a new entry for the product with the specified quantity
            bag[item_id] = quantity

        # Update the shopping bag in the user's session
        request.session["bag"] = bag

        # Redirect the user to the specified URL
        return redirect(redirect_url)
