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

import sys
import docplex.mp

from docplex.mp.model import Model

mdl = Model(name="marketing_campaign", checker='on')


channelVars = mdl.binary_var_cube(offersR, productsR, channelsR)

# At most 1 product is offered to each customer
mdl.add_constraints( mdl.sum(channelVars[o,p,c] for p in productsR for c in channelsR) <=1
                   for o in offersR)

# Do not exceed the budget
mdl.add_constraint( mdl.sum(channelVars[o,p,c]*channels.get_value(index=c, col="cost") 
                                           for o in offersR 
                                           for p in productsR 
                                           for c in channelsR)  <= availableBudget, "budget")  

# At least 10% offers per channel
for c in channelsR:
    mdl.add_constraint(mdl.sum(channelVars[o,p,c] for p in productsR for o in offersR) >= len(offers) // 10)

mdl.print_information()

obj = 0

for c in channelsR:
    for p in productsR:
        product=products[p]
        coef = channels.get_value(index=c, col="factor") * value_per_product[product]
        obj += mdl.sum(channelVars[o,p,c] * coef* offers.get_value(index=o, col=product) for o in offersR)

mdl.maximize(obj)

mdl.parameters.timelimit = 30

s = mdl.solve()
assert s, "No Solution !!!"

print(mdl.get_solve_status())
print(mdl.get_solve_details())

totaloffers = mdl.sum(channelVars[o,p,c] 
                      for o in offersR
                      for p in productsR 
                      for c in channelsR)
mdl.add_kpi(totaloffers, "nb_offers")

budgetSpent = mdl.sum(channelVars[o,p,c]*channels.get_value(index=c, col="cost") 
                                           for o in offersR 
                                           for p in productsR 
                                           for c in channelsR)
mdl.add_kpi(budgetSpent, "budgetSpent")

for c in channelsR:
    channel = channels.get_value(index=c, col="name")
    kpi = mdl.sum(channelVars[o,p,c] for p in productsR for o in offersR)
    mdl.add_kpi(kpi, channel)

for p in productsR:
    product = products[p]
    kpi = mdl.sum(channelVars[o,p,c] for c in channelsR for o in offersR)
    mdl.add_kpi(kpi, product)
	
mdl.report()



data_kpis = [['Offers', mdl.kpi_value_by_name('nb_offers')], 
		['Mortgage', mdl.kpi_value_by_name('Mortgage')], 
		['Pension', mdl.kpi_value_by_name('Pension')], 
		['Savings', mdl.kpi_value_by_name('Savings')], 
		['BudgetSpent', mdl.kpi_value_by_name('budgetSpent')], 
		['Revenue', mdl.objective_value]]

df_kpis = pd.DataFrame(columns=['kpi', 'value'], data=data_kpis)

outputs['kpis'] = df_kpis