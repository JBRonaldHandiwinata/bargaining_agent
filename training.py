import numpy as np
import random
import pandas as pd

# Define the Q-learning agent
class QLearningAgent:
    def __init__(self, opening_price, bottom_price):
        self.q_table = np.zeros((opening_price - bottom_price + 1, 3)) * 0.1 # States for prices and actions
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 1.0
        self.exploration_decay = 0.99
        self.min_exploration_rate = 0.1
        self.opening_price = opening_price
        self.bottom_price = bottom_price

    def get_state(self, price):
        return self.opening_price - price  # Inverse for index

    def choose_action(self, state):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.randint(0, 2)  # Explore: return a random action
        else:
            return np.argmax(self.q_table[state])  # Exploit: return the action with max Q-value

    def update_q_table(self, state, action, reward, next_state):
        max_future_q = np.max(self.q_table[next_state])
        current_q = self.q_table[state][action]
        # Q-learning formula
        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (reward + self.discount_factor * max_future_q)
        self.q_table[state, action] = new_q

    def decay_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.exploration_rate, self.min_exploration_rate)

# Define the environment and training function
def train_agent(agent, episodes):
    for _ in range(episodes):
        customer_offer = random.randint(agent.bottom_price, agent.opening_price)
        # state = agent.get_state(agent.opening_price)
        state = agent.get_state(customer_offer)
        done = False

        while not done:
            action = agent.choose_action(state)
            # print("\n action {} -- state {} ".format(action, state))

            if action == 0:  # Accept
                reward = customer_offer - agent.opening_price
                done = True
                print(f"\nAgent accepts the price of {customer_offer}.")
            elif action == 1:  # Counter
                counter_offer = customer_offer + 100  # Counter higher
                if counter_offer > agent.opening_price:
                    reward = counter_offer - agent.opening_price
                    done = True
                else:
                    reward = -10  # Penalty for countering too low
                print("\n action {} -- state {} ".format(action, state))
                print(f" {customer_offer} Agent counters with a price of {counter_offer}.")
            else:  # Reject
                reward = -5  # Penalty for rejection
                done = True

            next_state = agent.get_state(agent.opening_price)
            agent.update_q_table(state, action, reward, next_state)
            state = next_state

        agent.decay_exploration_rate()

# Usage
opening_price = 10000
bottom_price = 5000
agent = QLearningAgent(opening_price, bottom_price)
train_agent(agent, episodes=10000000)

# Display the Q-table
print("Q-table:")
print(agent.q_table)
"""
Store Q-table
"""
np.save("q_table_seller.npy", agent.q_table)

df = pd.DataFrame(agent.q_table)
df.to_csv("q_table_seller.csv", index=False, header=["Accept", "Counter", "Reject"])
