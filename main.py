import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import pandas as pd
import plotly.express as px
import json
import mysql.connector
import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import time
# Multi page initialization
import home,state_data,transaction_data,user_data,visual_data

st.set_page_config(page_title='Phonepe pulse Data Visualization')
# Initialize a class
class Multiapp:
    def __init__(self):
        self.apps = []
    def add_app(self,title,function):
        self.apps.append({
            "title":title,
            "function":function
        })

    def run():
# Inputs for Side bar option 
        with st.sidebar:
            app = option_menu(
            menu_title='Visualization',
            options=["Home","Transaction","User","State wise Growth","Data Visualization"],
            menu_icon='cast',
            icons=['house','credit-card','person','bar-chart','bar-chart'],
            default_index=1
    )
            
# Function call for use other pages
        if app=='Home':
            home.app()
        elif app=='Transaction':
            transaction_data.app()
        elif app=='User':
            user_data.app()
        elif app=='State wise Growth':
            state_data.app()
        elif app=='Data Visualization':
            visual_data.app()

    run()
    # Introduction about PHonepe
def app():
    st.title(":blue[Phonepe Pulse Data Visualization]")
    st.subheader(":orange[PhonePe: A Leading Digital Wallet in India]")
    st.write("Introducing PhonePe, a safe and user-friendly digital wallet that allows quick money transfers in multiple languages.")
    st.write(":orange[Key Benefits of PhonePe]")
    st.write("1. **Safe and Secure:** PhonePe follows industry-standard security measures to protect your transactions.")
    st.write("2. **Easy to Use:** The app is designed to be user-friendly and requires minimal time to get accustomed to.")
    st.write("3. **Multi-language Support:** PhonePe is available in multiple local Indian languages for a more personalized experience.")
    st.write("4. **24/7 Availability:** Transfer money anytime, anywhere, without any hassle.")

    st.write(":orange[Active Users Over Time]")
    users_over_time = [1000, 2500, 5000, 10000, 20000, 35000, 50000]  # Replace this with actual data
    st.bar_chart(users_over_time)
    st.write(":orange[Most Popular Languages]")
    popular_languages = ['Hindi', 'English', 'Tamil', 'Telugu', 'Marathi']  # Replace this with actual data
    st.bar_chart(popular_languages)
  # Databse Connection
mydb = mysql.connector.connect(host="localhost",user="root",password="")

print(mydb)
mycursor = mydb.cursor(buffered=True)

def app():


    # Create a function to create the line plot
    def load_data(state):
        query = "SELECT State, Year, SUM(Transaction_count) AS Transaction_Count FROM phonepe_data.aggregate_trans \
                WHERE State=%s \
                GROUP BY Year"
        mycursor.execute(query, (state,))
        out = mycursor.fetchall()
        mydb.commit()
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        return df

    # Create a function to create the line plot
    def create_line_plot(df):
        trace = go.Scatter(
            x=df['Year'],
            y=df['Transaction_Count'],
            mode='lines',
            name=df['State'].values[0]
        )

        layout = go.Layout(
            title='Transaction Count by Year for ' + df['State'].values[0],
            xaxis=dict(title='Year'),
            yaxis=dict(title='Transaction Count')
        )

        fig = go.Figure(data=[trace], layout=layout)

        return fig

    # Create a Streamlit app
    st.title(":green[Transaction Count by Year for Each State]")
    st.write(":red[Select the state to display the transaction count by year:]")

    states = ['Andaman & Nicobar','Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Lakshadweep', 'Puducherry']

    state_selected = st.selectbox(":blue[Select the state:]", states)

    df = load_data(state_selected)
    fig = create_line_plot(df)

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    import streamlit as st


# Database connection
mydb = mysql.connector.connect(host="localhost",user="root",password="")

print(mydb)
mycursor = mydb.cursor(buffered=True)

def app():

    # Load the geojson data
    with open("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")as f:
        india_states_geojson = json.load(f)

    # Create a function to load the data
    def load_data(year, quarter):
        query = "SELECT State, SUM(Transaction_amount) AS transaction_amount FROM phonepe_data.aggregate_trans \
                WHERE Year = %s and Quarter = %s \
                GROUP BY State"
        mycursor.execute(query, (year, quarter))
        out = mycursor.fetchall()
        mydb.commit()
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])
        
        return df

    # Create a function to create the choropleth map
    def create_choropleth_map(df, year, quarter):
        df_geo = pd.json_normalize(india_states_geojson['features']).rename(columns={'properties.ST_NM': 'State'})
        df1 = pd.merge(df, df_geo, on='State')
        fig = px.choropleth_mapbox(df1, geojson=india_states_geojson, 
                                locations='State', 
                                featureidkey='properties.ST_NM',
                                color='transaction_amount', 
                                color_continuous_scale='Viridis', 
                                range_color=(df1['transaction_amount'].min(), df1['transaction_amount'].max()),
                                mapbox_style='carto-positron', 
                                zoom=4, center={'lat': 22, 'lon': 82})
        fig.update_layout(title=f'Total Transaction Amount by State Year-{year}/Q{quarter}', 
                        title_x=0.5, 
                        margin={'r': 20, 't': 30, 'l': 20, 'b': 20})
        return fig

    # Create a Streamlit app
    st.title(":red[Choropleth Map of Transaction Amount by State]")
    st.write(":green[Select the year and quarter to display the choropleth map:]")

    years = ["Select the Year",2018, 2019, 2020, 2021, 2022, 2023]
    quarters = ["Select the Quarter",1, 2, 3, 4]
    
    year_selected = st.selectbox(":blue[Select the year:]", years)
    quarter_selected = st.selectbox(":blue[Select the quarter:]", quarters)

    df = load_data(year_selected, quarter_selected)
    fig = create_choropleth_map(df, year_selected, quarter_selected)

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
   

