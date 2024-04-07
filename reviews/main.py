from fastapi import FastAPI, HTTPException,APIRouter,Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from . import  models, schemas
import requests
import time
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

router=APIRouter()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


api_key = ('jCdg8QbUu-PAHoTT7IMS3yZTkrnNXYSUF-_DtKMhmCs7Dbg4mG_q0_EkaEWaFLPlELm6y5JzyS8wYqjhJ4BiwNNe0ZJb0iJsU20TC7EUOkAO0Gn90K5EAZtBzfqLZXYx')


# Endpoint to fetch Yelp reviews and store them in the database
# @router.get("/store-reviews/", tags=["add-review"])
# def fetch_all_reviews(restaurant_name:str, location:str,db: Session = Depends(get_db)):
#     # Set the API endpoint for business search
#     url = 'https://api.yelp.com/v3/businesses/search'

#     # Set the request headers including the API key
#     headers = {
#         'Authorization': f'Bearer {api_key}',
#     }

#     # Set the parameters for the search query (you can add more parameters as needed)
#     params = {
#         'term':restaurant_name,
#         'location':location ,  # Replace with the location of the restaurant
#         # 'limit': 10,  # Number of businesses to return
#     }
#     # Make a GET request to search for businesses
#     response = requests.get(url, headers=headers, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         businesses = data.get('businesses', [])

#         if businesses:
#             # Get the first business (restaurant)
#             first_business_id = businesses[0]['id']

#             # Initialize variables for pagination
#             reviews = []
#             offset = 0
#             total_reviews = 1  # Initialize total_reviews to a non-zero value

#             # Set the API endpoint for fetching reviews of the restaurant
#             reviews_url = f'https://api.yelp.com/v3/businesses/{first_business_id}/reviews'
#             # reviews_response = requests.get(reviews_url, headers=headers)

#             # if reviews_response.status_code == 200:
#             #     reviews_data = reviews_response.json()
#             #     reviews = reviews_data.get('reviews', [])
            
#             # Fetch all reviews using pagination
#             while len(reviews) < total_reviews:
#                 reviews_response = requests.get(reviews_url, headers=headers, params={'limit': 50, 'offset': offset})
                
#                 if reviews_response.status_code == 200:
#                     reviews_data = reviews_response.json()
#                     reviews.extend(reviews_data.get('reviews', []))
#                     total_reviews = reviews_data.get('total', 0)
#                     offset += 50

#                 else:
#                     print("Error fetching reviews:", reviews_response.text)
#                     break
                    

#             if reviews:
#                 # Display all fetched reviews
#                for idx, review in enumerate(reviews, start=1):
#                     name = review.get('user', {}).get('name')
#                     rating = review.get('rating')
#                     text = review.get('text')
#                     submission_time = review.get('time_created')

#                     # Store review in the database
#                     new_review = models.YelpReview(restaurant_name=restaurant_name,location=location,name=name, rating=rating, text=text, submission_time=submission_time)
#                     db.add(new_review)
#                db.commit()  
#                return {"message": "Yelp reviews fetched and stored successfully for {len(reviews)} reviews"}
#             else:
#                 raise HTTPException(status_code=404, detail="No reviews found for the restaurant")
#         else:
#             print("No businesses found.")
#     else:
#         print("Error fetching businesses:", response.text)

@router.get("/get-reviews/", tags=["add-review"])
def get_all_reviews(restaurant_name:str, location:str,db: Session = Depends(get_db)):
    reviews = db.query(models.YelpScrapReview).filter(
        models.YelpScrapReview.restaurant_name == restaurant_name,
        models.YelpScrapReview.location == location
    ).all()

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for the specified restaurant and location")

    return reviews



      
