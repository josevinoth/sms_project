class CafeteriaStack:
    def __init__(self):
        self.stack = []

    def push(self, order):
        """
        Place a new food order onto the stack (push operation).
        """
        self.stack.append(order)

    def pop(self):
        """
        Process the most recent order (pop operation).
        """
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None  # No orders to process

    def peek(self):
        """
        Peek at the most recent order without removing it from the stack.
        """
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None  # No orders to peek at

    def cancel_order(self, order_to_cancel):
        """
        Cancel a specific order from the stack.
        """
        if order_to_cancel in self.stack:
            self.stack.remove(order_to_cancel)
            return True  # Order canceled successfully
        else:
            return False  # Order not found in the stack

    def modify_order(self, old_order, new_order):
        """
        Modify a specific order in the stack.
        """
        if old_order in self.stack:
            index = self.stack.index(old_order)
            self.stack[index] = new_order
            return True  # Order modified successfully
        else:
            return False  # Order not found in the stack

    def is_empty(self):
        """
        Check if the stack is empty.
        """
        return len(self.stack) == 0

    def get_orders(self):
        """
        Get a list of all orders in the stack.
        """
        return self.stack

# Create a cafeteria stack
cafeteria_stack = CafeteriaStack()

print("*************Make Selection***********")
print("1. Place Order")
print("2. Cancel Order")
print("3. Modify Order")
print("4. Process Order")

ch=int(input("Enter selection: "))

if ch==1:
    # Place orders
    order_status='Yes'
    while order_status=='Yes':
        order = (input("Enter your Order: "))
        cafeteria_stack.push(order)
        order_status=((input("Do you like to order more?")))
    cafeteria_stack.get_orders()

elif ch==2:
    # Cancel an order
    cafeteria_stack.stack = ["Dosa", "Idli"]
    print(cafeteria_stack.stack)
    order_to_cancel = (input("Enter your Order to Cancel: "))
    if cafeteria_stack.cancel_order(order_to_cancel):
        print(f"{order_to_cancel} has been canceled.")
    else:
        print(f"{order_to_cancel} not found in the orders.")

elif ch==3:
    # Modify an order
    cafeteria_stack.stack = ["Dosa", "Idli"]
    old_order = input("Enter Old Order: ")
    new_order = input("Enter New Order: ")
    if cafeteria_stack.modify_order(old_order, new_order):
        print(f"{old_order} has been modified to {new_order}.")
    else:
        print(f"{old_order} not found in the orders.")

elif ch==4:
    # Process orders (LIFO) using pop
    cafeteria_stack.stack = ["Dosa", "Idli"]
    processed_order = cafeteria_stack.pop()
    print("Processed Order (Pop):", processed_order)  # Output: Processed Order (Pop): Salad

# Get the current list of orders
current_orders = cafeteria_stack.get_orders()
print("Current Orders:", current_orders)  # Output: Current Orders: ['Hot Dog']

# Peek at the most recent order without removing it
latest_order = cafeteria_stack.peek()
print("Latest Order (Peek):", latest_order)  # Output: Latest Order (Peek): Salad
