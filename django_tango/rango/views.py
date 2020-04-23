from django.shortcuts import render
from .models import Page, Category
from rango.forms import CategoryForm, PageForm

# from django.urls import reverse
from django.shortcuts import redirect


from django.conf import settings


def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    category_list = Category.objects.order_by("-likes")[:5]
    most_viewed_pages = Page.objects.order_by("-views")[:5]
    context_dict = {
        "categories": category_list,
        "top_5_pages": most_viewed_pages,
        "category": None,
    }
    # Return a rendered response to send to the client.
    # # We make use of the shortcut function to make our lives easier.
    # # Note that the first parameter is the template we wish to use.
    return render(request, "rango/index.html", context=context_dict)


def about(request):
    # prints out whether the method is a GET or a POST
    print(request.method)
    # prints out the user name, if no one is logged in it prints `AnonymousUser`
    print(request.user)

    context_dict = {
        "yourname": "Tim Chase",
        "MEDIA_URL": settings.MEDIA_URL,
        "category": None,
    }
    return render(request, "rango/about.html", context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)
        # Adds our results list to the template context under name pages.
        context_dict["pages"] = pages
        # We also add the category object from
        # # the database to the context dictionary.
        # # We'll use this in the template to verify that the category exists.
        context_dict["category"] = category

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything

        # the template will display the "no category" message for us.
        context_dict["category"] = None
        context_dict["pages"] = None

    # Go render the response and return it to the client.
    return render(request, "rango/category.html", context_dict)


def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == "POST":
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page
            # Then we can direct the user back to the index page.
            # return redirect("index")
            return index(request)

            # The supplied form contained errors
            # just print them to the terminal.
        else:
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, "rango/add_category.html", {"form": form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    # A HTTP POST?
    if request.method == "POST":
        form = PageForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                # return show_category(request, category_name_slug)
                return redirect("show_category", category_name_slug)
            # Save the new page to the database.

            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page
            # Then we can direct the user back to the index page.

            # The supplied form contained errors
            # just print them to the terminal.
            else:
                print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    context_dict = {"form": form, "category": category}
    return render(request, "rango/add_page.html", context_dict)


# Create your views here.
