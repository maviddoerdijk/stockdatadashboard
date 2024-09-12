import pandas as pd

df = pd.read_excel('portfolio.xlsx')
print(df.head(n=100))

df['Portfolio Value'] = df['Portfolio Value'].replace(0, pd.NA)
df['Portfolio Value'] = df['Portfolio Value'].ffill()

print(df.head(n=100))