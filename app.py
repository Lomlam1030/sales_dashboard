import streamlit as st
import pandas as pd
from datetime import date
from services import SalesService
import altair as alt
import calendar

# Theme colors for charts and visualizations
COLORS = {
    'background': '#E6E6FA',     # Lilac
    'primary': '#4169E1',        # Royal Blue
    'accent': '#8A2BE2',         # BlueViolet
    'text': '#1E1E3F',           # Dark Blue for text on light background
    'card': '#483D8B',           # DarkSlateBlue for tabs
    'tab_selected': '#6A5ACD'    # SlateBlue for selected tab
}

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Apply custom CSS
st.markdown(f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {COLORS['background']};
    }}
    
    /* Text colors */
    .stMarkdown, p, span {{
        color: {COLORS['text']};
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['primary']};
    }}
    
    /* Metric cards */
    [data-testid="stMetricValue"] {{
        color: {COLORS['primary']};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {COLORS['card']};
        color: white;
    }}
    
    /* Buttons */
    .stButton>button {{
        background-color: {COLORS['card']};
        color: #E6E6FA !important;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: normal;
        height: 3rem;
        transition: all 0.3s ease;
        font-size: 1rem;
        font-family: sans-serif;
    }}
    
    /* Button text styling to match tabs */
    .stButton>button p, .stButton>button span, .stButton>button div {{
        color: #E6E6FA !important;
        font-weight: 400 !important;
        font-family: sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }}
    
    /* Button hover effect */
    .stButton>button:hover {{
        background-color: {COLORS['tab_selected']};
        color: #E6E6FA !important;
        border: none;
    }}
    
    /* Button active effect */
    .stButton>button:active {{
        background-color: {COLORS['tab_selected']};
        color: #E6E6FA !important;
        border: none;
        transform: translateY(1px);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        margin: 0 0 2rem 0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 3rem;
        white-space: pre-wrap;
        background-color: {COLORS['card']};
        border-radius: 4px;
        padding: 1rem;
        margin-right: 1rem;
    }}

    /* Override the tab text color */
    .stTabs [data-baseweb="tab"] * {{
        color: #E6E6FA !important;
    }}
    
    button[role="tab"] {{
        color: #E6E6FA !important;
    }}
    
    button[role="tab"] div {{
        color: #E6E6FA !important;
    }}

    /* Selected tab */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {COLORS['tab_selected']};
    }}

    /* Tab hover effect */
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {COLORS['tab_selected']};
        transition: all 0.3s ease;
    }}

    /* Override all button text colors */
    button, button *, .stButton button, .stButton button * {{
        color: #E6E6FA !important;
        fill: #E6E6FA !important;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize the sales service
sales_service = SalesService()

def show_daily_sales():
    # Select actuals date range
    col1, col2 = st.columns(2)
    with col1:
        actual_start = st.date_input("Start of Actuals", value=date(2007, 1, 1))
    with col2:
        actual_end = st.date_input("End of Actuals", value=date(2008, 12, 31), min_value=actual_start)
        
    if st.button("Show Actuals"):
        try:
            with st.spinner('Fetching data...'):
                # Fetch data for selected range
                df = sales_service.get_daily_sales(
                actual_start.strftime("%Y-%m-%d"),
                actual_end.strftime("%Y-%m-%d")
                )
                
                if df.empty:
                    st.warning("No data available for the selected date range.")
                    return
                
                # Process data
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                df['total_sales_millions'] = df['total_sales'] / 1_000_000
                df = df.sort_values(by="date")
                
                # Create title with date range
                title = f"📅 Daily Sales Trend ({actual_start.strftime('%Y-%m-%d')} to {actual_end.strftime('%Y-%m-%d')})"
                
                # Create Altair chart
                chart = alt.Chart(df).mark_line(
                    color='#4B6EF5',              # Navy blue (you can also use 'navy')
                    strokeWidth=2).encode(
                    x=alt.X('date:T', 
                           title='Date',
                           axis=alt.Axis(format='%Y-%m-%d', labelAngle=45)),
                    y=alt.Y('total_sales_millions:Q',
                           title='Total Sales (Millions $)',
                           scale=alt.Scale(
                               domain=[
                                   df['total_sales_millions'].min() * 0.98,
                                   df['total_sales_millions'].max() * 1.02
                               ]
                           ),
                           axis=alt.Axis(format='$,.4f')),
                    tooltip=[
                        alt.Tooltip('date:T', title='Date', format='%Y-%m-%d'),
                        alt.Tooltip('total_sales_millions:Q', title='Sales (M)', format='$,.4f'),
                        alt.Tooltip('day_of_week:N', title='Day'),
                        alt.Tooltip('store_count:Q', title='Stores'),
                        alt.Tooltip('product_count:Q', title='Products')
                    ]
                ).properties(
                    title=title,
                    height=500
                ).configure_point(
                    size=100
                ).interactive()
                
                # Display the chart
                st.altair_chart(chart, use_container_width=True)
                
                # Stats
                st.subheader("📊 Summary Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Min Sales", f"${df['total_sales_millions'].min():.2f}M")
                with col2:
                    st.metric("Avg Sales", f"${df['total_sales_millions'].mean():.2f}M")
                with col3:
                    st.metric("Max Sales", f"${df['total_sales_millions'].max():.2f}M")
                
                # Raw data
                with st.expander("📄 Show Raw Data"):
                    st.dataframe(df)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Check if API is reachable.")

    st.markdown("### 🔮 Extend with Prediction")
    col3, col4 = st.columns(2)
    with col3:
        prediction_start = st.date_input("Start of Prediction", value=date(2009, 1, 1), min_value=actual_end)
    with col4:
        prediction_end = st.date_input("End of Prediction", value=date(2009, 3, 31), min_value=prediction_start)

    if st.button("Show Actuals + Predictions"):
        try:
            with st.spinner("Fetching data..."):
                # --- Get actuals ---
                df_actual = sales_service.get_daily_sales(
                    actual_start.strftime("%Y-%m-%d"),
                    actual_end.strftime("%Y-%m-%d")
                )
                df_actual['date'] = pd.to_datetime(df_actual['date'])
                df_actual['sales_millions'] = df_actual['total_sales'] / 1_000_000
                df_actual['type'] = 'Actual'

                # --- Get predictions ---
                predfactor = 16.0
                df_pred = sales_service.get_sales_prediction(
                    prediction_start.strftime("%Y-%m-%d"),
                    prediction_end.strftime("%Y-%m-%d")
                )
                df_pred['date'] = pd.to_datetime(df_pred['date'])
                df_pred['sales_millions'] = df_pred['predicted_sales'] / 1_000_000 * predfactor
                df_pred['type'] = 'Predicted'

                # --- Combine ---
                df_combined = pd.concat([
                    df_actual[['date', 'sales_millions', 'type']],
                    df_pred[['date', 'sales_millions', 'type']]
                ])

                # --- Plot ---
                chart = alt.Chart(df_combined).mark_line().encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('sales_millions:Q', title='Sales (Millions $)'),
                    color=alt.Color('type:N', scale=alt.Scale(
                        domain=['Actual', 'Predicted'],
                        range=['#4B6EF5', '#D8BFD8']  # Royal Blue, Purple
                    )),
                    tooltip=[
                        alt.Tooltip('date:T', format='%Y-%m-%d'),
                        alt.Tooltip('type:N'),
                        alt.Tooltip('sales_millions:Q', title='Sales (M)', format='$,.2f')
                    ]
                ).properties(
                    title=f"📈 Actual Sales + Predictions ({actual_start} to {prediction_end})",
                    height=500
                ).interactive()

                st.altair_chart(chart, use_container_width=True)

                # KPIs
                st.subheader("📊 Key Stats")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Actual Sales", f"${df_actual['sales_millions'].sum():,.2f}M")
                with col2:
                    st.metric("Total Predicted Sales", f"${df_pred['sales_millions'].sum():,.2f}M")
                with col3:
                    st.metric("Days Predicted", len(df_pred))

                # Raw data
                with st.expander("📄 Show Combined Data"):
                    st.dataframe(df_combined)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def show_monthly_sales():
    # Year selection
    selected_year = st.selectbox(
        "Select Year",
        options=range(2007, 2009),
        key="monthly_year_select"
    )
    
    if st.button("Get Monthly Sales"):
        try:
            with st.spinner('Fetching data...'):
                # Fetch yearly data
                response = sales_service.get_monthly_sales(selected_year)
                
                if not response or 'monthly_data' not in response:
                    st.warning("No data available for the selected year.")
                    return
                
                # Convert monthly data to DataFrame
                df = pd.DataFrame(response['monthly_data'])
                
                # Convert sales to millions for better readability
                df['total_sales_millions'] = df['total_sales'] / 1_000_000
                
                # Create title
                title = f"📅 Monthly Sales for {selected_year}"
                
                # Create Altair chart for monthly sales
                sales_chart = alt.Chart(df).mark_line(point=True, color='#4B6EF5').encode(
                    x=alt.X('month:N', 
                           title='Month',
                           sort=None),  # Preserve month order
                    y=alt.Y('total_sales_millions:Q',
                           title='Total Sales (Millions $)',
                           scale=alt.Scale(
                               domain=[
                                   df['total_sales_millions'].min() * 0.98,
                                   df['total_sales_millions'].max() * 1.02
                               ]
                           ),
                           axis=alt.Axis(format='$,.2f')),
                    tooltip=[
                        alt.Tooltip('month:N', title='Month'),
                        alt.Tooltip('total_sales_millions:Q', title='Sales (M)', format='$,.2f'),
                        alt.Tooltip('store_count:Q', title='Stores'),
                        alt.Tooltip('product_count:Q', title='Products'),
                        alt.Tooltip('avg_sale_amount:Q', title='Avg Sale', format='$,.2f')
                    ]
                ).properties(
                    title=title,
                    height=400
                ).configure_point(
                    size=100
                ).interactive()
                
                # Create line chart for store and product count trends
                metrics_df = pd.melt(df, 
                                   id_vars=['month'], 
                                   value_vars=['store_count', 'product_count'],
                                   var_name='metric',
                                   value_name='count')
                
                metrics_chart = alt.Chart(metrics_df).mark_line(point=True).encode(
                    x=alt.X('month:N', 
                           title='Month',
                           sort=None),
                    y=alt.Y('count:Q',
                           title='Count'),
                    color=alt.Color('metric:N', 
                                  title='Metric',
                                  legend=alt.Legend(
                                      title=None,
                                      orient='top')),
                    tooltip=[
                        alt.Tooltip('month:N', title='Month'),
                        alt.Tooltip('metric:N', title='Metric'),
                        alt.Tooltip('count:Q', title='Count')
                    ]
                ).properties(
                    title='Store and Product Count Trends',
                    height=300
                ).interactive()
                
                # Display the charts
                st.altair_chart(sales_chart, use_container_width=True)
                st.altair_chart(metrics_chart, use_container_width=True)
                
                # Yearly Summary
                st.subheader("📊 Yearly Summary")
                
                # Sales metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Yearly Sales", 
                             f"${response['total_yearly_sales']/1_000_000:.2f}M")
                with col2:
                    st.metric("Average Monthly Sales", 
                             f"${(response['total_yearly_sales']/12)/1_000_000:.2f}M")
                with col3:
                    st.metric("Peak Month", 
                             f"{df.loc[df['total_sales'].idxmax(), 'month']}")
                
                # Store and Product metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Store Count (End of Year)", 
                             f"{df.iloc[-1]['store_count']}")
                with col2:
                    st.metric("Product Count (End of Year)", 
                             f"{df.iloc[-1]['product_count']}")
                with col3:
                    avg_sale = df['avg_sale_amount'].mean()
                    st.metric("Average Sale Amount", 
                             f"${avg_sale:.2f}")
                
                # Raw data
                with st.expander("📄 Show Raw Data"):
                    st.dataframe(df.style.format({
                        'total_sales': '${:,.2f}',
                        'avg_sale_amount': '${:,.2f}'
                    }))
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Check if API is reachable.")

