import tkinter as tk
from tkinter import messagebox
import mysql.connector
import bcrypt
import bookingsystem

# Database Setup
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="hotel_booking",
        port=3306
    )
    c = conn.cursor()
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")
    exit()

# Create users table if it doesn't exist
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        userID INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        role VARCHAR(20) DEFAULT 'customer'
    )
""")
conn.commit()

# Create default admin user if it doesn't exist
c.execute("SELECT * FROM users WHERE email = %s", ("admin@gmail.com",))
if not c.fetchone():
    password = "admin123".encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    c.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
              ("Admin", "admin@gmail.com", hashed, "admin"))
    conn.commit()
    print("Default admin user created: email=admin@gmail.com, password=admin123")

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password")
        return

    c.execute("SELECT userID, username, password, role FROM users WHERE email=%s", (email,))
    user = c.fetchone()

    if user:
        print(f"User found: {user}")  
        print(f"Role: {user[3]}")    
        if check_password(user[2], password):
            root.destroy()
            if user[3] == 'admin':
                print("Opening admin system") 
                bookingsystem.open_admin_system(user[0], user[1])
            else:
                print("Opening booking system") 
                bookingsystem.open_booking_system(user[0], user[1])
        else:
            messagebox.showerror("Login Failed", "Invalid email or password")
    else:
        messagebox.showerror("Login Failed", "Invalid email or password")

def register():
    root.destroy()
    register_window()

def register_window():
    reg_root = tk.Tk()
    reg_root.title("Register")
    reg_root.geometry("400x350")
    
    tk.Label(reg_root, text="Register", font=("Arial", 18, "bold")).pack(pady=10)
    
    tk.Label(reg_root, text="Username:", font=("Arial", 12)).pack()
    reg_username_entry = tk.Entry(reg_root, font=("Arial", 12))
    reg_username_entry.pack()
    
    tk.Label(reg_root, text="Email:", font=("Arial", 12)).pack()
    reg_email_entry = tk.Entry(reg_root, font=("Arial", 12))
    reg_email_entry.pack()
    
    tk.Label(reg_root, text="Password:", font=("Arial", 12)).pack()
    reg_password_entry = tk.Entry(reg_root, font=("Arial", 12), show="*")
    reg_password_entry.pack()
    
    tk.Button(reg_root, text="Register", font=("Arial", 12, "bold"), 
              command=lambda: register_user(reg_root, reg_username_entry, reg_email_entry, reg_password_entry)).pack(pady=10)
    tk.Button(reg_root, text="Back to Login", font=("Arial", 12), 
              command=lambda: [reg_root.destroy(), main()]).pack(pady=5)
    
    reg_root.mainloop()

def register_user(reg_root, reg_username_entry, reg_email_entry, reg_password_entry):
    username = reg_username_entry.get().strip()
    email = reg_email_entry.get().strip()
    password = reg_password_entry.get().strip()
    role = "customer"
    
    if not all([username, email, password]):
        messagebox.showerror("Error", "Please fill in all fields")
        return
    
    c.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    if c.fetchone():
        messagebox.showerror("Error", "Username or email already exists")
        return
    
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)", 
                 (username, email, hashed_password, role))
        conn.commit()
        messagebox.showinfo("Success", "Account Created Successfully")
        reg_root.destroy()
        main()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Registration failed: {e}")

def main():
    global root, email_entry, password_entry
    
    root = tk.Tk()
    root.title("Login")
    root.geometry("400x300")
    root.configure(bg="white")
    
    tk.Label(root, text="Login", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(root, text="Email:", font=("Arial", 12)).pack()
    email_entry = tk.Entry(root, font=("Arial", 12))
    email_entry.pack()
    
    tk.Label(root, text="Password:", font=("Arial", 12)).pack()
    password_entry = tk.Entry(root, font=("Arial", 12), show="*")
    password_entry.pack()
    
    tk.Button(root, text="Login", font=("Arial", 12, "bold"), command=login).pack(pady=10)
    tk.Button(root, text="Register", font=("Arial", 12), command=register).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()