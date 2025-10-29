import matplotlib.pyplot as plt

# Data for the confirmation points
points = ['Essence-Only Fallback', 'Debounce After Edit', 'Patience Window']
statuses = ['Pending', 'Pending', 'Pending']  # Default status is 'Pending'

# Function to update the status of each point
def update_status(index, new_status):
    statuses[index] = new_status

# Function to plot the confirmation points
def plot_confirmation_points():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(points, [1, 1, 1], color=['orange' if status == 'Pending' else 'green' for status in statuses])
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title('Confirmation Points')

    # Annotate with current status
    for i, (point, status) in enumerate(zip(points, statuses)):
        ax.text(0.5, i, status, va='center', ha='center', color='white', fontweight='bold')
    
    plt.show()

# Initial plot
plot_confirmation_points()

# Example of updating statuses and re-plotting
# Uncomment these lines and run again to see the changes
# update_status(0, 'Confirmed')
# update_status(1, 'Confirmed')
# update_status(2, 'Confirmed')
# plot_confirmation_points()