@router.get("/full-reviews/", tags=["add-review"])
def all_reviews(restaurant_name:str, location:str,db: Session = Depends(get_db)):
   # Set the API endpoint for business search
    url = 'https://api.yelp.com/v3/businesses/search'

    # Set the request headers including the API key
    headers = {
        'Authorization': f'Bearer {api_key}',
    }

    # Set the parameters for the search query (you can add more parameters as needed)
    params = {
        'term':restaurant_name,
        'location':location ,  # Replace with the location of the restaurant
    }
    response = requests.get(url, headers=headers, params=params)

    # Make a GET request to search for businesses
    if response.status_code == 200:
        data = response.json()
        businesses = data.get('businesses', [])

        if businesses:
            # Get the first business (restaurant)
            first_business_id = businesses[0]['id']

            for business in businesses:
            

                next_page_token="eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0Ijo5fQ=="
                while (next_page_token != None):

                    url = 'https://www.yelp.com/gql/batch'
                    # Define the request body
                    body = [{
                        "operationName": "GetBusinessReviewFeed",
                        "variables": {
                            # "encBizId": business['id'],
                            "encBizId": first_business_id,
                            "reviewsPerPage": 10,
                            "selectedReviewEncId": "",
                            "hasSelectedReview": False,
                            "sortBy": "RELEVANCE_DESC",
                            "languageCode": "en",
                            "ratings": [5, 4, 3, 2, 1],
                            "queryText": "",
                            "isSearching": False,
                            "after": next_page_token,
                            "isTranslating": False,
                            "translateLanguageCode": "en",
                            "reactionsSourceFlow": "businessPageReviewSection",
                            "guv": "BB5EFAFEB38E1723",
                            "minConfidenceLevel": "HIGH_CONFIDENCE",
                            "highlightType": "",
                            "highlightIdentifier": "",
                            "isHighlighting": False
                        },
                        "extensions": {
                            "operationType": "query",
                            "documentId": "7815a1d734b7bbf381ef5e9f87c73ade6346d850da7e9dc05f471868cfb4963a"
                        }
                    }]

                    # Define headers (if any)
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    # Make the POST request
                    response = requests.post(url, json=body, headers=headers)
                    print("response:",response)
                    # break

                    # Check if the request was successful
                    if response.status_code == 200:
                        # Print the response content (reviews)
                        reviews_data = response.json()
                        # print(reviews_data)
                        # print(review['data']['business']['reviews']['pageInfo']['endCursor'])
                        # break
                    # else:
                    #     # Print error message if the request fails
                    #     print(f"Error: {response.status_code} - {response.text}")
                        if reviews_data:
                             # Display the reviews
                            for idx, review in enumerate(reviews_data, start=1):
                                node=review['data']['business']['reviews']['edges']
                                restaurant_name=review['data']['business']['name']

                                next_page_token=review['data']['business']['reviews']['pageInfo']['endCursor']
                                for idx, reviewlisting in enumerate(node, start=1):
                                    review_id=reviewlisting['node']['encid']
                                    existing_review = db.query(models.YelpReview).filter_by(review_id=review_id).first()
                                    if existing_review is None:
                                    #  print(f"Review with ID {review_id} already exists. Skipping.")
                                     
                                    # else:
                                        name = reviewlisting['node']['author']['displayName']
                                        # rating_id = reviewlisting['node']['encid']
                                        rating = reviewlisting['node']['rating']
                                        text = reviewlisting['node']['text']['full']
                                        submission_time = reviewlisting['node']['createdAt']['utcDateTime']
                                        new_review = models.YelpReview(restaurant_name=restaurant_name,location=location,review_id=review_id,name=name, rating=rating, text=text, submission_time=submission_time)
                                        db.add(new_review)
                                db.commit() 

                                                                            
                        else:
                            # next_page_token = None
                            print("No reviews found for the restaurant.")
                        
                    else:
                        # next_page_token=None
                        print("No businesses found.")
                break
                

    else:
        print("Error fetching businesses:", response.text)

#get all_reviews
@router.get("/all_reviews/", tags=["add-review"])
def all_reviews(restaurant_name:str, location:str,db: Session = Depends(get_db)):
    reviews = db.query(models.YelpReview).filter(models.YelpReview.restaurant_name == restaurant_name,models.YelpReview.location == location).all()
    return reviews



