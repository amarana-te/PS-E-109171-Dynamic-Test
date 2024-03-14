my_dict = {1285674: ["AZid", "RIid", 123]}

for key, value_list in my_dict.items():
  for value in value_list[:-1]:  # Iterate up to the second-last element
    # Do something with each value except the last
    print(value)
