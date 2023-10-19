######### Airbnb Data Analysis Capstone Project
######### Developed by Geetha Sukumar
######### Date: 29/08/2023

import re
import pymongo
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import plotly.express as px
import folium



class airbnb_data:
    def __init__(self):
        
        self.MONGODB_CLIENT="mongodb+srv://gkg:1234@cluster0.eeit1pl.mongodb.net/?retryWrites=true&w=majority"
        
 ## DB connection definition
    def mongo_db_connect(self):
        collections=''
    
        try:
            client=pymongo.MongoClient(self.MONGODB_CLIENT)
            db = client.sample_airbnb
            self.collections=db.listingsAndReviews
            st.write("Successfully connected to DB - Airbnb Data")
            st.write(collections)
        except:
            st.write("Error: Function mongo_db_connect - connected to DB - Airbnb Data failed!")



### get data from mongo db            
    def get_airbnb_data(self):
        self.mongo_db_connect()
        cursor = self.collections.find({})
        list_cur = list(cursor)

        self.airbnb_df = pd.DataFrame(list_cur)    
        
        
### prepare the data
    def prep_airbnb_data(self):

        required_features = ['listing_url','name', 'price', 'bathrooms', 'access', 'property_type', 'room_type', 'room_type','accommodates','bedrooms','weekly_price', 'reviews_per_month']
        self.airbnb_selected_df = pd.concat([self.airbnb_df[self.airbnb_df.columns.intersection(required_features)], pd.json_normalize(self.airbnb_df['address'])], axis=1)
        coordinates = pd.DataFrame(self.airbnb_selected_df['location.coordinates'].to_list(), columns=['latitude','longitude'])
        self.airbnb_selected_df = pd.concat([self.airbnb_selected_df,coordinates ], axis=1)
        self.airbnb_selected_df.drop(['location.coordinates'], axis=1)
        self.airbnb_selected_df = pd.concat([self.airbnb_selected_df, pd.json_normalize(self.airbnb_df['availability'])], axis=1)
        self.airbnb_selected_df = pd.concat([self.airbnb_selected_df, pd.json_normalize(self.airbnb_df['review_scores'])], axis=1)
       
        
       
       
        
        # using dictionary to convert specific columns
        convert_to_str_dict = {'price': str,
                        'bedrooms' : str,
                        'weekly_price' : str,
                        'bathrooms': str,
                        }
      
        
        convert_to_float_dict = {'price': float,
                        'bedrooms' : float,
                        'weekly_price' : float,
                        'bathrooms': float,
                        }
                        
       
        
        self.airbnb_selected_df = self.airbnb_selected_df.astype(convert_to_str_dict)
        self.airbnb_selected_df = self.airbnb_selected_df.astype(convert_to_float_dict)
        
        # fill the nan with 0

        self.airbnb_selected_df.fillna({'reviews_per_month':0}, inplace=True)

       
        self.airbnb_selected_df.dropna(subset = ['bedrooms','bathrooms', 'weekly_price'], inplace=True)
      
        
        self.airbnb_selected_df = self.airbnb_selected_df.fillna(0)

        
        
        
        
        
        
        
    
########### Main program Starts ###########            

def main():
    st.title ("Airbnb Data Analysis")
    st.markdown("By Geetha Sukumar")
    m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {
                        background-color: #42c2f5;
                        color:#ffffff;
                    }


                    </style>""", unsafe_allow_html=True)
                    
    if "dc" not in st.session_state:
        st.session_state.dc = None
        st.session_state.collections = None
            
        ### Instantiate object
    
        dc = airbnb_data()
        st.session_state.dc = dc
      
        ## Get the data from the mongodb
        dc.get_airbnb_data()
        st.write(dc.airbnb_df.columns)
 
    
    if st.sidebar.button("Prepare Data"):
        if "dc" in st.session_state:
            dc = st.session_state.dc
            
    
   
            with st.spinner():
                dc.prep_airbnb_data()
                #st.write(dc.airbnb_selected_df.columns)
                st.table(dc.airbnb_selected_df.head())
                
                 
                # Group data by property type and calculate average price
                price_by_property_type = dc.airbnb_selected_df.groupby("property_type")["price"].mean().reset_index()

                # Create a bar chart
                st.bar_chart(price_by_property_type.set_index("property_type"))     
               
         
                #sns.countplot(dc.airbnb_selected_df['room_type'], palette="plasma")
                #fig = plt.gcf()
                #fig.set_size_inches(10,10)
                #plt.title('room_type')
                
        else:
             st.write("Get the Airbnb Data from DB to Prepare!")

    if st.sidebar.button("Visualise"):
        if "dc" in st.session_state:
            dc = st.session_state.dc
            
            
            st.table(dc.airbnb_selected_df.head())
            
            # Group data by property type and calculate average price
            price_by_property_type = dc.airbnb_selected_df.groupby("property_type")["price"].mean().reset_index()

            # Create a bar chart
            st.bar_chart(price_by_property_type.set_index("property_type"))     
           
           
           
           
           
            # Group data by season and calculate occupancy rate
            #dc.airbnb_selected_df.groupby("property_type")[["season"] = pd.to_datetime(df["date"]).dt.strftime("%B")
            #occupancy_rate = df.groupby("season")["availability"].mean().reset_index()

            # Create a line chart
            #fig = px.line(occupancy_rate, x="season", y="availability", title="Occupancy Rate by Season")
            #st.plotly_chart(fig)
           
            
            
            
            
            m = folium.Map(location=[latitude, longitude], zoom_start=10)

            # Add markers for Airbnb listings
            for index, row in dc.airbnb_selected_df.iterrows():
                folium.Marker([row["latitude"], row["longitude"]], tooltip=row["name"]).add_to(m)

            # Display the map
            st.write(m)
            
            
            
            
            
            
            availability_threshold = 50
            filtered_data = df[df['availability'] >= availability_threshold]

            # Create a Folium map centered on a specific location (you can adjust the coordinates)
            m = folium.Map(location=[filtered_data['latitude'].mean(), filtered_data['longitude'].mean()], zoom_start=12)

            # Add markers for Airbnb listings
            for index, row in filtered_data.iterrows():
                popup_text = f"Name: {row['name']}<br>Availability: {row['availability']}%"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='blue')
                ).add_to(m)

            # Display the map in the Streamlit app
            st.write(m)
                        
            
            
            
            
                        
        else:
             st.write("Prepare the Airbnb Data from DB to Visualise!")



                
main()
   