from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
#from .models import related models
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html', {})


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html', {})

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login_bootstrap.html', context)
    else:
        return render(request, 'djangoapp/user_login_bootstrap.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    dealership_list = []
    if request.method == "GET":
        url = "https://645999e8.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context["dealership_list"] = dealerships
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://645999e8.us-south.apigw.appdomain.cloud/api/review"
        # Get dealers from the URL
        dealer_details = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        # Concat all dealer's short name
        #dealer_details_reviews = ' '.join([dealer_detail.sentiment for dealer_detail in dealer_details])
        context["review_list"] = dealer_details
        context["dealer_id"] = dealer_id
        # Return a list of dealer short name
        #return HttpResponse(dealer_details_reviews)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
    context = {}
    if request.method == 'GET':
        print("GET add_review")
        #return HttpResponse("GET add_reviews for dealerId %s." % dealer_id)
        #url = "https://645999e8.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        #dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_details_reviews = ' '.join([dealer_detail.sentiment for dealer_detail in dealer_details])
        #context["dealership_list"] = dealerships
        context["dealer_id"] = dealer_id
        context["cars"] = CarModel.objects.all()
        print(CarModel.objects.all())
        # Return a list of dealer short name
        #return HttpResponse(dealer_details_reviews)
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        print("POST add_review")
        #review = {}
        #user = self.request.user
        #if user.is_authenticated:
        #print("authenticated")
        #set requested data
        #review['name']= request.POST['name']
        #review['dealerid'] = dealer_id
        #review['review'] = request.POST['review']

        form = request.POST
        review = {
            "name": "{request.user.first_name} {request.user.last_name}",
            "dealerid": dealer_id,
            "review": form["content"],
            "purchase": bool(form.get("purchasecheck")),
            "id": 99
            }
        if form.get("purchasecheck"):
            review["purchase_date"] = datetime.strptime(form.get("purchase_date"), "%m/%d/%Y").isoformat()
            car = models.CarModel.objects.get(pk=form["car"])
            review["car_make"] = car.carmaker.name
            review["car_model"] = car.name
            review["car_year"]= car.year.strftime("%Y")
            #review["purchase"] = "ture"

        print(review)

        url="https://645999e8.us-south.apigw.appdomain.cloud/api/review"

        json_result = post_request(url, review, dealerId=dealer_id)
        print("---json_result---")
        print(json_result)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        #else:
            #print("NOT authenticated")


# ...
