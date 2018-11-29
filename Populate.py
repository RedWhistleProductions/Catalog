#!/usr/bin/env python3
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
Add_Item(1, "Felix", "Cartoon Character", "", "Felix.png")
Add_Item(2, "Spike", "Cartoon Character", "", "Spike.png")
Add_Item(3, "George", "Cartoon Character", "", "George.jpg")
Add_Item(1, "Nintendo", "Classic Gaming System", "", "NES.jpg")
Add_Item(2, "Playstation", "Classic Gaming System", "", "Playstation.jpg")
Add_Item(3, "Sega", "Classic Gaming System", "", "Sega.jpg")
Add_Item(1, "Pizza", "Food", "", "Pizza.jpg")
Add_Item(2, "Tacos", "Food", "", "Tacos.jpg")
Add_Item(3, "Sushi", "Food", "", "Sushi.jpg")
Add_Item(3, "Programming Meme", "Meme", "", "CMD_is_not_BASH.jpg")
print("Items Added /n/n")

Display()
