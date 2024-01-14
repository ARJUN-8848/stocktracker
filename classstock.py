import mysql.connector
import pandas as pd
from datetime import datetime
from plyer import notification
import csv
import random

class StockPortfolioTracker:
    def __init__(self):     #private
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="8848613225",
                database="userr"
            )
            self.cursor = self.mydb.cursor()

            self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(50) NOT NULL UNIQUE, password INT NOT NULL)")
            self.mydb.commit()

            self.cursor.execute("CREATE TABLE IF NOT EXISTS stock (id INT AUTO_INCREMENT PRIMARY KEY, symbol VARCHAR(10) NOT NULL, shares DECIMAL(10, 2) NOT NULL, purchase_price DECIMAL(10, 2) NOT NULL, purchase_date DATE NOT NULL)")
            self.mydb.commit()

            self.cursor.execute("CREATE TABLE IF NOT EXISTS alerts (id INT AUTO_INCREMENT PRIMARY KEY, symbol VARCHAR(10) NOT NULL, threshold DECIMAL(10, 2) NOT NULL)")
            self.mydb.commit()

            self.cursor.execute("CREATE TABLE IF NOT EXISTS transaction_history (id INT AUTO_INCREMENT PRIMARY KEY,symbol VARCHAR(10) NOT NULL,transaction_type VARCHAR(10) NOT NULL,shares DECIMAL(10, 2) NOT NULL,price DECIMAL(10, 2) NOT NULL,transaction_date DATETIME NOT NULL)")
            self.mydb.commit()

        except Exception as e:
            print("DATABASE ALREADY EXISTS!!!!!!!!!")
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="8848613225",
                database="stock"
            )
            self.cursor = self.mydb.cursor()

        self.user = None

    def register_user(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        insert_user = "INSERT INTO users (username, password) VALUES (%s, %s)"
        user_data = (username, password)
        self.cursor.execute(insert_user, user_data)
        self.mydb.commit()
        print("User registered successfully.")

    def authenticate_user(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        select_user = "SELECT * FROM users WHERE username = %s AND password = %s"
        user_data = (username, password)
        self.cursor.execute(select_user, user_data)
        user = self.cursor.fetchone()

        if user:
            print("Login successful.")
            self.user = user
            return True
        else:
            print("Invalid username or password. Please try again.")
            return False

    def login_menu(self):
        while True:
            print("\n---------------------Stock Portfolio Tracker Login:-----------------------")
            print("1. Register New User")
            print("2. Login")
            print("3. Exit")

            login_choice = input("Enter your choice (1/2/3): ")

            if login_choice == "1":
                self.register_user()
            elif login_choice == "2":
                if self.authenticate_user():
                    break
            elif login_choice == "3":
                exit()
            else:
                print("Invalid choice. Please enter a valid option.")

    def welcome_user(self):
        user_id, username, _ = self.user
        print(f"Welcome, {username}!")

    def add_stock(self):
        symbol = input("Enter the stock symbol: ")
        shares = float(input("Enter the number of shares: "))
        purchase_price = float(input("Enter the purchase price per share: "))
        purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
        add_stock_query = "INSERT INTO stock (symbol, shares, purchase_price, purchase_date) VALUES (%s, %s, %s, %s)"
        data = (symbol, shares, purchase_price, purchase_date)
        self.cursor.execute(add_stock_query, data)
        self.mydb.commit()
        print("Stock added successfully.")

    def update_stock(self):
        self.display_stock()
        stock_id = input("Enter the ID of the stock you want to update: ")
        self.cursor.execute("SELECT * FROM stock WHERE id = %s", (stock_id,))
        stock_info = self.cursor.fetchone()
        if not stock_info:
            print("Stock not found.")
            return
        print(f"Current Stock Information: {stock_info}")
        new_shares = float(input("Enter the new number of shares: "))
        new_price = float(input("Enter the new purchase price per share: "))
        new_date = input("Enter the new purchase date (YYYY-MM-DD): ")

        update_stock_query = "UPDATE stock SET shares = %s, purchase_price = %s, purchase_date = %s WHERE id = %s"
        new_data = (new_shares, new_price, new_date, stock_id)
        self.cursor.execute(update_stock_query, new_data)
        self.mydb.commit()
        print("Stock information updated successfully.")

    def display_stock(self):
        display_stock_query = "SELECT * FROM stock"
        self.cursor.execute(display_stock_query)
        result = self.cursor.fetchall()

        if not result:
            print("Stocks not found.")
        else:
            print("Stocks:")
            for a in result:
                print(f"ID: {a[0]}, Symbol: {a[1]}, Shares: {a[2]}, Purchase Price: {a[3]}, Purchase Date: {a[4]}")

    def delete_stock(self):
        self.display_stock()
        stock_id = input("Enter the ID of the stock you want to delete: ")

        delete_stock_query = "DELETE FROM stock WHERE id = %s"
        self.cursor.execute(delete_stock_query, (stock_id,))
        self.mydb.commit()
        print("Stock deleted successfully.")

    def calculate_stock_value(self):
        self.cursor.execute("SELECT symbol, shares, purchase_price FROM stock")
        stocks = self.cursor.fetchall()
        total_value = 0

        for stock in stocks:
            symbol = stock[0]
            shares = stock[1]
            purchase_price = stock[2]
            stock_value = shares * purchase_price
            total_value = total_value + stock_value
            print(f"Symbol: {symbol}, Shares: {shares}, Purchase Price: {purchase_price}, Value: {stock_value}")

        print(f"Total Portfolio Value: {total_value}")

    def export_stocks(self):
        self.cursor.execute("SELECT * FROM stock")
        stocks = self.cursor.fetchall()

        if not stocks:
            print("No stocks to export.")
        else:
            df = pd.DataFrame(stocks, columns=['ID', 'Symbol', 'Shares', 'Purchase Price', 'Purchase Date'])
            filename = f"stock_portfolio_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"Stocks exported to {filename} successfully.")

    def set_price_alert(self):
        symbol = input("Enter the stock symbol for the alert: ")
        threshold = float(input("Enter the price threshold for the alert: "))

        add_alert_query = "INSERT INTO alerts (symbol, threshold) VALUES (%s, %s)"
        data = (symbol, threshold)
        self.cursor.execute(add_alert_query, data)
        self.mydb.commit()
        print("Price alert set successfully.")

    def check_price_alerts(self):
        self.cursor.execute("SELECT symbol, threshold FROM alerts")
        alerts = self.cursor.fetchall()

        for alert in alerts:
            symbol = alert[0]
            threshold = alert[1]
            self.cursor.execute("SELECT purchase_price FROM stock WHERE symbol = %s", (symbol,))
            current_price = self.cursor.fetchone()[0]

            if current_price and float(current_price) < threshold:
                message = f"Alert: {symbol} price is below {threshold}! Current Price: {current_price}"
                notification.notify(title='Stock Alert', message=message, app_name='Stock Portfolio Tracker',)

    def Hint(self):
        sub = ['1.Before investing, take the time to educate yourself about the stock market. \n Understand the basics of how it works, different investment vehicles, and the factors that can affect stock prices.',
               '2.Define your financial goals and investment objectives. \n Are you investing for short-term gains, long-term growth, or income? Having clear goals will help guide your investment decisions.',
               '3.Diversification involves spreading your investments across different asset classes, industries, and geographic regions. \n This helps reduce risk by not putting all your money into one investment.',
               '4. Successful investing often requires a long-term perspective.\n The stock market can be volatile in the short term, but historically, it has shown overall growth over longer periods.']
        sentence = f"{random.choice(sub)}."
        print(sentence)

    def add_transaction_history(self):
        symbol = input("Enter the stock symbol: ")
        transaction_type = input("Enter the transaction type (Buy/Sell): ")
        shares = float(input("Enter the number of shares: "))
        price = float(input("Enter the transaction price per share: "))
        add_transaction = "INSERT INTO transaction_history (symbol, transaction_type, shares, price, transaction_date) VALUES (%s, %s, %s, %s, %s)"
        transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (symbol, transaction_type, shares, price, transaction_date)
        self.cursor.execute(add_transaction, data)
        self.mydb.commit()
        print("Transaction added to history successfully.")

    def display_transaction_history(self):
        self.cursor.execute("SELECT * FROM transaction_history")
        transactions = self.cursor.fetchall()

        if not transactions:
            print("No transactions found.")
        else:
            print("Transaction History:")
            for transaction in transactions:
                print(
                    f"ID: {transaction[0]}, Symbol: {transaction[1]}, Type: {transaction[2]}, Shares: {transaction[3]}, Price: {transaction[4]}, Date: {transaction[5]}")

if __name__ == "__main__":
    stock_tracker = StockPortfolioTracker()
    stock_tracker.login_menu()
    stock_tracker.welcome_user()

    while True:
        print("\n---------------------Stock Portfolio Tracker Menu:-----------------------")
        print("1. Add Stock")
        print("2. Update Stock")
        print("3. Display Stock")
        print("4. Delete Stock")
        print("5. Calculate Stock Value")
        print("6. Export Stocks to CSV")
        print("7. Set Price Alert")
        print("8. Check Price Alerts")
        print("9. Hint")
        print("10. Add transaction history")
        print("11. Display transaction history")
        print("12. Exit")

        choice = input("Enter your choice (1/2/3/4/5/6/7/8/9/10/11/12): ")

        if choice == "1":
            stock_tracker.add_stock()
        elif choice == "2":
            stock_tracker.update_stock()
        elif choice == "3":
            stock_tracker.display_stock()
        elif choice == "4":
            stock_tracker.delete_stock()
        elif choice == "5":
            stock_tracker.calculate_stock_value()
        elif choice == "6":
            stock_tracker.export_stocks()
        elif choice == "7":
            stock_tracker.set_price_alert()
        elif choice == "8":
            stock_tracker.check_price_alerts()
        elif choice == "9":
            stock_tracker.Hint()
        elif choice == "10":
            stock_tracker.add_transaction_history()
        elif choice == "11":
            stock_tracker.display_transaction_history()
        elif choice == "12":
            break
        else:
            print("Invalid choice. Please enter a valid option.")
