import matplotlib.pyplot as plt
import pandas as pd

# This part would typically involve loading data from a file or an API.
# For the purpose of this example, we'll create a simple DataFrame manually.
# You would replace this with your actual data loading logic.
apple_stock_data = pd.DataFrame({
    'Date': pd.date_range(start="2022-01-01", periods=5, freq='D'),
    'Close': [150.00, 153.25, 157.85, 155.20, 159.45]
})

# Plot the stock prices.
plt.figure(figsize=(10, 5))
plt.plot(apple_stock_data['Date'], apple_stock_data['Close'], marker='o')
plt.title('Apple Stock Price')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')

# Save the plot to a file.
plt.savefig('stock_price.png')
plt.close()