# Database Connection

mydb = mysql.connector.connect(host="localhost",user="root",password="")
print(mydb)
mycursor = mydb.cursor(buffered=True)

def app():
    
    # Create a function to load the data

    def load_data(year, quarter):
        query = "SELECT State, SUM(Total_count) AS total_count FROM phonepe_data.aggregate_user \
                WHERE Year = %s \
                GROUP BY State"
        mycursor.execute(query, (year,))
        out = mycursor.fetchall()
        mydb.commit()
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])
        return df

    # Create a function to create the choropleth map

    def create_choropleth_map(df, year, quarter):
        df_geo = pd.json_normalize(india_states_geojson['features']).rename(columns={'properties.ST_NM': 'State'})
        df1 = pd.merge(df, df_geo, on='State')
        fig = px.choropleth_mapbox(df1, geojson=india_states_geojson, 
                                locations='State', 
                                featureidkey='properties.ST_NM',
                                color='total_count', 
                                color_continuous_scale='Viridis', 
                                range_color=(df1['total_count'].min(), df1['total_count'].max()),
                                mapbox_style='carto-positron', 
                                zoom=4, center={'lat': 22, 'lon': 82})
        fig.update_layout(title=f'Total Transaction User Count by State Year-{year}/Q{quarter}', 
                        title_x=0.5, 
                        margin={'r': 20, 't': 30, 'l': 20, 'b': 20})
        return fig

    # Load the geojson data
    with open("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")as f:
        india_states_geojson = json.load(f)

    # Create a Streamlit app
    st.title(":green[Choropleth Map of Total Transaction User Count by State]")
    st.write(":red[Select the year and quarter to display the choropleth map:]")

    years = ["Select the Year",2018, 2019, 2020, 2021, 2022]
    quarters = ["Select the Quater",1, 2, 3, 4]

    year_selected = st.selectbox(":blue[Select the year:]", years)
    quarter_selected = st.selectbox(":blue[Select the quarter:]", quarters)

    df = load_data(year_selected, quarter_selected)
    fig = create_choropleth_map(df, year_selected, quarter_selected)

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
    import streamlit as st


# Database Connection
mydb = mysql.connector.connect(host="localhost",user="root",password="")
print(mydb)
mycursor = mydb.cursor(buffered=True)