# @router.get("/final_reviews/", tags=["add-review"])
# def final_reviews(restaurant_name:str, location:str,db: Session = Depends(get_db)):
#     # Set the API endpoint for business search
#     url = 'https://api.yelp.com/v3/businesses/search'

#     # Set the request headers including the API key
#     headers = {
#         'Authorization': f'Bearer {api_key}',
#     }

#     # Set the parameters for the search query (you can add more parameters as needed)
#     params = {
#         'term':restaurant_name,
#         'location':location ,  # Replace with the location of the restaurant
#          'limit': 10,  # Number of businesses to return
#     }
#     # Make a GET request to search for businesses
#     response = requests.get(url, headers=headers, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         businesses = data.get('businesses', [])

#         if businesses:
#             # Get the first business (restaurant)
#             first_business_id = businesses[0]['id']
#             review_count = businesses[0]['review_count']
#             print("totalNumberOfReview",review_count)


#             url = 'https://www.yelp.com/gql/batch'

#             # Define the request body
#             body = [{
#                 "operationName": "GetBusinessReviewFeed",
#                 "variables": {
#                     "encBizId": first_business_id,
#                     "reviewsPerPage": review_count-550,
#                     "selectedReviewEncId": "",
#                     "hasSelectedReview": False,
#                     "sortBy": "RELEVANCE_DESC",
#                     "languageCode": "en",
#                     "ratings": [5, 4, 3, 2, 1],
#                     "queryText": "",
#                     "isSearching": False,
#                     "after": "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0Ijo5fQ==",
#                     "isTranslating": False,
#                     "translateLanguageCode": "en",
#                     "reactionsSourceFlow": "businessPageReviewSection",
#                     "guv": "BB5EFAFEB38E1723",
#                     "minConfidenceLevel": "HIGH_CONFIDENCE",
#                     "highlightType": "",
#                     "highlightIdentifier": "",
#                     "isHighlighting": False
#                 },
#                 "extensions": {
#                     "operationType": "query",
#                     "documentId": "7815a1d734b7bbf381ef5e9f87c73ade6346d850da7e9dc05f471868cfb4963a"
#                 }
#             }]

#             # Define headers (if any)
#             headers = {
#                 'Content-Type': 'application/json'
#             }

#             # Make the POST request
#             response = requests.post(url, json=body, headers=headers)


#             # Check if the request was successful
#             if response.status_code == 200:
#                 # Print the response content (reviews)
#                 reviews_data = response.json()
#                 print(reviews_data)
#             # else:
#             #     # Print error message if the request fails
#             #     print(f"Error: {response.status_code} - {response.text}")
                
                                

#             if reviews_data:
                
#                 # Display all fetched reviews
#                for idx, review in enumerate(reviews_data, start=1):
#                    node=review['data']['business']['reviews']['edges']
#                    for idx, reviewlisting in enumerate(node, start=1):

#                     review_id=reviewlisting['node']['encid']
#                     name = reviewlisting['node']['author']['displayName']
#                     rating_id = reviewlisting['node']['encid']
#                     rating = reviewlisting['node']['rating']
#                     text = reviewlisting['node']['text']['full']
#                     submission_time = reviewlisting['node']['createdAt']['utcDateTime']

#                     # Store review in the database
#                     new_review = models.YelpReview(restaurant_name=restaurant_name,location=location,review_id=review_id,name=name,rating_id=rating_id, rating=rating, text=text, submission_time=submission_time)
#                     db.add(new_review)
#                db.commit() 
#                reviews = db.query(models.YelpReview).filter(
#         models.YelpReview.restaurant_name == restaurant_name,
#         models.YelpReview.location == location
#     ).all()

#             #    return {"message": "Yelp reviews fetched and stored successfully for  reviews"}
#                return reviews
#             else:
            
#                 raise HTTPException(status_code=404, detail="No reviews found for the restaurant")


#         else:
#             print("No businesses found.")
#     else:
#         print("Error fetching businesses:", response.text)


