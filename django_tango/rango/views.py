from django.shortcuts import render
from .models import Page, Category, UserProfile
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

# from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.conf import settings
from datetime import datetime
from rango.flightaware_search import run_query


def index(request):
    request.session.set_test_cookie()
    # Construct a dictionary to pass to the template engine as its context.
    # # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    category_list = Category.objects.order_by("-likes")[:5]
    most_viewed_pages = Page.objects.order_by("-views")[:5]
    context_dict = {
        "categories": category_list,
        "top_5_pages": most_viewed_pages,
        # "category": None,
    }

    # Return a rendered response to send to the client.
    # # We make use of the shortcut function to make our lives easier.
    # # Note that the first parameter is the template we wish to use.

    visitor_cookie_handler(request)
    context_dict["visits"] = request.session["visits"]

    response = render(request, "rango/index.html", context=context_dict)
    return response


def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    # prints out whether the method is a GET or a POST
    print(request.method)
    # prints out the user name, if no one is logged in it prints `AnonymousUser`
    print(request.user)

    context_dict = {
        "yourname": "Tim Chase",
        "MEDIA_URL": settings.MEDIA_URL,
        "category": None,
    }
    visitor_cookie_handler(request)
    context_dict["visits"] = request.session["visits"]
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
        pages = Page.objects.filter(category=category).order_by("-views")
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

    # Handle search request
    if request.method == "POST":
        query = request.POST["query"].strip()
        if query:
            result_list = run_query(query)
            context_dict["result_list"] = result_list
            context_dict["query"] = query

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


# def register(request):
#     # A boolean value for telling the template
#     # whether the registration was successful.
#     # Set to False initially. Code changes value to
#     # True when registration succeeds.
#     registered = False

#     # If it's a HTTP POST, we're interested in processing form data.
#     if request.method == "POST":
#         # Attempt to grab information from the raw form information.
#         # Note that we make use of both UserForm and UserProfileForm.
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)

#         # If the two forms are valid...
#         if user_form.is_valid() and profile_form.is_valid():
#             # Save the user's form data to the database.
#             user = user_form.save()

#             # Now we hash the password with the set_password method.
#             # Once hashed, we can update the user object.
#             user.set_password(user.password)
#             user.save()

#             # Now sort out the UserProfile instance.
#             # Since we need to set the user attribute ourselves,
#             # we set commit=False. This delays saving the model
#             # until we're ready to avoid integrity problems.
#             profile = profile_form.save(commit=False)
#             profile.user = user

#             # Did the user provide a profile picture?
#             # If so, we need to get it from the input form and
#             # put it in the UserProfile model.
#             if "picture" in request.FILES:
#                 profile.picture = request.FILES["picture"]

#             # Now we save the UserProfile model instance.
#             profile.save()

#             # Update our variable to indicate that the template
#             # registration was successful.
#             registered = True
#         else:
#             # Invalid form or forms - mistakes or something else?
#             # Print problems to the terminal.
#             print(user_form.errors, profile_form.errors)
#     else:
#         # Not a HTTP POST, so we render our form using two ModelForm instances.
#         # These forms will be blank, ready for user input.

#         user_form = UserForm()
#         profile_form = UserProfileForm()

#     # Render the template depending on the context.
#     return render(
#         request,
#         "rango/register.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#             "registered": registered,
#         },
#     )


# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(username=username, password=password)
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse("index"))
#             else:
#                 return HttpResponseRedirect("Your Rango account is disabled")
#         else:
#             print("Invalid login details: {0}, {1}".format(username, password))
#             return HttpResponse("Invalid login details supplied.")
#     else:
#         return render(request, "rango/login.html", {})


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse("index"))


@login_required
def restricted(request):
    return render(request, "rango/restricted.html")


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, "visits", "1"))
    last_visit_cookie = get_server_side_cookie(
        request, "last_visit", str(datetime.now())
    )
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session["last_visit"] = str(datetime.now())
    else:
        request.session["last_visit"] = last_visit_cookie
    request.session["visits"] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def search(request):
    result_list = []
    context_dict = {}

    if request.method == "POST":
        query = request.POST["query"].strip()
        if query:
            result_list = run_query(query)
            context_dict["result_list"] = result_list
            context_dict["query"] = query
    return render(request, "rango/search.html", context_dict)


def track_url(request):
    page_id = None
    url = "/rango/"
    if request.method == "GET":
        if "page_id" in request.GET:
            page_id = request.GET["page_id"]
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect("index")
        else:
            print(form.errors)

    context_dict = {"form": form}

    return render(request, "rango/profile_registration.html", context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect("index")

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {"website": userprofile.website, "picture": userprofile.picture}
    )

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect("profile", user.username)
        else:
            print(form.errors)

    return render(
        request,
        "rango/profile.html",
        {"userprofile": userprofile, "selecteduser": user, "form": form},
    )


@login_required
def list_profiles(request):
    userprofile_list = User.objects.all()

    return render(
        request, "rango/list_profiles.html", {"userprofile_list": userprofile_list},
    )


@login_required
def like_category(request):
    cat_id = None
    if request.method == "GET":
        # cat_id = request.GET["category_id"]
        cat_id = request.GET["cat_id"]
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=""):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ""

    if request.method == "GET":
        starts_with = request.GET["suggestion"]
    cat_list = get_category_list(8, starts_with)

    return render(request, "rango/cats.html", {"cats": cat_list})
