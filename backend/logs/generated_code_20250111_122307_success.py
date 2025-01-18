# Query: Show Max Verstappen's race wins in 2023
# Generated at: 2025-01-11T12:23:07.727962
# Status: success

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Data processing
# Convert necessary columns to numeric
df['season'] = pd.to_numeric(df['season'], errors='coerce')
df['round'] = pd.to_numeric(df['round'], errors='coerce')
df['position'] = pd.to_numeric(df['position'], errors='coerce')
df['points'] = pd.to_numeric(df['points'], errors='coerce')

# Filter data for Max Verstappen's race wins in 2023
verstappen_wins_2023 = df[(df['season'] == 2023) & 
                          (df['driverName'] == 'Max Verstappen') & 
                          (df['position'] == 1)]

# Create visualization
plt.figure(figsize=(10, 6))
sns.barplot(data=verstappen_wins_2023, x='raceName', y='points', palette='viridis')
plt.title("Max Verstappen's Race Wins in 2023")
plt.xlabel('Race Name')
plt.ylabel('Points')
plt.xticks(rotation=45)
plt.tight_layout()

# Generate summary
num_wins = verstappen_wins_2023.shape[0]
output = f"Max Verstappen won {num_wins} races in the 2023 season."