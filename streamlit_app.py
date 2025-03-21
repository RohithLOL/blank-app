import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit.components.v1 as components
from IPython.display import HTML, display

# Initial conditions
initial_population = 500  # Starting number of turtles
carrying_capacity = 2000  # Max turtles before they run out of space
generations = 100  # Number of steps in the simulation

# Temperature-related settings
optimal_temperature = 29  # Best temperature for balance

# Mortality and reproduction
maturity_age = 4  # Age at which females can reproduce
hatchling_survival_rate = 0.8  # 80% of baby turtles survive
adult_mortality_rate = 0.1  # 10% of adults die per generation
female_mortality_rate = 0.05  # Extra female deaths when it gets colder
male_mortality_rate_warm = 0.2  # Increased male mortality when it's warm
max_females_per_male = 10
average_eggs_per_female = 100


# Initial gender distribution
initial_males = initial_population // 2
initial_females = initial_population // 2

def get_female_ratio(temp, pivotal_temp=29.0, transition=0.5):
    """
    Determines the proportion of female hatchlings based on incubation temperature.
    
    Parameters:
    - temp: Incubation temperature (°C).
    - pivotal_temp: Temperature at which the sex ratio is 1:1.
    - transition: Controls the steepness of the transition from male to female.
    
    Returns:
    - Proportion of female hatchlings (0 to 1).
    """
    return 1 / (1 + np.exp(-transition * (temp - pivotal_temp)))


def logistic_growth(population):
    """Applies logistic growth to control population size."""
    return population * (1 - population / carrying_capacity)

def simulate_population(temp_range, cooling=False):
    males, females = initial_males, initial_females
    male_counts, female_counts, total_population = [males], [females], [males + females]

    for temp in temp_range:
        if males < 1 or females < 1:
            break

        female_ratio = get_female_ratio(temp)
        male_ratio = 1 - female_ratio

        mature_females = female_counts[-maturity_age] if len(female_counts) >= maturity_age else females

        # Ensure reproduction is based on the smaller population (males or mature females)
        reproducing_pairs = min(mature_females, males)

        # If reproducing pairs are very low, limit the number of offspring
        potential_offspring = reproducing_pairs * average_eggs_per_female
        surviving_offspring = int(potential_offspring * hatchling_survival_rate)

        # Apply the temperature-based sex ratio
        new_males = int(surviving_offspring * male_ratio)
        new_females = int(surviving_offspring * female_ratio)

        # If males drop below 5, severely limit new offspring (forcing collapse)
        if males <= 5:
            new_males = max(0, new_males // 2)  # Reduce male births
            new_females = max(0, new_females // 2)  # Reduce female births
            females = int(females * 0.85)  # Reduce female count directly

        # Apply mortality rates
        males = int(males * (1 - (male_mortality_rate_warm if not cooling else adult_mortality_rate)))
        females = int(females * (1 - adult_mortality_rate))

        if cooling:
            females = int(females * (1 - female_mortality_rate))

        # Add newborns
        males += new_males
        females += new_females

        # If there are no males left, remove females too
        if males == 0:
            females = 0

        # Apply carrying capacity constraints
        total = males + females
        if total > carrying_capacity:
            scale = carrying_capacity / total
            females = int(females * scale)
            males = int(males * scale)


        # Record population counts
        male_counts.append(males)
        female_counts.append(females)
        total_population.append(males + females)

    return temp_range[:len(male_counts)], male_counts, female_counts, total_population




# Define temperature changes
warming_temps = np.arange(29, 35, 0.1)  # Increasing temperature
cooling_temps = np.arange(29, 24, -0.1)  # Decreasing temperature

# Run simulations
temps_warm, males_warm, females_warm, total_warm = simulate_population(warming_temps)
temps_cool, males_cool, females_cool, total_cool = simulate_population(cooling_temps, cooling=True)

def animate_scenario(temps, males, females, total, title, color_male, color_female, color_total):
    """Creates an animation to show how the population changes over temperature."""
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Initialize plot lines for males, females, and total population
    line_males, = ax.plot([], [], color_male, label="Males", linewidth=2)
    line_females, = ax.plot([], [], color_female, label="Females", linewidth=2)
    line_total, = ax.plot([], [], color_total, label="Total Population", linewidth=2)

    # Set axis limits
    ax.set_xlim(min(temps), max(temps))
    ax.set_ylim(0, carrying_capacity + 100)
    
    # Labels and title
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Turtle Population")
    ax.set_title(title)
    
    # Legend and grid
    ax.legend()
    ax.grid()

    def init():
        """Initialize empty data for the animation."""
        line_males.set_data([], [])
        line_females.set_data([], [])
        line_total.set_data([], [])
        return line_males, line_females, line_total

    def update(frame):
        """Update the animation at each step."""
        line_males.set_data(temps[:frame], males[:frame])
        line_females.set_data(temps[:frame], females[:frame])
        line_total.set_data(temps[:frame], total[:frame])
        return line_males, line_females, line_total

    # Create animation
    ani = FuncAnimation(fig, update, frames=len(temps), init_func=init, interval=50, blit=False)
    
    return components.html(ani.to_jshtml(),width=2000, height=1000)  # Convert to HTML animation

st.subheader("🌍 What is Global Warming?")
st.text("Global warming refers to the long-term increase in Earth's average surface temperature due to human activities, primarily the burning of fossil fuels, which releases greenhouse gases like carbon dioxide into the atmosphere. This leads to climate changes such as more extreme temperatures, rising sea levels, and disruptions in ecosystems.")
st.text("")
st.subheader("🐢 The Issue: Temperature Affects Turtle Gender Ratio")
st.text("The sex of sea turtles is determined by the temperature of the sand during incubation. If the temperature is too high, more females are born; if it is too low, more males are born. With climate change causing temperature fluctuations, this can result in skewed populations with more females or more males, which affects the turtle population's ability to reproduce effectively.")
st.text("")
st.title("How does temperature affect gender birth rates?")
st.text("Temperature plays a crucial role in determining the gender of turtle hatchlings. Higher temperatures generally result in more female turtles, while lower temperatures lead to more males. However, this effect varies depending on the species, as some may exhibit the reverse pattern.")
st.text("")
st.title("💡 The Solution: Temperature Regulation System")
st.text("To address this issue, a solution has been proposed where a shade is placed over the beach to block excess heat, and heat scanners are used to monitor the temperature. If the temperature is too high, a misting system sprays water to cool the sand. If the temperature is too low, a heating system is activated to bring the temperature back to the ideal level, helping to balance the male-to-female ratio and maintain a healthy turtle population.")
st.text("")
st.title("How do turtles affect ecosystems and biodiversity?")
st.text("Turtles play a vital role in maintaining the balance of ecosystems. They regulate other species by consuming them, preventing overpopulation that could damage the ecosystem. Additionally, turtles serve as prey for other animals, supporting biodiversity. For instance, green sea turtles feed on seagrass, preventing it from growing excessively and suffocating itself. Preserving turtle populations is essential for maintaining healthy marine ecosystems.")
st.text("")


st.subheader("🔥 Warming Scenario:")

st.html(animate_scenario(
    temps_warm, males_warm, females_warm, total_warm, 
    "Warming Scenario: Turtle Population vs. Temperature", 
    'b-', 'r-', 'g-'
))

st.subheader("❄️ Cooling Scenario:")

st.html(animate_scenario(
    temps_cool, males_cool, females_cool, total_cool, 
    "Cooling Scenario: Turtle Population vs. Temperature", 
    'c-', 'm-', 'y-'
))