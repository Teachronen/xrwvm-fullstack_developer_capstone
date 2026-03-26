from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import logging
import json

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review


logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}

    return JsonResponse(response_data)


def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    username_exist = False

    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("%s is new user", username)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(response_data)
    else:
        response_data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(response_data)


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    response = get_request(endpoint)

    # 👇 זה התיקון הקריטי
    if isinstance(response, list):
        return JsonResponse({"status": 200, "dealers": response})
    else:
        return JsonResponse({"status": 500, "dealers": []})
        
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        response = get_request(endpoint)

        # fixing
        if isinstance(response, list):
            reviews = response
        else:
            reviews = []

        for review_detail in reviews:
            review_text = review_detail.get("review", "")
            sentiment_response = analyze_review_sentiments(review_text)

            if sentiment_response and "sentiment" in sentiment_response:
                review_detail["sentiment"] = sentiment_response["sentiment"]
            else:
                review_detail["sentiment"] = "neutral"

        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        response = get_request(endpoint)

        if isinstance(response, list) and len(response) > 0:
            return JsonResponse({"status": 200, "dealer": response[0]})
        elif isinstance(response, dict) and response:
            return JsonResponse({"status": 200, "dealer": response})
        else:
            return JsonResponse({"status": 404, "dealer": {}})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

@csrf_exempt
def add_review(request):
    print("request.user =", request.user)
    print("is_anonymous =", request.user.is_anonymous)

    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            print("add_review backend response =", response)

            if response:
                return JsonResponse({"status": 200, "response": response}, status=200)
            else:
                return JsonResponse({"status": 500, "message": "Failed to post review"}, status=500)
        except Exception as e:
            print("Error in posting review:", e)
            return JsonResponse({"status": 500, "message": "Error in posting review"}, status=500)
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"}, status=403)
        
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)

    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []

    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})