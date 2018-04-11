import pandas as pd

offers = inputs['offers']

products = ["Savings", "Mortgage", "Pension"]

# How much revenue is earned when selling each product
productValue = [200, 300, 400]
value_per_product = {products[i] : productValue[i] for i in range(len(products))}

# Total available budget
availableBudget = 25000

# For each channel, cost of making a marketing action and success factor
channels =  pd.DataFrame(data=[("gift", 20.0, 0.20), 
                               ("newsletter", 15.0, 0.05), 
                               ("seminar", 23.0, 0.30)], columns=["name", "cost", "factor"])

offersR = range(0, len(offers))
productsR = range(0, len(products))
channelsR = range(0, len(channels))


gsol = pd.DataFrame()
gsol['id'] = offers['id']

budget = 0
revenue = 0

for product in products:
    gsol[product] = 0
   
noffers = len(offers)

# ensure the 10% per channel by choosing the most promising per channel
for c in channelsR: #, channel in channels.iterrows():
    i = 0;
    while (i< ( noffers // 10 ) ):
        # find a possible offer in this channel for a customer not yet done
        added = False
        for o  in offersR:
            already = False
            for product in products:   
                if gsol.get_value(index=o, col=product) == 1:
                    already = True
                    break
            if already:
                continue
            possible = False
            possibleProduct = None
            for product in products:
                if offers.get_value(index=o, col=product) == 1:
                    possible = True
                    possibleProduct = product
                    break
            if not possible:
                continue
            #print "Assigning customer ", offers.get_value(index=o, col="id"), " with product ", product, " and channel ", channel['name']
            gsol.set_value(index=o, col=possibleProduct, value=1)
            i = i+1
            added = True
            budget = budget + channels.get_value(index=c, col="cost")
            revenue = revenue + channels.get_value(index=c, col="factor")*value_per_product[product]            
            break
        if not added:
            print("NOT FEASIBLE")
            break
			
# add more to complete budget       
while (True):
    added = False
    for c, channel in channels.iterrows():
        if (budget + channel.cost > availableBudget):
            continue
        # find a possible offer in this channel for a customer not yet done
        for o  in offersR:
            already = False
            for product in products:   
                if gsol.get_value(index=o, col=product) == 1:
                    already = True
                    break
            if already:
                continue
            possible = False
            possibleProduct = None
            for product in products:
                if offers.get_value(index=o, col=product) == 1:
                    possible = True
                    possibleProduct = product
                    break
            if not possible:
                continue
            #print "Assigning customer ", offers.get_value(index=o, col="id"), " with product ", product, " and channel ", channel['name']
            gsol.set_value(index=o, col=possibleProduct, value=1)
            i = i+1
            added = True
            budget = budget + channel.cost
            revenue = revenue + channel.factor*value_per_product[product]            
            break
    if not added:
        print("FINISH BUDGET")
        break
    
print(gsol.head())			

a = gsol[gsol.Mortgage == 1]
b = gsol[gsol.Pension == 1]
c = gsol[gsol.Savings == 1]

abc = gsol[(gsol.Mortgage == 1) | (gsol.Pension == 1) | (gsol.Savings == 1)]

print("Number of clients: %d" %len(abc))
print("Numbers of Mortgage offers: %d" %len(a))
print("Numbers of Pension offers: %d" %len(b))
print("Numbers of Savings offers: %d" %len(c))
print("Total Budget Spent: %d" %budget)
print("Total revenue: %d" %revenue)

data_kpis = [['Offers', len(abc)], ['Mortgage', len(a)], ['Pension', len(b)], ['Savings', len(c)], ['BudgetSpent', budget], ['Revenue', revenue]]

df_kpis = pd.DataFrame(columns=['kpi', 'value'], data=data_kpis)

outputs['kpis'] = df_kpis
outputs['solution'] = gsol
