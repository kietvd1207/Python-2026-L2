colors = ["Purple", "Orange", "Yellow", "Red", "Blue", "Black"]

favorite = input("What is your favorite color? ")

if favorite in colors:
    index = colors.index(favorite)
    print("Your color is at index", index, "in my list")
else:
    print("Sorry, I could not find your color")