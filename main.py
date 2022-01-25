from console.input import selection_input

colors = ('red', 'orange', 'yellow', 'green', 'blue', 'purple')

def upper_first(in_str):
  return in_str[0].upper() + in_str[1:]

output = selection_input("Select A Color: ", colors, item_format_method=upper_first)
print(output)

