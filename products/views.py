from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category
from .forms import ProductForm

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """
    """
    Defining a Django view function named all_products to display all products, 
    including handling sorting and search queries. Initializing variables products, 
    query, categories, sort, and direction with default values.
    """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    """
    Checking if there are any parameters in the GET request.
    If 'sort' is present, extracting the sorting key from the GET parameters. 
    If the sorting key is 'name', it's converted to 'lower_name' and products 
    are annotated with the lowercased name. Sorting is then done based on the selected key.
    If 'direction' is present, extracting the sorting direction. If it's 'desc', 
    the sorting key is prefixed with '-' to indicate descending order. Sorting the products accordingly.
    """
    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
        
        """
        If 'category' is present in the GET parameters, extracting 
        and splitting the category names. Filtering the products to include 
        only those in the specified categories and updating the categories 
        variable with the corresponding Category objects.
        """
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        """
        If 'q' (search term) is present in the GET parameters, extracting the search query. 
        If no query is provided, showing an error message and redirecting to the 'products' view.
        Constructing a complex query using the Q class to search for products with names or 
        descriptions containing the search term. Filtering the products based on the constructed query.
        """
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    """
    Creating a string current_sorting to represent the current sorting configuration.
    Creating a dictionary context containing data to be passed to the template, including
    the filtered products, search term, current categories, and sorting configuration.
    Rendering the 'products.html' template with the provided context.
    """
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)

"""
Using get_object_or_404 to get the product with the specified product_id 
or return a 404 response if the product is not found.
Creating a dictionary context containing the product to be passed to the template.
Rendering the 'product_detail.html' template with the provided context.
"""
def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)


def add_product(request):
    """ Add a product to the store """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


def edit_product(request, product_id):
    """ Edit a product in the store """
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)