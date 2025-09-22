import mysql.connector
from mysql.connector import Error
import getpass
from tabulate import tabulate

# ---------------- DATABASE CONNECTION ---------------- #
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",        # 🔹 change this to your MySQL username
            password="Kusuma@1610", # 🔹 change this to your MySQL password
            database="todopy"   # 🔹 database name
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# ---------------- DATABASE SETUP ---------------- #
def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kusuma@1610"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS todopy")
    cursor.execute("use todopy")

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            description VARCHAR(255) NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# ---------------- USER FUNCTIONS ---------------- #
def register_user():
    conn = create_connection()
    cursor = conn.cursor()
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        print("✅ Registration successful! Please login.")
    except Error as e:
        if "Duplicate entry" in str(e):
            print("❌ Username already exists.")
        else:
            print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()


def login_user():
    conn = create_connection()
    cursor = conn.cursor()
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    cursor.execute("SELECT user_id FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        print(f"✅ Login successful! Welcome {username}")
        return result[0], username
    else:
        print("❌ Invalid username or password.")
        return None, None

# ---------------- TASK FUNCTIONS ---------------- #
def add_task(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    description = input("Enter task description: ")
    cursor.execute("INSERT INTO tasks (user_id, description) VALUES (%s, %s)", (user_id, description))
    conn.commit()
    print("✅ Task added successfully!")
    cursor.close()
    conn.close()

def view_tasks(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, description, status, created_at FROM tasks WHERE user_id=%s", (user_id,))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()

    if tasks:
        print(tabulate(tasks, headers=["ID", "Description", "Status", "Created At"], tablefmt="grid"))
    else:
        print("📭 No tasks found.")

def update_task(user_id):
    view_tasks(user_id)
    task_id = input("Enter task ID to update: ")
    print("1. Mark as Completed\n2. Edit Description")
    choice = input("Enter choice: ")

    conn = create_connection()
    cursor = conn.cursor()

    if choice == "1":
        cursor.execute("UPDATE tasks SET status='Completed' WHERE task_id=%s AND user_id=%s", (task_id, user_id))
    elif choice == "2":
        new_desc = input("Enter new description: ")
        cursor.execute("UPDATE tasks SET description=%s WHERE task_id=%s AND user_id=%s", (new_desc, task_id, user_id))
    else:
        print("❌ Invalid choice.")
        return

    conn.commit()
    print("✅ Task updated successfully!")
    cursor.close()
    conn.close()

def delete_task(user_id):
    view_tasks(user_id)
    task_id = input("Enter task ID to delete: ")

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id=%s AND user_id=%s", (task_id, user_id))
    conn.commit()
    print("🗑 Task deleted successfully!")
    cursor.close()
    conn.close()

# ---------------- MAIN APP ---------------- #
def main():
    setup_database()

    while True:
        print("\n============================")
        print("   USER-BASED TODO SYSTEM")
        print("============================")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            register_user()
        elif choice == "2":
            user_id, username = login_user()
            if user_id:
                while True:
                    print(f"\n===== TODO DASHBOARD ({username}) =====")
                    print("1. Add Task")
                    print("2. View My Tasks")
                    print("3. Update Task")
                    print("4. Delete Task")
                    print("5. Logout")

                    option = input("Enter choice: ")

                    if option == "1":
                        add_task(user_id)
                    elif option == "2":
                        view_tasks(user_id)
                    elif option == "3":
                        update_task(user_id)
                    elif option == "4":
                        delete_task(user_id)
                    elif option == "5":
                        print("👋 Logged out successfully.")
                        break
                    else:
                        print("❌ Invalid choice.")
        elif choice == "3":
            print("👋 Exiting program. Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()


