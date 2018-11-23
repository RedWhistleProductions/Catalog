from application import *

print("Adding Users")
# Add_User(User_Name, Password, First, Last, Email)
Add_User("Sugar_Bear", "Wifey", "Sarah", "Snyder", "Wifey@LocalHost")
Add_User("Cyber_Cat", "Meow", "Cathy", "Garcia", "Cyber_Cat@LocalHost")
Add_User(
    "Mischieveous_Monkey",
    "Banana",
    "Billy",
    "Bob",
    "Mischieveous_Monkey@LocalHost")
Add_User("Dashing_Dog", "Woof", "Diego", "Gonzalez", "Dashing_Dog@LocalHost")
print("Users Added /n/n Adding Items")

# Add_Item(Owner_ID, Name, Category, Description = "", Image = "")
Add_Item(1, "Felix", "Stuffed Animal")
Add_Item(2, "Spike", "Stuffed Animal")
Add_Item(3, "George", "Stuffed Animal")
Add_Item(1, "Nintendo", "Gaming System")
Add_Item(2, "Playstation", "Gaming System")
Add_Item(3, "Sega", "Gaming System")
Add_Item(1, "Pizza", "Food")
Add_Item(2, "Tacos", "Food")
Add_Item(3, "Sushi", "Food")
print("Items Added /n/n")

Display()
