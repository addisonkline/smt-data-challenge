import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.stripplot(data=pd.read_csv('pickoff_data.csv'), x="runner_max_distance", y="pickoff_successful")
plt.title("Strip plot of runner distance")
plt.show()