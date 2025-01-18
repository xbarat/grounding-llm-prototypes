# Query: Show the distribution of driver nationalities in 2023
# Generated at: 2025-01-11T12:42:33.460482
# Status: success
# Data Type: nationality_distribution


# Driver Nationality Distribution
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
nationality_counts = df['nationality'].value_counts()
sns.barplot(x=nationality_counts.index, 
            y=nationality_counts.values,
            palette='viridis')
plt.title('Driver Nationality Distribution')
plt.xticks(rotation=45)
plt.ylabel('Count')
plt.tight_layout()

# Add value labels on top of bars
for i, v in enumerate(nationality_counts.values):
    plt.text(i, v, str(v), ha='center', va='bottom')
