import sys
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # Change to your MySQL user
    'password': '7806',     # Change to your MySQL password
    'database': 'warehouse_db',
    'port': 3306
}

def get_non_empty_string(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("[!] Error: Input cannot be empty.")

def get_positive_float(prompt):
    while True:
        try:
            val = float(input(prompt).strip())
            if val > 0:
                return val
            print("[!] Error: Value must be greater than zero.")
        except ValueError:
            print("[!] Error: Please enter a valid numerical value.")

def get_non_negative_int(prompt):
    while True:
        try:
            val = int(input(prompt).strip())
            if val >= 0:
                return val
            print("[!] Error: Value cannot be negative.")
        except ValueError:
            print("[!] Error: Please enter a valid integer.")

def get_positive_int(prompt):
    while True:
        try:
            val = int(input(prompt).strip())
            if val > 0:
                return val
            print("[!] Error: Value must be greater than zero.")
        except ValueError:
            print("[!] Error: Please enter a valid integer.")

def get_valid_location(prompt):
    """Enforces warehouse locations to start strictly with Section A or B."""
    while True:
        loc = input(prompt).strip().upper()
        if loc and loc.startswith(('A', 'B')):
            return loc
        print("[!] Error: Warehouse location must start with Section 'A' or 'B' (e.g., A1-01, B2-05).")

class Database:
    def __init__(self, config):
        self.config = config

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"[!] Database Connection Error: {e}")
            return None

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return True
        except Error as e:
            print(f"[!] Query Execution Error: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"[!] Query Fetch Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"[!] Query Fetch Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

class LoginManager:
    def __init__(self, db):
        self.db = db

    def login(self):
        print("\n--- SYSTEM LOGIN ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        query = "SELECT * FROM Users WHERE username = %s AND password = %s"
        user = self.db.fetch_one(query, (username, password))

        if user:
            print(f"\n[+] Login successful! Welcome {user['username']} ({user['role'].upper()})")
            return user
        else:
            print("\n[!] Invalid username or password.")
            return None

    def change_password(self, current_user):
        print("\n--- CHANGE PASSWORD ---")
        old_pass = input("Enter current password: ").strip()
        
        check_query = "SELECT * FROM Users WHERE user_id = %s AND password = %s"
        user = self.db.fetch_one(check_query, (current_user['user_id'], old_pass))

        if not user:
            print("[!] Incorrect current password.")
            return

        new_pass = input("Enter new password: ").strip()
        if not new_pass:
            print("[!] Password cannot be empty.")
            return

        update_query = "UPDATE Users SET password = %s WHERE user_id = %s"
        if self.db.execute_query(update_query, (new_pass, current_user['user_id'])):
            print("[+] Password updated successfully.")

class SupplierManager:
    def __init__(self, db):
        self.db = db

    def add_supplier(self):
        print("\n--- ADD SUPPLIER ---")
        name = get_non_empty_string("Supplier Name: ")
        phone = input("Phone Number: ").strip()
        email = input("Email: ").strip()
        address = input("Address: ").strip()

        query = "INSERT INTO Suppliers (supplier_name, phone, email, address) VALUES (%s, %s, %s, %s)"
        if self.db.execute_query(query, (name, phone, email, address)):
            print("[+] Supplier added successfully.")

    def view_suppliers(self):
        print("\n--- SUPPLIER LIST ---")
        suppliers = self.db.fetch_all("SELECT * FROM Suppliers")
        if not suppliers:
            print("No suppliers found.")
            return
        
        print(f"{'ID':<5} | {'Name':<30} | {'Phone':<16} | {'Email':<30}")
        print("-" * 88)
        for s in suppliers:
            print(f"{s['supplier_id']:<5} | {s['supplier_name']:<30} | {str(s['phone']):<16} | {str(s['email']):<30}")

    def update_supplier(self):
        print("\n--- UPDATE SUPPLIER ---")
        sup_id = get_positive_int("Enter Supplier ID to update: ")
        existing = self.db.fetch_one("SELECT * FROM Suppliers WHERE supplier_id = %s", (sup_id,))
        
        if not existing:
            print("[!] Supplier ID does not exist.")
            return

        print("Press ENTER to keep current values.")
        name = input(f"New Name [{existing['supplier_name']}]: ").strip() or existing['supplier_name']
        phone = input(f"New Phone [{existing['phone']}]: ").strip() or existing['phone']
        email = input(f"New Email [{existing['email']}]: ").strip() or existing['email']
        address = input(f"New Address [{existing['address']}]: ").strip() or existing['address']

        query = "UPDATE Suppliers SET supplier_name = %s, phone = %s, email = %s, address = %s WHERE supplier_id = %s"
        if self.db.execute_query(query, (name, phone, email, address, sup_id)):
            print("[+] Supplier details updated.")

    def delete_supplier(self):
        print("\n--- DELETE SUPPLIER ---")
        sup_id = get_positive_int("Enter Supplier ID to delete: ")
        if self.db.execute_query("DELETE FROM Suppliers WHERE supplier_id = %s", (sup_id,)):
            print("[+] Supplier deleted successfully.")

class ProductManager:
    def __init__(self, db):
        self.db = db

    def add_product(self):
        print("\n--- ADD PRODUCT ---")
        name = get_non_empty_string("Product Name: ")
        category = get_non_empty_string("Category (e.g., Mobile, Laptop, Electronics): ")
        price = get_positive_float("Price: ")
        quantity = get_non_negative_int("Initial Quantity: ")
        location = get_valid_location("Warehouse Location (Section A or B, e.g. A1-01, B2-05): ")
        supplier_id = get_positive_int("Supplier ID: ")

        supplier = self.db.fetch_one("SELECT * FROM Suppliers WHERE supplier_id = %s", (supplier_id,))
        if not supplier:
            print("[!] Error: Supplier ID does not exist. Please create supplier first.")
            return

        query = """
            INSERT INTO Products (product_name, category, price, quantity, warehouse_location, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (name, category, price, quantity, location, supplier_id)):
            print("[+] Product registered successfully.")

    def view_products(self):
        print("\n--- PRODUCT INVENTORY ---")
        query = """
            SELECT p.product_id, p.product_name, p.category, p.price, p.quantity, p.warehouse_location, s.supplier_name
            FROM Products p
            LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.product_id ASC
        """
        products = self.db.fetch_all(query)
        if not products:
            print("No products in inventory.")
            return

        print(f"{'ID':<5} | {'Name':<35} | {'Category':<15} | {'Price':<10} | {'Qty':<6} | {'Loc':<8} | {'Supplier':<25}")
        print("-" * 115)
        for p in products:
            sup_name = p['supplier_name'] or "N/A"
            print(f"{p['product_id']:<5} | {p['product_name']:<35} | {p['category']:<15} | ${p['price']:<9.2f} | {p['quantity']:<6} | {p['warehouse_location']:<8} | {sup_name:<25}")

    def search_product(self):
        print("\n--- SEARCH PRODUCT ---")
        term = input("Search by Name or Category: ").strip()
        query = "SELECT * FROM Products WHERE product_name LIKE %s OR category LIKE %s"
        results = self.db.fetch_all(query, (f"%{term}%", f"%{term}%"))

        if not results:
            print("No matching products found.")
            return

        print(f"{'ID':<5} | {'Name':<35} | {'Category':<15} | {'Price':<10} | {'Qty':<6} | {'Loc':<8}")
        print("-" * 88)
        for p in results:
            print(f"{p['product_id']:<5} | {p['product_name']:<35} | {p['category']:<15} | ${p['price']:<9.2f} | {p['quantity']:<6} | {p['warehouse_location']:<8}")

    def update_product(self):
        print("\n--- UPDATE PRODUCT ---")
        prod_id = get_positive_int("Enter Product ID to update: ")
        existing = self.db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (prod_id,))

        if not existing:
            print("[!] Product ID not found.")
            return

        print("Press ENTER to keep existing values.")
        name = input(f"New Name [{existing['product_name']}]: ").strip() or existing['product_name']
        category = input(f"New Category [{existing['category']}]: ").strip() or existing['category']
        price_in = input(f"New Price [{existing['price']}]: ").strip()
        price = float(price_in) if price_in else existing['price']
        
        loc_in = input(f"New Location [{existing['warehouse_location']}]: ").strip().upper()
        if loc_in:
            while not loc_in.startswith(('A', 'B')):
                print("[!] Error: Warehouse location must start with Section 'A' or 'B'.")
                loc_in = input("Enter valid location (Section A or B): ").strip().upper()
            location = loc_in
        else:
            location = existing['warehouse_location']

        query = """
            UPDATE Products 
            SET product_name = %s, category = %s, price = %s, warehouse_location = %s 
            WHERE product_id = %s
        """
        if self.db.execute_query(query, (name, category, price, location, prod_id)):
            print("[+] Product updated successfully.")

    def delete_product(self):
        print("\n--- DELETE PRODUCT ---")
        prod_id = get_positive_int("Enter Product ID to delete: ")
        if self.db.execute_query("DELETE FROM Products WHERE product_id = %s", (prod_id,)):
            print("[+] Product deleted successfully.")

class WarehouseManager:
    def __init__(self, db):
        self.db = db

    def assign_location(self):
        print("\n--- ASSIGN WAREHOUSE LOCATION ---")
        prod_id = get_positive_int("Enter Product ID: ")
        product = self.db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (prod_id,))
        
        if not product:
            print("[!] Product ID not found.")
            return

        new_loc = get_valid_location(f"Current Location [{product['warehouse_location']}]. New Location (Section A or B): ")
        query = "UPDATE Products SET warehouse_location = %s WHERE product_id = %s"
        if self.db.execute_query(query, (new_loc, prod_id)):
            print("[+] Warehouse location assigned successfully.")

    def view_by_location(self):
        print("\n--- VIEW PRODUCTS BY LOCATION / SECTION ---")
        loc = input("Enter Location or Section Prefix (e.g., A1, B2, or 'A' / 'B'): ").strip().upper()
        query = "SELECT * FROM Products WHERE warehouse_location LIKE %s"
        products = self.db.fetch_all(query, (f"{loc}%",))

        if not products:
            print(f"No products found at location matching '{loc}'.")
            return

        print(f"{'ID':<5} | {'Product Name':<35} | {'Quantity':<6} | {'Location':<10}")
        print("-" * 65)
        for p in products:
            print(f"{p['product_id']:<5} | {p['product_name']:<35} | {p['quantity']:<6} | {p['warehouse_location']:<10}")

class StockManager:
    def __init__(self, db):
        self.db = db

    def stock_in(self):
        print("\n--- STOCK IN ---")
        prod_id = get_positive_int("Product ID: ")
        qty = get_positive_int("Quantity to Add: ")

        product = self.db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (prod_id,))
        if not product:
            print("[!] Product not found.")
            return

        new_qty = product['quantity'] + qty
        update_q = "UPDATE Products SET quantity = %s WHERE product_id = %s"
        history_q = "INSERT INTO Stock_History (product_id, stock_in, stock_out) VALUES (%s, %s, 0)"

        if self.db.execute_query(update_q, (new_qty, prod_id)) and self.db.execute_query(history_q, (prod_id, qty)):
            print(f"[+] Stock updated! New Quantity: {new_qty}")

    def stock_out(self):
        print("\n--- STOCK OUT ---")
        prod_id = get_positive_int("Product ID: ")
        qty = get_positive_int("Quantity to Deduct: ")

        product = self.db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (prod_id,))
        if not product:
            print("[!] Product not found.")
            return

        if product['quantity'] < qty:
            print(f"[!] Error: Insufficient inventory. Available: {product['quantity']}")
            return

        new_qty = product['quantity'] - qty
        update_q = "UPDATE Products SET quantity = %s WHERE product_id = %s"
        history_q = "INSERT INTO Stock_History (product_id, stock_in, stock_out) VALUES (%s, 0, %s)"

        if self.db.execute_query(update_q, (new_qty, prod_id)) and self.db.execute_query(history_q, (prod_id, qty)):
            print(f"[+] Stock deducted! Remaining Quantity: {new_qty}")

class OrderManager:
    def __init__(self, db):
        self.db = db

    def create_order(self):
        print("\n--- CREATE ORDER ---")
        customer = get_non_empty_string("Customer Name: ")
        prod_id = get_positive_int("Product ID: ")
        qty = get_positive_int("Order Quantity: ")

        product = self.db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (prod_id,))
        if not product:
            print("[!] Product does not exist.")
            return

        if product['quantity'] < qty:
            print(f"[!] Stock insufficient. Current stock: {product['quantity']}")
            return

        query = "INSERT INTO Orders (customer_name, product_id, quantity, status) VALUES (%s, %s, %s, 'Pending')"
        if self.db.execute_query(query, (customer, prod_id, qty)):
            print("[+] Order created with state 'Pending'.")

    def dispatch_order(self):
        print("\n--- DISPATCH ORDER ---")
        order_id = get_positive_int("Enter Order ID to dispatch: ")
        order = self.db.fetch_one("SELECT * FROM Orders WHERE order_id = %s", (order_id,))

        if not order:
            print("[!] Order not found.")
            return

        if order['status'] != 'Pending':
            print(f"[!] Cannot dispatch. Current status: {order['status']}")
            return

        product = self.db.fetch_one("SELECT * FROM Products WHERE product_id = %s", (order['product_id'],))
        if product['quantity'] < order['quantity']:
            print(f"[!] Cannot dispatch order. Stock too low ({product['quantity']}).")
            return

        new_qty = product['quantity'] - order['quantity']
        update_prod = "UPDATE Products SET quantity = %s WHERE product_id = %s"
        history_q = "INSERT INTO Stock_History (product_id, stock_in, stock_out) VALUES (%s, 0, %s)"
        update_order = "UPDATE Orders SET status = 'Dispatched' WHERE order_id = %s"

        if (self.db.execute_query(update_prod, (new_qty, order['product_id'])) and
            self.db.execute_query(history_q, (order['product_id'], order['quantity'])) and
            self.db.execute_query(update_order, (order_id,))):
            print("[+] Order successfully dispatched and inventory updated!")

    def cancel_order(self):
        print("\n--- CANCEL ORDER ---")
        order_id = get_positive_int("Enter Order ID to cancel: ")
        order = self.db.fetch_one("SELECT * FROM Orders WHERE order_id = %s", (order_id,))

        if not order:
            print("[!] Order not found.")
            return

        if order['status'] == 'Dispatched':
            print("[!] Cannot cancel an already dispatched order.")
            return

        query = "UPDATE Orders SET status = 'Cancelled' WHERE order_id = %s"
        if self.db.execute_query(query, (order_id,)):
            print("[+] Order cancelled.")

    def view_orders(self):
        print("\n--- ORDER HISTORY ---")
        query = """
            SELECT o.order_id, o.customer_name, p.product_name, o.quantity, o.status, o.order_date
            FROM Orders o
            JOIN Products p ON o.product_id = p.product_id
            ORDER BY o.order_date DESC
        """
        orders = self.db.fetch_all(query)
        if not orders:
            print("No orders recorded.")
            return

        print(f"{'ID':<5} | {'Customer':<25} | {'Product':<30} | {'Qty':<5} | {'Status':<12} | {'Date':<19}")
        print("-" * 105)
        for o in orders:
            print(f"{o['order_id']:<5} | {o['customer_name']:<25} | {o['product_name']:<30} | {o['quantity']:<5} | {o['status']:<12} | {str(o['order_date']):<19}")

class ReportManager:
    def __init__(self, db):
        self.db = db

    def summary_report(self):
        print("\n--- INVENTORY SUMMARY REPORT ---")
        tot_products = self.db.fetch_one("SELECT COUNT(*) AS total FROM Products")['total']
        tot_stock = self.db.fetch_one("SELECT SUM(quantity) AS total FROM Products")['total'] or 0
        valuation = self.db.fetch_one("SELECT SUM(quantity * price) AS total FROM Products")['total'] or 0.0

        print(f"Total Unique Product Lines: {tot_products}")
        print(f"Total Stock Units in House: {tot_stock}")
        print(f"Total Inventory Valuation: ${valuation:,.2f}")

    def low_stock_report(self, threshold=5):
        print(f"\n--- LOW STOCK REPORT (Threshold <= {threshold}) ---")
        query = "SELECT product_id, product_name, quantity, warehouse_location FROM Products WHERE quantity <= %s"
        results = self.db.fetch_all(query, (threshold,))

        if not results:
            print("All stock levels are optimal.")
            return

        print(f"{'ID':<5} | {'Product Name':<35} | {'Quantity':<10} | {'Location':<10}")
        print("-" * 68)
        for r in results:
            print(f"{r['product_id']:<5} | {r['product_name']:<35} | {r['quantity']:<10} | {r['warehouse_location']:<10}")

    def transaction_history_report(self):
        print("\n--- RECENT STOCK MOVEMENT LOGS ---")
        query = """
            SELECT sh.stock_id, p.product_name, sh.stock_in, sh.stock_out, sh.transaction_date
            FROM Stock_History sh
            JOIN Products p ON sh.product_id = p.product_id
            ORDER BY sh.transaction_date DESC LIMIT 20
        """
        logs = self.db.fetch_all(query)
        if not logs:
            print("No transactions logged.")
            return

        print(f"{'ID':<5} | {'Product':<30} | {'Stock In':<10} | {'Stock Out':<10} | {'Timestamp':<19}")
        print("-" * 82)
        for l in logs:
            print(f"{l['stock_id']:<5} | {l['product_name']:<30} | {l['stock_in']:<10} | {l['stock_out']:<10} | {str(l['transaction_date']):<19}")

class Dashboard:
    def __init__(self, db, current_user, login_mgr, prod_mgr, sup_mgr, wh_mgr, stock_mgr, order_mgr, rpt_mgr):
        self.db = db
        self.user = current_user
        self.login_mgr = login_mgr
        self.prod_mgr = prod_mgr
        self.sup_mgr = sup_mgr
        self.wh_mgr = wh_mgr
        self.stock_mgr = stock_mgr
        self.order_mgr = order_mgr
        self.rpt_mgr = rpt_mgr

    def show(self):
        while True:
            print("\n=================================")
            print(f" WAREHOUSE DASHBOARD ({self.user['role'].upper()})")
            print("=================================")
            print("1. Product Management")
            print("2. Supplier Management")
            print("3. Warehouse Locations (Section A & B)")
            print("4. Stock In / Stock Out")
            print("5. Order Management")
            print("6. Reports")
            print("7. Change Password")
            print("8. Logout")
            
            choice = input("Select Option (1-8): ").strip()

            if choice == '1':
                self.product_menu()
            elif choice == '2':
                self.supplier_menu()
            elif choice == '3':
                self.warehouse_menu()
            elif choice == '4':
                self.stock_menu()
            elif choice == '5':
                self.order_menu()
            elif choice == '6':
                self.reports_menu()
            elif choice == '7':
                self.login_mgr.change_password(self.user)
            elif choice == '8':
                print("[+] Logged out safely.")
                break
            else:
                print("[!] Invalid selection.")

    def product_menu(self):
        while True:
            print("\n--- PRODUCT MENU ---")
            print("1. View Products")
            print("2. Search Product")
            print("3. Add Product")
            print("4. Update Product")
            print("5. Delete Product (Admin Only)")
            print("6. Back to Main Menu")

            ch = input("Choice: ").strip()
            if ch == '1': self.prod_mgr.view_products()
            elif ch == '2': self.prod_mgr.search_product()
            elif ch == '3': self.prod_mgr.add_product()
            elif ch == '4': self.prod_mgr.update_product()
            elif ch == '5':
                if self.user['role'] == 'admin':
                    self.prod_mgr.delete_product()
                else:
                    print("[!] Permission Denied: Admin rights required.")
            elif ch == '6': break

    def supplier_menu(self):
        while True:
            print("\n--- SUPPLIER MENU ---")
            print("1. View Suppliers")
            print("2. Add Supplier")
            print("3. Update Supplier")
            print("4. Delete Supplier (Admin Only)")
            print("5. Back to Main Menu")

            ch = input("Choice: ").strip()
            if ch == '1': self.sup_mgr.view_suppliers()
            elif ch == '2': self.sup_mgr.add_supplier()
            elif ch == '3': self.sup_mgr.update_supplier()
            elif ch == '4':
                if self.user['role'] == 'admin':
                    self.sup_mgr.delete_supplier()
                else:
                    print("[!] Permission Denied: Admin rights required.")
            elif ch == '5': break

    def warehouse_menu(self):
        while True:
            print("\n--- WAREHOUSE LOCATION MENU (Section A & B) ---")
            print("1. View Products at Location / Section")
            print("2. Assign / Move Product Location")
            print("3. Back to Main Menu")

            ch = input("Choice: ").strip()
            if ch == '1': self.wh_mgr.view_by_location()
            elif ch == '2': self.wh_mgr.assign_location()
            elif ch == '3': break

    def stock_menu(self):
        while True:
            print("\n--- STOCK MANAGEMENT ---")
            print("1. Stock In (+) ")
            print("2. Stock Out (-) ")
            print("3. Back to Main Menu")

            ch = input("Choice: ").strip()
            if ch == '1': self.stock_mgr.stock_in()
            elif ch == '2': self.stock_mgr.stock_out()
            elif ch == '3': break

    def order_menu(self):
        while True:
            print("\n--- ORDERS MANAGEMENT ---")
            print("1. View Orders")
            print("2. Create New Order")
            print("3. Dispatch Order")
            print("4. Cancel Order")
            print("5. Back to Main Menu")

            ch = input("Choice: ").strip()
            if ch == '1': self.order_mgr.view_orders()
            elif ch == '2': self.order_mgr.create_order()
            elif ch == '3': self.order_mgr.dispatch_order()
            elif ch == '4': self.order_mgr.cancel_order()
            elif ch == '5': break

    def reports_menu(self):
        while True:
            print("\n--- REPORTS MENU ---")
            print("1. Inventory Summary")
            print("2. Low Stock Warning")
            print("3. Recent Stock Movements")
            print("4. Back to Main Menu")

            ch = input("Choice: ").strip()
            if ch == '1': self.rpt_mgr.summary_report()
            elif ch == '2': self.rpt_mgr.low_stock_report()
            elif ch == '3': self.rpt_mgr.transaction_history_report()
            elif ch == '4': break

def main():
    db = Database(DB_CONFIG)
    
    conn = db.get_connection()
    if not conn:
        print("[!] Critical Error: Could not connect to MySQL database.")
        sys.exit(1)
    conn.close()

    login_mgr = LoginManager(db)
    prod_mgr = ProductManager(db)
    sup_mgr = SupplierManager(db)
    wh_mgr = WarehouseManager(db)
    stock_mgr = StockManager(db)
    order_mgr = OrderManager(db)
    rpt_mgr = ReportManager(db)

    print("=========================================")
    print("      WAREHOUSE MANAGEMENT SYSTEM        ")
    print("=========================================")

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Login")
        print("2. Exit System")
        choice = input("Select an option (1-2): ").strip()

        if choice == '1':
            user = login_mgr.login()
            if user:
                dashboard = Dashboard(
                    db, user, login_mgr, prod_mgr, sup_mgr, 
                    wh_mgr, stock_mgr, order_mgr, rpt_mgr
                )
                dashboard.show()
        elif choice == '2':
            print("\nExiting system. Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid option. Select 1 or 2.")

if __name__ == "__main__":
    main()
    
