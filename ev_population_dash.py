import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Read the data from the CSV file
df = pd.read_csv('ev_population_cleaned.csv')

# Calculate the average electric range by make and model
avg_range_df = df.groupby(['Make'])['Electric_Range'].mean().reset_index()

#Calculate the market share of top 10 makes
top_10_makes = df['Make'].value_counts().nlargest(10)
avg_range_top_10_makes = avg_range_df[avg_range_df['Make'].isin(top_10_makes.index)]

# Calculate the number of vehicle registrations per year
registrations_per_year = df['Model_Year'].value_counts().sort_index().reset_index()
registrations_per_year.columns = ['Model_Year', 'Registration_Count']

# Calculate the top 10 bestselling models
top_10_models = df['Model'].value_counts().nlargest(10)

# Calculate the market share of top 10 makes
top_10_makes = df['Make'].value_counts().nlargest(10)

# Calculate the remaining makes and models
remaining_models = df['Model'].value_counts().nsmallest(len(df['Model'].unique()) - 10).sum()
remaining_makes = df['Make'].value_counts().nsmallest(len(df['Make'].unique()) - 10).sum()

# Calculate the number of distinct model launches by the top 10 makes
model_launches = df[df['Make'].isin(top_10_makes.index)].groupby('Make')['Model'].nunique()

# Filter the dataframe to include only the top 10 makes
df_top_10_makes = df[df['Make'].isin(top_10_makes.index)]


# Extract latitude and longitude values from "Vehicle Location" column
df['Coordinates'] = df['Vehicle Location'].str.replace('POINT ', '').str.replace('(', '').str.replace(')', '').str.split()

# Replace invalid values with NaN
df['Coordinates'] = df['Coordinates'].apply(lambda x: [float(c) if c != 'Unknown' else None for c in x])

# Split the coordinates into latitude and longitude columns
df[['Longitude', 'Latitude']] = pd.DataFrame(df['Coordinates'].tolist(), index=df.index)

# Create a filtered dataframe with Clean_Alternative_Fuel_Vehicle_Eligibility = 'yes'
eligible_df = df[df['Clean_Alternative_Fuel_Vehicle_Eligibility'] == 'Yes']

# Calculate the number of eligible models per year
eligibility_per_year = eligible_df.groupby('Model_Year')['Clean_Alternative_Fuel_Vehicle_Eligibility'].count().reset_index()
eligibility_per_year.columns = ['Model_Year', 'Eligible_Model_Count']

# Filter the data for the top 10 makes and distinct electric vehicle types
top_10_makes_data = df[df['Make'].isin(top_10_makes.index)]
top_10_makes_ev_types = top_10_makes_data['Electric_Vehicle_Type'].value_counts()




# Calculate the total number of registrations
total_registrations = len(df)

# Calculate the growth in number of registrations from 2010 to 2022
registrations_2010 = df[df['Model_Year'] == 2010].shape[0]
registrations_2022 = df[df['Model_Year'] == 2022].shape[0]
growth_percent = (registrations_2022 - registrations_2010) / registrations_2010 * 100
growth_percent = f"{growth_percent:.2f}%"  # Format the value with 2 decimal places and add a percent sign

# Calculate the highest selling make and model
highest_selling_make = df['Make'].value_counts().idxmax()
highest_selling_model = df['Model'].value_counts().idxmax()

# Calculate the average electric range
average_range = df['Electric_Range'].mean()

# Calculate the percentage of electric vehicle types
ev_type_percentages = df['Electric_Vehicle_Type'].value_counts(normalize=True) * 100


# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(
    [
        html.H1(
            'Exploring Electric Vehicle Trends in The US',
            style={
                'font-family': 'Arial',
                'font-size': '40px',
                'text-align': 'center'
            }
        ),
    # Table Showing Key Performing Index
    dash_table.DataTable(
        data=[
            {'KPI': 'Total number of registrations', 'Value': total_registrations},
            {'KPI': 'Percent growth in number of electric vehicle from 2010 to 2022', 'Value': growth_percent},
            {'KPI': 'Electric Vehicle Manufacturer with maximum maket share', 'Value': highest_selling_make},
            {'KPI': 'Best selling model ', 'Value': highest_selling_model},
            {'KPI': 'Average electric range', 'Value': average_range},
            {'KPI': 'Percentage distribution of electric vehicle type', 'Value': '\n'.join(f"{k}: {v:.2f}%" for k, v in ev_type_percentages.items())}
        ],
        columns=[{'name': 'KPI', 'id': 'KPI'}, {'name': 'Value', 'id': 'Value'}],
        style_table={'border': '1px solid black'},
        style_cell={
            'padding': '8px',
            'textAlign': 'left',
            'fontSize': '16px'
        },
        style_header={'fontWeight': 'bold'},
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }]
    ),

 #  Line chart showing number of registration 
    dcc.Graph(
    id='registration-line',
    figure=go.Figure(
        data=[
            go.Scatter(
                x=registrations_per_year['Model_Year'],
                y=registrations_per_year['Registration_Count'],
                mode='lines',
                line=dict(color='navy')
            )
        ],
        layout=go.Layout(
            title={
                'text': 'Number of Vehicle Registrations per Year',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis=dict(title='Model Year'),
            yaxis=dict(title='Registration Count')
        )
    )
    ),
# map showing density of ev's in a particular area
     dcc.Graph(
        id='density-map',
        figure=go.Figure(
            data=go.Densitymapbox(
                lat=df['Latitude'],
                lon=df['Longitude'],
                z=df['Base_MSRP'],
                radius=10,
                colorscale='Blues',  # Update the colorscale to 'Reds'
                opacity=0.7
            ),
            layout=go.Layout(
                title={
                'text': 'Vehicle Location Density',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },           
                mapbox_style='open-street-map',
                mapbox_zoom=3,
                mapbox_center=dict(lat=42, lon=-100),
                
            )
        )
    ),

 # pie chart showing top 10 makes
    dcc.Graph(
    id='top-10-makes-pie',
    figure=go.Figure(
        data=[
            go.Pie(
                labels=top_10_makes.index,
                values=top_10_makes.values,
                marker=dict(
                    colors=['#FF6384', '#36A2EB', '#FFCE56', '#FF9933', '#66CC99', '#FF66CC', '#3366CC', '#FFCC00', '#9933FF', '#00CCCC', '#FF3333', '#33CC33']
                )
            )
        ],
        layout=go.Layout(title={
                'text': 'Top 10 Electric Vehicle Maufacturers',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}})
    )
    ),

# donut chart showing top 10 bestselling model
    dcc.Graph(
    id='top-10-models-donut',
    figure=go.Figure(
        data=[go.Pie(labels=top_10_models.index, values=top_10_models.values, hole=0.5)],
        layout=go.Layout(title={
                'text': 'Top 10 Bestselling Models',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}})
    )
    ),    

   # Horizontal ba graph showing number of model launches by top 10 makes
    dcc.Graph(
    id='model-launches-bar',
    figure=px.bar(
        x=model_launches.values,
        y=model_launches.index,
        orientation='h',
        title='Number of Model Launches by Top 10 Makes',
        color_discrete_sequence=['violet'] * len(model_launches)  # Set the color to violet for all bars
    ).update_layout(
        title={'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top'},
        xaxis={'title': 'Number of Electric Cars'},
        yaxis={'title': 'Top 10 Electric Car Manufacturers'}
    )
    ),
    
  # area chart showing number f vehicles eligible for clean alternative energy fuel
    dcc.Graph(
    id='eligible-models-area-chart',
    figure=go.Figure(
        data=go.Scatter(
            x=eligibility_per_year['Model_Year'],
            y=eligibility_per_year['Eligible_Model_Count'],
            mode='lines',
            fill='tozeroy'
        ),
        layout=go.Layout(
            title='Number of Clean Alternative Fuel Vehicle Eligible Models by Model Year',
            xaxis=dict(title='Model Year'),
            yaxis=dict(title='Number of Eligible Models')
        )
    ).update_layout(title={'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top'})
    ),    

 #  bar graph showing average range of top 10 makes 
    dcc.Graph(
    id='avg-range-bar',
    figure=go.Figure(
        data=[
            go.Bar(
                x=avg_range_top_10_makes['Make'],
                y=avg_range_top_10_makes['Electric_Range'],
                text=avg_range_top_10_makes['Electric_Range'],
                textposition='auto',
                marker=dict(color='green')
            )
        ],
        layout=go.Layout(
            title=dict(text='Average Electric Range of Top 10 Makes', x=0.5),
            xaxis=dict(title='Make'),
            yaxis=dict(title='Average Electric Range')
        )
    )
    ),

# scatter plot showing Electric Range by Electric Vehicle Type
    dcc.Graph(
    id='scatter-plot',
    figure=px.scatter(
        df,
        y='Electric_Range',
        x='Electric_Vehicle_Type',
        color='Electric_Vehicle_Type',
        hover_data=['Make', 'Model'],
        title='Electric Range by Electric Vehicle Type',
        labels={'Electric_Range': 'Electric Range', 'Electric_Vehicle_Type': 'Electric Vehicle Type'}
    ).update_layout(title={'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top'})
    ),

#  bubble chart showing Electric Range vs Base MSRP by Make 
    dcc.Graph(
    id='electric-range-vs-msrp-bubble',
    figure=px.scatter(df, x='Electric_Range', y='Base_MSRP', size='Model_Year', color='Make',
                      hover_data=['County', 'City', 'State', 'Model', 'Electric_Vehicle_Type'],
                      title='Electric Range vs Base MSRP by Make ',
                      labels={'Electric_Range': 'Electric Range', 'Base_MSRP': 'Base MSRP'},
                      ).update_layout(title={'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top'})
)

        
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
