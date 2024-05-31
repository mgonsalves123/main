import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr
from datetime import datetime

def get_amazon_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Try different possible class names for price elements
    price = None
    possible_classes = [
        "a-price-whole",
        "priceToPay",
        "priceblock_ourprice",
        "priceblock_dealprice"
    ]

    for class_name in possible_classes:
        price_element = soup.find("span", {"class": class_name})
        if price_element:
            price = price_element.get_text()
            break

    if price:
        # Remove any commas or other characters and convert to float
        price = price.replace(",", "").replace("$", "").strip()
        try:
            return float(price)
        except ValueError:
            return None
    return None

# Track price history
price_history = pd.DataFrame(columns=["Date", "Price"])

def track_price(url):
    global price_history
    current_price = get_amazon_price(url)
    if current_price:
        new_entry = pd.DataFrame({"Date": [datetime.now()], "Price": [current_price]})
        price_history = pd.concat([price_history, new_entry], ignore_index=True)
        price_history.to_csv("price_history.csv", index=False)
        return f"Current price: ${current_price}"
    else:
        return "Failed to retrieve the price. Please check the URL or try again later."

# Plot price history
def plot_price_history():
    if price_history.empty:
        return "No price data available."
    
    plt.figure(figsize=(10, 5))
    plt.plot(price_history["Date"], price_history["Price"], marker='o')
    plt.title("Amazon Product Price History")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.grid(True)
    plt.savefig("price_history.png")
    plt.close()
    return "price_history.png"

# Load existing price history if available
try:
    price_history = pd.read_csv("price_history.csv")
except FileNotFoundError:
    price_history = pd.DataFrame(columns=["Date", "Price"])

# Gradio interface
def respond(url):
    result = track_price(url)
    plot = plot_price_history()
    return result, plot

# Define Gradio interface
demo = gr.Interface(
    fn=respond,
    inputs=[gr.Textbox(label="Amazon Product URL")],
    outputs=[gr.Textbox(label="Price Tracking Result"), gr.Image(label="Price History Plot")]
)

if __name__ == "__main__":
    demo.launch()
