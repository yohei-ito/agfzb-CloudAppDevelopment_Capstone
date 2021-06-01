import requests
import json
import asyncio
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    print("API Key {} ".format(api_key))
    try:
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data



# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        #dealers = json_result["rows"]
        dealers = json_result["dealership"]
        #print(dealers)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], state=dealer_doc["state"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result["review"]
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            print(review_doc["purchase"])
            if review_doc["purchase"]:
                # Create a Carreview object with values in `doc` object
                print("true proc")
                review_obj = DealerReview(dealership=review_doc["dealership"],name=review_doc["name"], purchase=review_doc["purchase"],
                                    review=review_doc["review"], purchase_date=review_doc["purchase_date"], car_make=review_doc["car_make"],
                                    car_model=review_doc["car_model"], car_year=review_doc["car_year"],
                                    id=review_doc["id"])
            else:
                print("false proc")
                review_obj = DealerReview(dealership=review_doc["dealership"],name=review_doc["name"], purchase=review_doc["purchase"],
                                    review=review_doc["review"],purchase_date=None, car_make=None,
                                    car_model=None, car_year=None,
                                    id=review_doc["id"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)

            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    result = "Not checked"
    print(text)
    try:
        json_result = get_request(url="https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/6521efe7-d9ad-4487-b0e6-443e6e7e2639/v1/analyze",
                        api_key="P3iXa9KQMrou-auXaJ034eDh1f4igclRepwmdZ_vsTDP",
                        version="2021-03-25",
                        features="sentiment",
                        language="en",
                        text=text)
        result = json_result["sentiment"]["document"]["label"]
        print(result)
    finally:
        return result
