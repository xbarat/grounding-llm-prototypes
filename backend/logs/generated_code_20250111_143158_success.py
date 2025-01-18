# Query: Show the points distribution for all drivers in the 2022 Miami Grand Prix
# Generated at: 2025-01-11T14:31:58.773009
# Status: success
# Data Type: driver_comparison


# Driver Performance Comparison
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os

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
plt.savefig(os.path.join('/Users/btsznh/giraffe/orbit-vi/backend/plots', f'driver_performance_{timestamp}.png'), bbox_inches='tight', dpi=300)
plt.close()
