# streamlit run 'C:\Users\Dell\Desktop\food-web-app\food_app\recipe.py'

import streamlit as st
import pickle
import pandas as pd
import requests
import re
from dotenv import  load_dotenv
import os

load_dotenv()

def get_food_recommendations_from_api(food):
    app_id = os.getenv('app_id')
    app_key = os.getenv('app_key')
    
    url = f'https://api.edamam.com/api/recipes/v2?type=public&app_id={app_id}&app_key={app_key}&q={food}'

    try:
        # Make a GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            api_data = response.json()

            # Initialize lists to store food labels and image URLs
            labels = []
            image_urls = []

            # Extracting labels and image URLs from the response
            hits = api_data.get('hits', [])
            for hit in hits[:6]:  # Loop through the first 7 hits
                recipe = hit.get('recipe', {})
                label = recipe.get('label')
                if label:
                    # Use regular expression to extract only food names
                    food_name = re.search(r'^([\w\s-]+)', label).group(1)
                    labels.append(food_name)
                    image_url = recipe.get('image')
                    image_urls.append(image_url)

            return labels, image_urls
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None, None
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None
    
def recommend_food(food):
    recommended_foods = []  # Initialize an empty list to store recommendations
    image_urls = []  # Initialize an empty list to store image URLs
    
    # Check in dataset 1
    if food in core['recipe_name'].values:
        food_index = core[core['recipe_name'] == food].index[0]
        distances = similarity1[food_index]
        food_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
        for i in food_list:
            recommended_foods.append(core.iloc[i[0]].recipe_name)  # Append each recommendation to the list
            image_urls.append(core.iloc[i[0]].image_url)  # Append corresponding image URL
        return recommended_foods, image_urls, core[core['recipe_name'] == food].iloc[0]['image_url']
    
    # Check in dataset 2
    elif food in raw['recipe_name'].values:
        food_index = raw[raw['recipe_name'] == food].index[0]
        distances = similarity2[food_index]
        food_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
        for i in food_list:
            recommended_foods.append(raw.iloc[i[0]].recipe_name)  # Append each recommendation to the list
            image_urls.append(raw.iloc[i[0]].image_url)  # Append corresponding image URL
        return recommended_foods, image_urls, raw[raw['recipe_name'] == food].iloc[0]['image_url']
    
    # Check in dataset 3
    elif food in indian['recipe_name'].values:
        food_index = indian[indian['recipe_name'] == food].index[0]
        distances = similarity3[food_index]
        food_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
        for i in food_list:
            recommended_foods.append(indian.iloc[i[0]].recipe_name)  # Append each recommendation to the list
            image_urls.append(indian.iloc[i[0]].image_url)  # Append corresponding image URL
        return recommended_foods, image_urls, indian[indian['recipe_name'] == food].iloc[0]['image_url']
    
    # If not found in any dataset, call the API
    else:
        recommendations, image_urls = get_food_recommendations_from_api(food)
        if recommendations:
            return recommendations, image_urls, image_urls[0]
        else:
            return [], [], None


# Load the pickle file and other necessary data
core_dict = pickle.load(open('core_food.pkl', 'rb'))
raw_dict = pickle.load(open('raw_food.pkl', 'rb'))
indian_dict = pickle.load(open('indian_food.pkl', 'rb'))

similarity1 = pickle.load(open('similarity1.pkl','rb'))
similarity2 = pickle.load(open('similarity2.pkl','rb'))
similarity3 = pickle.load(open('similarity3.pkl','rb'))

core = pd.DataFrame(core_dict)
raw = pd.DataFrame(raw_dict)
indian = pd.DataFrame(indian_dict)

merge_df = pd.concat([core, raw, indian], ignore_index=True)

# Set up the Streamlit app
st.title('Food Recommender System')

selected_food = st.text_input('Enter a food recipe:')

selected_food_lower = selected_food.lower()

if selected_food_lower:
    # Get recommendations, image URLs, and user-entered food image URL
    recommendations, image_urls, user_food_image_url = recommend_food(selected_food_lower)
    if recommendations:
        # Display user-entered food name and its image
        st.write(f"You entered: {selected_food_lower}")
        st.image(user_food_image_url, caption=selected_food_lower, width=250)  # Adjust width as needed
        
        # Display recommendations with images in two columns
        col1, col2 = st.columns(2)  # Create two columns
        
        # Display images in the first column
        with col1:
            for recommendation, image_url in zip(recommendations[:3], image_urls[:3]):  # Display first 3 recommendations
                st.image(image_url, caption=recommendation, width=250)  # Adjust width as needed
        
        # Display images in the second column
        with col2:
            for recommendation, image_url in zip(recommendations[3:], image_urls[3:]):  # Display remaining recommendations
                st.image(image_url, caption=recommendation, width=250)  # Adjust width as needed
    else:
        st.write("Sorry, no recommendations found for that food item.")

else:
    st.write("Please enter a food recipe.")
