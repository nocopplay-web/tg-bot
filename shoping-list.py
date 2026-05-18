import sqlite3

shopping_list = []


def add_product(shopping_list):
    """asks the user for the product name and price, then add it to the list."""
    name = input("Enter product name: ")
    price = float(input("Enter product price: "))
    product = {'name': name,
            'price': price,
            }
    shopping_list.append(product)
    print(f"Product {name} added!")
    
def show_list(shopping_list):
    """Print all products in the list with numbers. If the list is empty, print a message.
"""
    length = len(shopping_list)
    if length == 0:
        print("The list is empty")
    else:
        print("My shopping list")
        i = 1
        for product in shopping_list:
            print(str(i) + ". " + product['name'] + " - " + str(product['price']) + " rub. ")
            i += 1

def calculate_total(shopping_list):
    """calculates the total amount of goods"""
    total = 0
    for product in shopping_list:
        total += product['price']
    return total

def save_to_db(shopping_list, filename):
    con = sqlite3.connect(filename)
    cursor = con.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (name TEXT, price REAL)""")
    con.commit()
    
    cursor.execute("DELETE FROM products")
    con.commit()
    
    for product in shopping_list:
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (product['name'], product['price']))
    con.commit()  
    con.close()
        
    print("Save to: " + filename)
        

    
def load_from_db(filename):
    con = sqlite3.connect(filename)
    cursor = con.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (name TEXT, price REAL)""")
    con.commit()
    
    cursor.execute("SELECT name, price FROM products")
    rows = cursor.fetchall()
    con.close()
    
    result = []
    
    for row in rows:
        product = {"name": row[0], "price": row[1]}
        result.append(product)
    
    return result

def main():
    filename = "shopping_list.db"
    shopping_list = load_from_db(filename)
    
    while True:
        print("\n===MENU===")
        print("1. Add product:")
        print("2. Check list")
        print("3. Show total")
        print("4. Exit")
        
        choicer = input("Enter please action: ")
        if choicer == '1':
            add_product(shopping_list)
        elif choicer == '2':
            show_list(shopping_list)
        elif choicer == '3':
            total = calculate_total(shopping_list)
            print("Total: " + str(total) + " rub")
        elif choicer == '4':
            save_to_db(shopping_list, filename)
            print("Goodbye")
            break
        else:
            print("Wrong choice, try again")
        
main()
    

        

    