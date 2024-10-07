import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import yfinance as yf
from datetime import datetime

# Page title and layout
st.set_page_config(page_title="Automated Financial Portfolio Management System", layout="wide")
st.title("📈 Automated Financial Portfolio Management System")
st.write("Welcome! Manage your financial portfolio with ease and get insights to make informed decisions.")

# Create a DataFrame to store portfolio data if it doesn't exist already
if "portfolio_data" not in st.session_state:
    st.session_state.portfolio_data = pd.DataFrame(columns=["Symbol", "Quantity", "Price", "Date Added"])

# Sidebar to add stock to portfolio
st.sidebar.header("Add Stock to Portfolio")
with st.sidebar.form("add_stock_form"):
    symbol = st.text_input("Stock Symbol (e.g., AAPL, GOOGL)").upper()
    quantity = st.number_input("Quantity", min_value=1, step=1)
    add_stock = st.form_submit_button("Add to Portfolio")

# Add stock to the portfolio DataFrame
if add_stock:
    if symbol and quantity > 0:
        # Fetch the current price using yfinance
        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")["Close"].iloc[-1]
        except:
            price = None

        if price is not None:
            # Prepare a new data entry as a DataFrame
            new_data_df = pd.DataFrame({
                "Symbol": [symbol],
                "Quantity": [quantity],
                "Price": [price],
                "Date Added": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })

            # Concatenate with the existing DataFrame
            st.session_state.portfolio_data = pd.concat([st.session_state.portfolio_data, new_data_df], ignore_index=True)

            st.success(f"Added {quantity} shares of {symbol} at ${price:.2f} per share.")
        else:
            st.error(f"Could not fetch the current price for {symbol}. Please try again later.")
    else:
        st.error("Please enter valid values for all fields.")

# Display portfolio data as a table
st.subheader("📊 Current Portfolio")
if not st.session_state.portfolio_data.empty:
    st.dataframe(st.session_state.portfolio_data)
else:
    st.write("Your portfolio is empty. Please add some stocks.")

# Add a pie chart to visualize portfolio distribution
if not st.session_state.portfolio_data.empty:
    st.subheader("💹 Portfolio Distribution")

    # Calculate total value per stock
    st.session_state.portfolio_data["Total Value"] = st.session_state.portfolio_data["Quantity"] * st.session_state.portfolio_data["Price"]

    # Create a pie chart of stock distribution
    pie_chart = alt.Chart(st.session_state.portfolio_data).mark_arc().encode(
        theta=alt.Theta(field="Total Value", type="quantitative"),
        color=alt.Color(field="Symbol", type="nominal"),
        tooltip=["Symbol", "Total Value"]
    ).properties(title="Stock Distribution")

    st.altair_chart(pie_chart, use_container_width=True)

# Display portfolio metrics
if not st.session_state.portfolio_data.empty:
    total_investment = st.session_state.portfolio_data["Total Value"].sum()
    total_stocks = st.session_state.portfolio_data["Quantity"].sum()

    st.metric("💸 Total Investment", f"${total_investment:,.2f}")
    st.metric("📈 Total Stocks Held", f"{int(total_stocks)}")

# Sidebar to remove stock from portfolio
st.sidebar.header("Remove Stock from Portfolio")
with st.sidebar.form("remove_stock_form"):
    stock_to_remove = st.selectbox("Select a Stock to Remove", st.session_state.portfolio_data["Symbol"].unique() if not st.session_state.portfolio_data.empty else [""])
    remove_stock = st.form_submit_button("Remove Stock")

# Remove the selected stock from the portfolio
if remove_stock and stock_to_remove:
    st.session_state.portfolio_data = st.session_state.portfolio_data[st.session_state.portfolio_data["Symbol"] != stock_to_remove]
    st.success(f"Removed all shares of {stock_to_remove} from the portfolio.")

# Advanced Features
if not st.session_state.portfolio_data.empty:
    st.subheader("📊 Advanced Portfolio Insights")

    # Fetch real-time stock data using yfinance
    def get_stock_data(symbol):
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo")
            return hist
        except:
            return None

    # Display historical price chart for each stock
    for symbol in st.session_state.portfolio_data["Symbol"].unique():
        st.subheader(f"📉 Historical Data for {symbol}")
        stock_data = get_stock_data(symbol)
        if stock_data is not None and not stock_data.empty:
            line_chart = alt.Chart(stock_data.reset_index()).mark_line().encode(
                x="Date:T",
                y="Close:Q",
                tooltip=["Date", "Close"]
            ).properties(title=f"{symbol} Price Trend (Last Month)")
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.write(f"Could not fetch data for {symbol}.")

    # Recommendations based on portfolio analysis
    st.subheader("💡 Portfolio Recommendations")
    if total_investment < 5000:
        st.info("Consider increasing your investment to diversify your portfolio and reduce risk.")
    elif len(st.session_state.portfolio_data["Symbol"].unique()) < 3:
        st.info("Your portfolio has limited diversity. Adding more stocks from different sectors could improve stability.")
    else:
        st.success("Your portfolio is well diversified. Keep monitoring for market trends.")

    # Display risk assessment based on stock volatility
    st.subheader("📊 Risk Assessment")
    for symbol in st.session_state.portfolio_data["Symbol"].unique():
        stock_data = get_stock_data(symbol)
        if stock_data is not None and not stock_data.empty:
            stock_volatility = np.std(stock_data["Close"]) / np.mean(stock_data["Close"])
            risk_level = "High" if stock_volatility > 0.05 else "Low"
            st.write(f"{symbol}: Volatility - {stock_volatility:.2f}, Risk Level - {risk_level}")