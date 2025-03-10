import streamlit as st
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

# Set the title of the app
st.title("Subtv Loyality and Referral Scheme Simulation")

st.header("Inputs")
num_customers = st.number_input("Number of Customers", min_value=1, value=1000, step=1)
profit_margin = st.number_input("Average Profit Margin (%)", min_value=0.0, value=2.0, step=0.1)
points_to_value_ratio = st.number_input('Points to Value Ration', min_value=0.001, value=0.001, step=0.001, format="%.3f")


# Create two columns
col1, col2 = st.columns(2)

# Add content to the first column
with col1:
    st.subheader("Customer Behaviours")
    average_purchases_per_customer = st.number_input("Average Purchases per Customer", min_value=1, value=3, step=1)
    average_order_value = st.number_input("Average Order Value (£)", min_value=1, value=30, step=1)
    percentage_claimed = st.number_input("Percentage of Bonus Claimed", min_value=1, value=50, step=1)

    st.subheader("Referrals")
    points_per_referral = st.number_input("Referral Points", min_value=1, value=1000, step=1)
    referree = st.checkbox("Bonus for both referrer and referee")
    
    st.subheader('Purchases')
    point_per_spend = st.number_input("Points Per £ Spend", min_value=1, value=2, step=1)

# Add content to the second column
with col2:
    st.subheader("Milestones")
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        milestone1 = st.number_input("Milestone One Orders", min_value=0, value=5, step=1)
        milestone2 = st.number_input("Milestone Two Orders", min_value=0, value=10, step=1)
        milestone3 = st.number_input("Milestone Three Orders", min_value=0, value=25, step=1)

    with col2_2:
        milestone1_value = st.number_input("Milestone One Value", min_value=0, value=1000, step=1)
        milestone2_value = st.number_input("Milestone Two Value", min_value=0, value=2000, step=1)
        milestone3_value = st.number_input("Milestone Three Value", min_value=0, value=5000, step=1)

    st.subheader('Requests')
    points_per_request = st.number_input('Points per Request', min_value=0, value=1, step=1)
    points_per_upvote = st.number_input('Points per Upvote', min_value=0, value=10, step=1)



