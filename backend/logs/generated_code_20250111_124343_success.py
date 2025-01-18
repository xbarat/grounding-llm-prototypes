# Query: Show Max Verstappen's race wins in 2023
# Generated at: 2025-01-11T12:43:43.105975
# Status: success
# Data Type: driver_comparison


# Driver Performance Comparison
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
sns.scatterplot(data=df, 
                x='round', 
                y='points',
                hue='driverName',
                style='driverName',
                s=100)
plt.title('Driver Points per Race')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Save the plot
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plt.savefig(f'plots/driver_performance_{timestamp}.png', bbox_inches='tight', dpi=300)
plt.close()
