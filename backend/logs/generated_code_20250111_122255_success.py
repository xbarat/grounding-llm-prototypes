# Query: Show the distribution of driver nationalities in 2023
# Generated at: 2025-01-11T12:22:55.299188
# Status: success

# Data processing
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Assuming df is the DataFrame containing the race data
# Check for missing values
df = df.dropna()

# Create visualization
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='nationality', order=df['nationality'].value_counts().index)
plt.title('Distribution of Driver Nationalities in 2023')
plt.xlabel('Nationality')
plt.ylabel('Number of Drivers')
plt.xticks(rotation=45)

# Generate summary
nationality_counts = df['nationality'].value_counts()
output = f"The distribution of driver nationalities in 2023 shows that the most common nationality is {nationality_counts.idxmax()} with {nationality_counts.max()} drivers."