def app():
    st.title(":blue[Data Visualization]")
    st.write(":green[Insights]")

    # Query from various insights which get from data

    query_select = st.selectbox(":violet[Select Your Query]",("Select the Query","Top 10 States with Highest Total count 2023",
                                "Top 10 Register users In 2023","State wise Transaction Amount",
                                "Satae wise Transaction count distribution",
                                "Transaction type count over the Years",
                                "State wise Transaction count over Years",
                                "Percentage of Users Brand wise",
                                "State wise Register User",
                                "State wise App opened Data"))
    
    if query_select=="Select the Query:":
        st.write("  ")

    elif query_select=="Top 10 States with Highest Total count 2023":
        st.write(":orange[Top 10 States with Highest Total count 2023]")
        # Execute the SQL query
        mycursor.execute("SELECT State,Pincode,SUM(Total_count) AS Total_Count FROM phonepe_data.top_trans \
                        Where Year=2023\
                        GROUP BY State \
                        ORDER BY Total_Count DESC LIMIT 10")

        # Fetch the results
        states = []
        total_counts = []
        for row in mycursor.fetchall():
            states.append(row[0])
            total_counts.append(row[2])

        # Create a bar chart
        fig, ax = plt.subplots(figsize=(15,6))
        ax.bar(states, total_counts)
        ax.set_xlabel('State')
        ax.set_ylabel('Total Count')
        ax.set_title('Top 10 States with Highest Total Count 2023')

        # Display the chart in Streamlit
        st.pyplot(fig)



    elif query_select=="Top 10 Register users In 2023":
        st.write(":orange[Top 10 Register users In 2023]")
        # Execute the SQL query
        mycursor.execute("SELECT State,Pincode,SUM(Register_user) AS Register_User FROM phonepe_data.top_user \
                        Where Year=2023\
                        GROUP BY State \
                        ORDER BY Register_User DESC LIMIT 10")

        # Fetch the results
        states = []
        register_users = []
        for row in mycursor.fetchall():
            states.append(row[0])
            register_users.append(row[2])

        # Create a bar chart
        fig, ax = plt.subplots(figsize=(15,6))
        ax.bar(states, register_users)
        ax.set_xlabel('State')
        ax.set_ylabel('Register Users')
        ax.set_title('Top 10 States with Highest Register Users 2023')

        # Display the chart in Streamlit
        st.pyplot(fig)


    elif query_select=="State wise Transaction Amount":
        st.write(":orange[State wise Transaction Amount]")
        # Execute the SQL query
        mycursor.execute("SELECT State,Year,Transaction_amount FROM phonepe_data.aggregate_trans\
                        where year between 2018 and 2023\
                        Group by State")

        # Fetch the results
        out = mycursor.fetchall()

        # Close the database connection
        mydb.commit()

        # Convert fetched data to DataFrame
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        # Create a bar chart using Plotly
        fig = px.bar(df, x=df.State, y=df.Transaction_amount, color=df.State,title='State wise transaction amount in Billions for year 2018',height=750)

        # Display the chart in Streamlit
        st.plotly_chart(fig)


    elif query_select== "Satae wise Transaction count distribution":
        st.write(":orange[Satae wise Transaction count distribution]")
        # Execute the SQL query
        mycursor.execute("SELECT State,Year,Transaction_type,SUM(Transaction_count) Transaction_count FROM phonepe_data.aggregate_trans \
                        Group by State,Transaction_type")

        # Fetch the results
        out = mycursor.fetchall()

        # Close the database connection
        mydb.commit()

        # Convert fetched data to DataFrame
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        # Create a bar chart using Plotly
        fig = px.bar(df, x=df.State, y=df.Transaction_count, color=df.Transaction_type,title='State wise transaction count distribution',height=750)

        # Display the chart in Streamlit
        st.plotly_chart(fig)


    elif query_select== "Transaction type count over the Years":
        st.write(":orange[Transaction type count over the Years]")
        # Execute the SQL query
        mycursor.execute("SELECT Year,Transaction_type,SUM(Transaction_count) Transaction_count FROM phonepe_data.aggregate_trans \
                        Group by Year,Transaction_type")

        # Fetch the results
        out = mycursor.fetchall()

        # Close the database connection
        mydb.commit()

        # Convert fetched data to DataFrame
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        # Create a bar chart using Plotly
        fig = px.bar(df, x=df.Transaction_type, y=df.Transaction_count, color=df.Year,title='Transaction type count over the years',height=750)

        # Display the chart in Streamlit
        st.plotly_chart(fig)


    elif query_select=="Percentage of Users Brand wise":
        st.write(":orange[Percentage of Users Brand wise]")
        # Execute the SQL query
        mycursor.execute("SELECT State,Year,sum(Percentage) as Percentage,Brand FROM phonepe_data.aggregate_user\
                        GROUP BY State,Brand")

        # Fetch the results
        out = mycursor.fetchall()

        # Close the database connection
        mydb.commit()

        # Convert fetched data to DataFrame
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        # Create a pie chart using Plotly
        fig = px.pie(df, values='Percentage', names='Brand',color_discrete_sequence=px.colors.sequential.RdBu,title='Percentage of User Brand wise')
        fig.update_traces(textposition='inside', textinfo='percent+label')

        # Display the chart in Streamlit
        st.plotly_chart(fig)


    elif query_select=="State wise Register User":
        st.write(":orange[State wise Register User]")
        # Execute the SQL query
        mycursor.execute("SELECT State,SUM(Register_user) as Registeruser FROM phonepe_data.map_user \
                        Group BY State ")

        # Fetch the results
        out = mycursor.fetchall()

        # Close the database connection
        mydb.commit()

        # Convert fetched data to DataFrame
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        # Create a pie chart using Plotly
        fig = px.pie(df, values='Registeruser', names='State',title='State wise Register User')
        fig.update_traces(textposition='inside', textinfo='percent+label')

        # Display the chart in Streamlit
        st.plotly_chart(fig)


    elif query_select=="State wise App opened Data":
        st.write(":orange[State wise App opened Data]")
        # Execute the SQL query
        mycursor.execute("SELECT State,SUM(Register_user) as Registeruser,SUM(App_opened) as App_open FROM phonepe_data.map_user \
                        where year=2023 \
                        Group BY State")

        # Fetch the results
        out = mycursor.fetchall()

        # Close the database connection
        mydb.commit()

        # Convert fetched data to DataFrame
        df = pd.DataFrame(out, columns=[i[0] for i in mycursor.description])

        # Create a pie chart using Plotly
        fig = px.pie(df, values='App_open', names='State',title='State wise App opened Data')
        fig.update_traces(textposition='inside', textinfo='percent+label')

        # Display the chart in Streamlit
        st.plotly_chart(fig)
    
   