import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import binom

df = pd.read_csv('pickoff_data.csv')
sns.stripplot(data=pd.read_csv('pickoff_data.csv'), x="runner_max_distance", y="pickoff_successful")
plt.title("Strip plot of runner distance")
plt.show()

short_distance_attempts = df.loc[df['runner_max_distance'] < 10.23]
size = short_distance_attempts.index.size
proportion = 70/374
successes = short_distance_attempts.loc[short_distance_attempts['pickoff_successful'] == 1].index.size
probability = binom.cdf(k=successes, n=size, p=proportion)
print(f'for 1st quartile: binom.cdf(successes = {successes}, n = {size}, p = {probability}) = {probability}')

short_med_distance_attempts = df.loc[(df['runner_max_distance'] > 10.23) & (df['runner_max_distance'] < 11.56)]
size = short_med_distance_attempts.index.size
proportion = 70/374
successes = short_med_distance_attempts.loc[short_med_distance_attempts['pickoff_successful'] == 1].index.size
probability = binom.cdf(k=successes, n=size, p=proportion)
print(f'for 2nd quartile: binom.cdf(successes = {successes}, n = {size}, p = {probability}) = {probability}')

long_med_distance_attempts = df.loc[(df['runner_max_distance'] > 11.56) & (df['runner_max_distance'] < 12.52)]
size = long_med_distance_attempts.index.size
proportion = 70/374
successes = long_med_distance_attempts.loc[long_med_distance_attempts['pickoff_successful'] == 1].index.size
probability = binom.cdf(k=successes, n=size, p=proportion)
print(f'for 3rd quartile: binom.cdf(successes = {successes}, n = {size}, p = {probability}) = {probability}')

long_distance_attempts = df.loc[df['runner_max_distance'] > 12.52]
size = long_distance_attempts.index.size
proportion = 70/374
successes = long_distance_attempts.loc[long_distance_attempts['pickoff_successful'] == 1].index.size
probability = binom.cdf(k=successes, n=size, p=proportion)
print(f'for 4th quartile: binom.cdf(successes = {successes}, n = {size}, p = {probability}) = {probability}')