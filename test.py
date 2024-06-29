with open('fund.txt', 'r') as file:
    fund = file.read()
print(int(fund.split(",")[0]))