def show_sales_prediction():
    st.subheader("🔮Prediction View")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        min_date = st.date_input(
            "Start Date",
            value=date(2009, 1, 1),
            key="prediction_start_date"
        )
    with col2:
        max_date = st.date_input(
            "End Date",
            value=date(2009, 1, 31),
            min_value=min_date,
            key="prediction_end_date"
        )
    
    if st.button("Get Sales Prediction"):
        try:
            with st.spinner('Fetching predictions...'):
                # Fetch prediction data
                predfactor = 16.0
                df = sales_service.get_sales_prediction(
                    min_date.strftime("%Y-%m-%d"),
                    max_date.strftime("%Y-%m-%d")
                )
                
                if df.empty:
                    st.warning("No predictions available for the selected date range.")
                    return
                
                # Convert sales to thousands for better readability
                df['predicted_sales_k'] = df['predicted_sales'] / 1000 * predfactor
                
                # Create title
                title = f"🔮 Prediction View ({min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')})"
                
                # Create Altair chart
                chart = alt.Chart(df).mark_line(
                    point=True,
                    strokeDash=[6, 3],  # Creates dotted line
                    color='#D8BFD8'     # Light purple (thistle)
                ).encode(
                    x=alt.X('date:T', 
                           title='Date',
                           axis=alt.Axis(format='%Y-%m-%d', labelAngle=45)),
                    y=alt.Y('predicted_sales_k:Q',
                           title='Predicted Sales (Thousands $)',
                           scale=alt.Scale(
                               domain=[
                                   df['predicted_sales_k'].min() * 0.98,
                                   df['predicted_sales_k'].max() * 1.02,
                               ]
                           ),
                           axis=alt.Axis(format='$,.2f')),
                    tooltip=[
                        alt.Tooltip('date:T', title='Date', format='%Y-%m-%d'),
                        alt.Tooltip('predicted_sales_k:Q', title='Predicted Sales (K)', format='$,.2f')
                    ]
                ).properties(
                    title=title,
                    height=500
                ).configure_point(
                    size=100,
                    color='#D8BFD8'  # Match points color with line
                ).interactive()
                
                # Display the chart
                st.altair_chart(chart, use_container_width=True)
                
                # Summary statistics
                st.subheader("📊 Prediction Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Min Predicted Sales", 
                             f"${df['predicted_sales'].min()/1000:.2f}K") 
                with col2:
                    st.metric("Avg Predicted Sales", 
                             f"${df['predicted_sales'].mean()/1000:.2f}K")
                with col3:
                    st.metric("Max Predicted Sales", 
                             f"${df['predicted_sales'].max()/1000:.2f}K")
                
                # Raw data
                with st.expander("📄 Show Raw Data"):
                    st.dataframe(df.style.format({
                        'predicted_sales': '${:,.2f}',
                        'predicted_sales_k': '${:,.2f}K'
                    }))
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Check if prediction API is reachable.")

def main():
    # Enhanced title with gradient background
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1 style="color: white; margin: 0;">📊 Sales Ninja Dashboard</h1>
        <p style="color: #f0f0f0; margin-top: 0.5rem;">Track performance, predict trends, and uncover insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Daily Sales", "Monthly Sales", "Sales Prediction"])
    
    with tab1:
        show_daily_sales()
    
    with tab2:
        show_monthly_sales()
        
    with tab3:
        show_sales_prediction()

if __name__ == "__main__":
    main()
