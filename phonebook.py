import sqlite3
import csv

# Database connection
conn = sqlite3.connect('phonebook.db')
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS PhoneBook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    phone_number TEXT UNIQUE NOT NULL
)
""")
conn.commit()

# Function to insert data from console
def insert_from_console():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name (optional): ")
    phone_number = input("Enter phone number: ")

    try:
        cursor.execute("""
        INSERT INTO PhoneBook (first_name, last_name, phone_number)
        VALUES (?, ?, ?)""", (first_name, last_name, phone_number))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.IntegrityError as e:
        print("Error:", e)

# Function to insert data from CSV
def insert_from_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print("Headers in CSV:", reader.fieldnames)  # Debug: Show headers
            if 'first_name' not in reader.fieldnames or 'phone_number' not in reader.fieldnames:
                print("Error: CSV must contain 'first_name', 'last_name', and 'phone_number' headers.")
                return
            
            for row in reader:
                print("Inserting row:", row)  # Debug: Show each row
                cursor.execute("""
                INSERT INTO PhoneBook (first_name, last_name, phone_number)
                VALUES (?, ?, ?)""", (row['first_name'], row.get('last_name', None), row['phone_number']))
            conn.commit()
            print("Data uploaded from CSV successfully!")
    except FileNotFoundError:
        print("Error: CSV file not found.")
    except sqlite3.IntegrityError as e:
        print("Error inserting data into the database:", e)


# Function to update data
def update_data():
    choice = input("What do you want to update? (1-First Name, 2-Phone): ")
    identifier = input("Enter the phone number or first name to identify the record: ")

    if choice == "1":
        new_first_name = input("Enter the new first name: ")
        cursor.execute("""
        UPDATE PhoneBook
        SET first_name = ?
        WHERE phone_number = ? OR first_name = ?
        """, (new_first_name, identifier, identifier))
    elif choice == "2":
        new_phone = input("Enter the new phone number: ")
        cursor.execute("""
        UPDATE PhoneBook
        SET phone_number = ?
        WHERE phone_number = ? OR first_name = ?
        """, (new_phone, identifier, identifier))
    else:
        print("Invalid choice.")
        return

    conn.commit()
    print("Data updated successfully!")

# Function to query data
def query_data():
    print("Filters: 1-All Records, 2-By First Name, 3-By Phone Number")
    choice = input("Choose a filter option: ")

    if choice == "1":
        cursor.execute("SELECT * FROM PhoneBook")
        results = cursor.fetchall()
    elif choice == "2":
        first_name = input("Enter first name to search: ")
        cursor.execute("SELECT * FROM PhoneBook WHERE first_name LIKE ?", (f"%{first_name}%",))
        results = cursor.fetchall()
    elif choice == "3":
        phone_number = input("Enter phone number to search: ")
        cursor.execute("SELECT * FROM PhoneBook WHERE phone_number = ?", (phone_number,))
        results = cursor.fetchall()
    else:
        print("Invalid choice.")
        return

    for row in results:
        print(row)

# Function to delete data
def delete_data():
    identifier = input("Enter the username or phone number to delete the record: ")

    cursor.execute("""
    DELETE FROM PhoneBook
    WHERE first_name = ? OR phone_number = ?
    """, (identifier, identifier))
    conn.commit()

    print("Record deleted successfully!")

# Menu for interaction
def menu():
    while True:
        print("\nPhoneBook Menu")
        print("1. Insert from console")
        print("2. Insert from CSV")
        print("3. Update data")
        print("4. Query data")
        print("5. Delete data")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            insert_from_console()
        elif choice == "2":
            file_path = input("Enter the path of the CSV file: ")
            insert_from_csv(file_path)
        elif choice == "3":
            update_data()
        elif choice == "4":
            query_data()
        elif choice == "5":
            delete_data()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")

# Run the menu
menu()

# Close database connection
conn.close()
