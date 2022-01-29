from console.inputs import ListInputOptions, ListInput, InputResult


myOptions = ListInputOptions()
myInput = ListInput(myOptions)

result, names = myInput("Enter Names")

print("Names:", ', '.join(names))