# Button to run the simulation
if st.button("Run Simulation"):
    # Generate synthetic customer behavior

    purchases_per_customer = np.random.poisson(lam=average_purchases_per_customer, size=num_customers)
    order_values = np.random.normal(loc=average_order_value, scale=5, size=sum(purchases_per_customer))  # Order values with some variance
    order_values = np.maximum(order_values, 1)  # Ensure no negative order values
    profit_margin = profit_margin / 100
    percentage_claimed = percentage_claimed / 100
    requests_per_customer = np.random.lognormal(mean=2, sigma=1.2, size=num_customers).astype(int)
    # Introduce a 50% chance of being zero
    mask = np.random.choice([0, 1], size=num_customers, p=[0.5, 0.5])  # 50% chance for zero
    requests_per_customer = requests_per_customer * mask
    # request_points = number_requests * points_per_request

    number_upvotes = np.random.lognormal(mean=1, sigma=0.4, size=sum(requests_per_customer)).astype(int) - 1
    number_upvotes = np.maximum(number_upvotes, 0)
    mask = np.random.choice([0, 1], size=len(number_upvotes), p=[0.5, 0.5])  # 50% chance for zero
    number_upvotes = number_upvotes * mask
    # number_upvotes = round(requests_per_customer * number_upvotes)
    # upvote_points = number_upvotes * number_requests * points_per_upvote


    referral_flags = np.round(stats.invgauss.rvs(mu=3 / 2, scale=2, size=num_customers)).astype(int) - 7

    # Simulating the customer transactions
    customer_data = []

    for i in range(num_customers):
        num_purchases = purchases_per_customer[i]
        purchase_values = order_values[sum(purchases_per_customer[:i]):sum(purchases_per_customer[:i + 1])]

        # Calculate points from purchases
        purchase_points = np.sum(purchase_values) * point_per_spend

        num_requests = requests_per_customer[i]
        request_points = num_requests * points_per_request
        num_upvotes = np.sum(number_upvotes[sum(requests_per_customer[:i]):sum(requests_per_customer[:i+1])])
        upvote_points = num_upvotes * points_per_upvote
            

        # Check milestone points
        milestone_points = 0
        if num_purchases >= milestone1:
            milestone_points += milestone1_value
        if num_purchases >= milestone2:
            milestone_points += milestone2_value
        if num_purchases >= milestone3:
            milestone_points += milestone3_value

        # Referral points
        num_referrals = min(max(referral_flags[i], 0), 5)
        referral_points = num_referrals * points_per_referral
        if referree:
            referral_points = 2*referral_points


        # Total points
        total_points = purchase_points + milestone_points + referral_points + request_points + upvote_points

        # Store data
        customer_data.append([i + 1, num_purchases, np.sum(purchase_values), purchase_points, milestone_points, num_referrals, referral_points, num_requests, request_points, num_upvotes, upvote_points, total_points])

    # Convert to DataFrame
    df_customers = pd.DataFrame(customer_data, columns=[
        "Customer_ID", "Purchases", "Total_Spend", "Purchase_Points",
        "Milestone_Points", "Number_Referrals", "Referral_Points", "Number_Requests", "Request_Points", "Number_Upvotes", "Upvote_Points" ,"Total_Points"
    ])


    df_customers["Total_Points_Value"] = df_customers.Total_Points * points_to_value_ratio
    # Calculate profit per customer
    df_customers["Revenue"] = df_customers["Total_Spend"] * profit_margin 
    df_customers["Individual_Profit"] = df_customers["Revenue"] - df_customers["Total_Points_Value"]

    # Round values
    df_customers = df_customers.round(2)

    # Create tabs for output
    tab1, tab2, tab3 = st.tabs(["Summary", "Individual Profits","Distributions"])
    # Summary Tab
    with tab1:

    # Display the table
        st.write("### Customer Data & Profit Summary")
        st.dataframe(df_customers)

        # Show summary statistics
        st.write("### Summary Statistics")
        st.write(df_customers.describe())

        # Show total profit
        # total_profit = df_customers["Individual_Profit"].sum()
        # st.write(f"### **Total Estimated Profit: ${total_profit:,.2f}**")
        st.write(f'### Total Giveaway: {round(df_customers.Total_Points.sum())} Points or £{round(df_customers.Total_Points_Value.sum(), 2)}')
        st.write(f'### Claimed Giveaway: £{round(percentage_claimed * df_customers.Total_Points_Value.sum(), 2)}')
        st.write(f'### Revenue: £{round(df_customers.Revenue.sum(), 2)}')
        st.write(f'### Profit: £{round(df_customers.Revenue.sum() - percentage_claimed * df_customers.Total_Points_Value.sum(), 2)}')
        st.write(f'### Points reduced profit by: £{round((percentage_claimed * df_customers.Total_Points_Value.sum()), 2)} ({round(100*(percentage_claimed * df_customers.Total_Points_Value.sum()/df_customers.Revenue.sum()), 1)}%) to gain {df_customers.Number_Referrals.sum()} referrals (plus some extra retention).')

    # Distribution Tab
    with tab2:
        # Histogram of Individual Profit
        st.write("### Histogram of Individual Profit")
        fig, ax = plt.subplots()
        ax.hist(df_customers['Individual_Profit'], bins=30, edgecolor='black')
        ax.set_xlabel('Individual Profit')
        ax.set_ylabel('Frequency')
        ax.set_title('Histogram of Individual Profit')
        st.pyplot(fig)

        st.write('### Customers who we lose money on')
        st.dataframe(df_customers[df_customers.Individual_Profit < 0])
        st.write(df_customers[df_customers.Individual_Profit < 0].describe())


        st.write('### Bonus Split')

        total_Purchase_Points = df_customers.Purchase_Points.sum()
        total_Milestone_Points = df_customers.Milestone_Points.sum()
        total_Referral_Points = df_customers.Referral_Points.sum()
        total_Request_Points = df_customers.Request_Points.sum()
        total_Upvote_Points = df_customers.Upvote_Points.sum()
        total_Points_Giveaway = sum([total_Purchase_Points, total_Milestone_Points, total_Referral_Points, total_Request_Points, total_Upvote_Points])
        
        # Create a DataFrame for the points breakdown
        points_breakdown = pd.DataFrame({
            'Points From': ['Purchases', 'Milestones', 'Referrals', 'Requests', 'Upvotes'],
            'Points': [total_Purchase_Points, total_Milestone_Points, total_Referral_Points, total_Request_Points, total_Upvote_Points],
        })

        # Calculate the value and percentage of points giveaway
        points_breakdown['Value (£)'] = points_breakdown['Points'] * points_to_value_ratio
        points_breakdown['Percentage of Points Giveaway'] = (100 * points_breakdown['Points'] / total_Points_Giveaway).apply(lambda x: f"{x:.1f}%")

        # Display the DataFrame
        st.dataframe(points_breakdown.round(2))


    
    with tab3:
        # Average Purchases
        st.write("### Purchases")
        avg_purchases = round(df_customers.Purchases.mean(), 1)
        st.write(f"Average Purchases: **{avg_purchases}**")

        purchase_counts = df_customers.Purchases.value_counts().reset_index()
        purchase_counts.columns = ["Purchases", "Count"]
        purchase_counts = purchase_counts.sort_values("Purchases")

        fig, ax = plt.subplots()
        ax.bar(purchase_counts["Purchases"], purchase_counts["Count"])
        ax.set_title("Purchases Distribution")
        ax.set_xlabel("Purchases")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        # Order Value
        st.write("### Order Values")
        # Calculate and display the average order value
        avg_order_value_simulated = round(np.mean(order_values), 2)
        st.write(f"Average Order Value: **£{avg_order_value_simulated}**")

        # Plot the distribution of order values
        fig, ax = plt.subplots()
        ax.hist(order_values, bins=30, edgecolor='black')
        ax.set_xlabel("Order Value (£)")
        ax.set_ylabel("Frequency")
        ax.set_title("Distribution of Order Values")
        st.pyplot(fig)


        # Referrers Distribution
        st.write("### Referrals")
        zero_referrals_pct = round(100 * (len(df_customers[df_customers.Number_Referrals == 0]) / len(df_customers)), 1)
        st.write(f"Percentage of Users who make zero referrals: **{zero_referrals_pct}%**")


        referrers_count = df_customers[df_customers.Number_Referrals > 0]['Number_Referrals'].value_counts().reset_index()
        referrers_count.columns = ["Number_Referrals", "Count"]
        referrers_count = referrers_count.sort_values("Number_Referrals")

        fig, ax = plt.subplots()
        ax.bar(referrers_count["Number_Referrals"], referrers_count["Count"])
        ax.set_title("Referrers Distribution")
        ax.set_xlabel("Referrals")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        # Requests Distribution
        st.write("### Requests")
        zero_Requests_pct = round(100 * (len(df_customers[df_customers.Number_Requests == 0]) / len(df_customers)), 1)
        st.write(f"Percentage of Users who make zero requests: **{zero_Requests_pct}%**")


        referrers_count = df_customers[df_customers.Number_Requests != 0]['Number_Requests'].value_counts().reset_index()
        referrers_count.columns = ["Number_Requests", "Count"]
        referrers_count = referrers_count.sort_values("Number_Requests")

        fig, ax = plt.subplots()
        ax.bar(referrers_count["Number_Requests"], referrers_count["Count"])
        ax.set_title("Requests Distribution")
        ax.set_xlabel("Requests")
        ax.set_ylabel("Count")
        st.pyplot(fig)


        # UPVOTES Distribution
        st.write("### Upvotes")
        zero_Upvotes_pct = round(100 * (len(df_customers[df_customers.Number_Upvotes == 0]) / len(df_customers)), 1)
        st.write(f"Percentage of Users who have zero Upvotes: **{zero_Upvotes_pct}%**")


        referrers_count = df_customers[df_customers.Number_Upvotes != 0]['Number_Upvotes'].value_counts().reset_index()
        referrers_count.columns = ["Number_Upvotes", "Count"]
        referrers_count = referrers_count.sort_values("Number_Upvotes")

        fig, ax = plt.subplots()
        ax.bar(referrers_count["Number_Upvotes"], referrers_count["Count"])
        ax.set_title("Upvotes Distribution")
        ax.set_xlabel("Upvotes")
        ax.set_ylabel("Count")
        st.pyplot(fig)
        