#scarp-data
@router.get("/scrap_reviews/", tags=["add-review"])
def scrap_reviews(location:str,db: Session = Depends(get_db)):
    url = 'https://api.yelp.com/v3/businesses/search'

    # Set the request headers including the API key
    headers = {
        'Authorization': f'Bearer {api_key}',
    }

    params = {
        # 'term': 'Girl & The Goat',
        # 'location': 'Washington D.C., DC, United States',  
        'location':location,
        'limit': 1,
        'offset':31

    }
    # Make a GET request to search for businesses
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # print("===========",data)
        businesses = data.get('businesses', [])
        # businesses = [{id:"DA2yuJeyRlhAQnoChpNc2g"},{id:""}]
        # print("+++++++++",businesses)

        if businesses:
            # Get the first business (restaurant)
            # businesses_id = len(businesses)
            # print("#########",businesses_id)
            for business in businesses:
                # print("id:",business['id'])
                print("review_Count:",business['review_count'])

                next_page_token="eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0Ijo5fQ=="
                while (next_page_token != None):

                    url = 'https://www.yelp.com/gql/batch'
                    # Define the request body
                    body = [{
                        "operationName": "GetBusinessReviewFeed",
                        "variables": {
                            "encBizId": business['id'],
                            # "encBizId": "DA2yuJeyRlhAQnoChpNc2g",
                            "reviewsPerPage": 20,
                            "selectedReviewEncId": "",
                            "hasSelectedReview": False,
                            "sortBy": "RELEVANCE_DESC",
                            "languageCode": "en",
                            "ratings": [5, 4, 3, 2, 1],
                            "queryText": "",
                            "isSearching": False,
                            "after": next_page_token,
                            "isTranslating": False,
                            "translateLanguageCode": "en",
                            "reactionsSourceFlow": "businessPageReviewSection",
                            "guv": "BB5EFAFEB38E1723",
                            "minConfidenceLevel": "HIGH_CONFIDENCE",
                            "highlightType": "",
                            "highlightIdentifier": "",
                            "isHighlighting": False
                        },
                        "extensions": {
                            "operationType": "query",
                            "documentId": "7815a1d734b7bbf381ef5e9f87c73ade6346d850da7e9dc05f471868cfb4963a"
                        }
                    }]

                    # Define headers (if any)
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    # Make the POST request
                    response = requests.post(url, json=body, headers=headers)
                    # print("response:",response)
                    # break
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Print the response content (reviews)
                        reviews_data = response.json()
                        # print(reviews_data)
                        # print(review['data']['business']['reviews']['pageInfo']['endCursor'])
                        # break
                    # else:
                    #     # Print error message if the request fails
                    #     print(f"Error: {response.status_code} - {response.text}")
                        if reviews_data:
                             # Display the reviews
                            for idx, review in enumerate(reviews_data, start=1):
                                node=review['data']['business']['reviews']['edges']
                                restaurant_name=review['data']['business']['name']
                                #next_page_token_value
                                next_page_token=review['data']['business']['reviews']['pageInfo']['endCursor']
                                for idx, reviewlisting in enumerate(node, start=1):
                                    source = "yelp"
                                    review_id=reviewlisting['node']['encid']
                                    existing_review = db.query(models.YelpScrapReview).filter_by(review_id=review_id).first()
                                    if existing_review is None:
                                        name = reviewlisting['node']['author']['displayName']
                                        rating = reviewlisting['node']['rating']
                                        text = reviewlisting['node']['text']['full']
                                        submission_time = reviewlisting['node']['createdAt']['utcDateTime']
                                        new_review = models.YelpScrapReview(source=source,restaurant_name=restaurant_name,location=location,review_id=review_id,name=name, rating=rating, text=text, submission_time=submission_time)
                                        db.add(new_review)
                                db.commit() 
                                                
                        else:
                            next_page_token = None
                            print("No reviews found for the restaurant.")
                    elif response.status_code == 500:
                        print("error: system error")
                        time.sleep(10)
                    else:
                        next_page_token=None
                        print("No businesses found.")
                time.sleep(30)
                
                # break
            # time.sleep(60)
    else:
        print("Error fetching businesses:", response.text)

        


