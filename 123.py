import pandas as pd
import streamlit as st 
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt



# Load the data from CSV files
order_data = pd.read_csv(orders_cleaned.csv)
assoc_rules = pd.read_csv(association_rules_results.csv)

# Title of the dashboard
st.title('Insightful Dashboard')

# Columns layout for displaying data
left_column, right_column = st.columns((2))

# Sidebar for filtering options
st.sidebar.title("Filter Options")

# Tabs for displaying different data sections
orders_tab, rules_tab = st.tabs(['Order Information', 'Market Basket Analysis'])

# Define the content for the 'Order Information' tab
with orders_tab:
    st.header("Orders Overview")
    st.write(order_data)

    # Convert the 'Order Date' column to datetime format
    order_data['Order Date'] = pd.to_datetime(order_data['Order Date'])

    # Get the min and max date for the date picker
    min_date = order_data['Order Date'].min()
    max_date = order_data['Order Date'].max()

    # Date range picker
    start_date = pd.to_datetime(st.sidebar.date_input('Start Date', min_date))
    end_date = pd.to_datetime(st.sidebar.date_input('End Date', max_date))

    # Filter the orders data based on the selected date range
    filtered_orders = order_data[(order_data['Order Date'] >= start_date) & (order_data['Order Date'] <= end_date)].copy()

    # Select market and category filters
    selected_market = st.sidebar.selectbox('Market', filtered_orders['Market'].unique())
    selected_categories = st.sidebar.multiselect('Category', filtered_orders['Category'].unique())

    # Apply filters to the orders data
    if selected_market and selected_categories:
        final_filtered_orders = filtered_orders[(filtered_orders['Market'] == selected_market) & (filtered_orders['Category'].isin(selected_categories))]
    elif selected_market:
        final_filtered_orders = filtered_orders[filtered_orders['Market'] == selected_market]
    elif selected_categories:
        sub_categories = filtered_orders[filtered_orders['Category'].isin(selected_categories)]['Sub-Category'].unique().tolist()
        final_filtered_orders = filtered_orders[(filtered_orders['Category'].isin(selected_categories)) | (filtered_orders['Sub-Category'].isin(sub_categories))]
    else:
        final_filtered_orders = filtered_orders.copy()

    # Visualization of sales by sub-category
    st.subheader('Sub-Category Sales')
    sub_category_sales = final_filtered_orders.groupby('Sub-Category', as_index=False)['Sales'].sum()
    fig1 = px.bar(sub_category_sales, x='Sub-Category', y='Sales', height=600, width=700)
    st.plotly_chart(fig1)

    # Visualization of sales by ship mode
    st.subheader('Sales by Shipping Method')
    fig2 = px.box(final_filtered_orders, x='Ship Mode', y='Sales', height=400, width=600)
    st.plotly_chart(fig2)

    # Visualization of profit by market
    st.subheader('Market Profit')
    market_profit = final_filtered_orders.groupby('Market', as_index=False)['Profit'].sum()
    fig3 = px.bar(market_profit, x='Market', y='Profit')
    st.plotly_chart(fig3)

    # Scatter plot to show relationship between quantity and profit
    scatter = px.scatter(order_data, x='Quantity', y='Profit', size='Sales')
    scatter['layout'].update(title="Relationship between Quantity and Profit",
                             titlefont=dict(size=20),
                             xaxis=dict(title="Quantity", titlefont=dict(size=19)),
                             yaxis=dict(title="Profit", titlefont=dict(size=19)))
    st.plotly_chart(scatter, use_container_width=True)

    # Line chart to show sales over time
    final_filtered_orders["MonthYear"] = final_filtered_orders["Order Date"].dt.to_period("M")
    st.subheader('Sales Over Time')
    monthly_sales = final_filtered_orders.groupby(final_filtered_orders["MonthYear"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index()
    monthly_sales = monthly_sales.sort_values(by="MonthYear")
    fig4 = px.bar(monthly_sales, x="MonthYear", y="Sales", height=500, width=1500, labels={"Sales": "Amount"}, template="gridon")
    st.plotly_chart(fig4, use_container_width=True)

    # Pie chart to display sales distribution by segment
    st.subheader('Sales Distribution by Segment')
    fig5 = px.pie(final_filtered_orders, values="Sales", names='Segment')
    st.plotly_chart(fig5)

# Define the content for the 'Market Basket Analysis' tab
with rules_tab:
    st.header("Market Basket Analysis - Association Rules")
    st.write(assoc_rules)

    # Heatmap visualization
    st.subheader("Heat Map of Association Rules")
    pivot_data = assoc_rules.pivot_table(index='antecedents', columns='consequents', values='lift')
    heatmap_fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_data, ax=ax, annot=True, cmap="viridis")
    st.pyplot(heatmap_fig)

    # Bar charts for top antecedents and consequents based on support
    bar_chart1, bar_chart2 = st.columns((2))
    with bar_chart1:
        top_antecedents_fig = px.bar(assoc_rules, x='support', y='antecedents', orientation='h', title='Top Antecedents by Support')
        st.plotly_chart(top_antecedents_fig, use_container_width=True)
    with bar_chart2:
        top_consequents_fig = px.bar(assoc_rules, x='support', y='consequents', orientation='h', title='Top Consequents by Support')
        st.plotly_chart(top_consequents_fig, use_container_width=True)

    # Pie charts for lift distribution of antecedents and consequents
    st.subheader('Lift Distribution of Antecedents')
    lift_antecedent_pie = px.pie(assoc_rules, values="lift", names='antecedents', template="gridon")
    lift_antecedent_pie.update_traces(text=assoc_rules["antecedents"])
    st.plotly_chart(lift_antecedent_pie, use_container_width=True)

    st.subheader('Lift Distribution of Consequents')
    lift_consequent_pie = px.pie(assoc_rules, values="lift", names='consequents', template="gridon")
    lift_consequent_pie.update_traces(text=assoc_rules["consequents"])
    st.plotly_chart(lift_consequent_pie, use_container_width=True)





