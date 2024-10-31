import numpy as np
import random
import time
import gradio as gr
from multiprocessing import Process
import multiprocessing

# Parameters
opening_price = 10000
bottom_price = 5000

# Define the Q-learning agent
class QLearningAgent:
    def __init__(self, opening_price, bottom_price, q_table):
        self.q_table = q_table
        self.opening_price = opening_price
        self.bottom_price = bottom_price

    def get_state(self, price):
        return self.opening_price - price  # Inverse for index

    # def choose_action(self, state):
    #     return np.argmax(self.q_table[state])  # Always exploit in simulation
    def choose_action(self, state, epsilon=0.1):
        if random.random() < epsilon:
            return random.choice([0, 1, 2])  # Random action: accept, counter, reject
        return np.argmax(self.q_table[state])

# Load the Q-table from file
def load_q_table(filename):
    return np.load(filename)

# Define the negotiation response function
def negotiate(agent, customer_name, customer_offer):
    if customer_offer < bottom_price or customer_offer > opening_price:
        print(f"customer offer {customer_offer} -- Offer must be between {bottom_price} and {opening_price}.")
        return opening_price

    state = agent.get_state(opening_price)
    action = agent.choose_action(state)

    if action == 0:  # Accept
        print(f"Customer {customer_name} offer of {customer_offer} -- Agent accepts the offer of {customer_offer}.")
        return customer_offer
    else:  # Counter
        counter_offer = customer_offer + 100  # Counter higher
        if counter_offer > opening_price:
            print(f"Customer {customer_name} offer of {customer_offer} -- Agent counters with an offer of {opening_price}.")
            return opening_price
        else:
            print (f"Customer {customer_name} offer of {customer_offer} -- Agent counters with an offer of {counter_offer}.")
            return counter_offer


def negotiate_price(b, stop_event):
    q_table_filename = "q_table_seller.npy"

    # Load the Q-table and initialize the agent
    q_table = load_q_table(q_table_filename)
    agent = QLearningAgent(opening_price, bottom_price, q_table)
    offer = opening_price / 2

    money = dict(Buyer_1=12000, Buyer_2=15000)
    increase = dict(Buyer_1=50, Buyer_2=30)
    sleep = dict(Buyer_1=1.7, Buyer_2=1.5)

    con = False
    if money[b] > offer:
        con = True
    while con:
        if stop_event.is_set():
            print(f"\n>>>>>>>>>> Bicycle has been sold, negotiation is stop >>>>")
            con = False

        seller_offer = negotiate(agent=agent, customer_name=b, customer_offer=offer)
        if seller_offer == offer:
            print(f"\n>>>>>>>>>> Buyer {b} has a deal with price {offer}")
            con = False
            stop_event.set()
        print(seller_offer)
        offer = int(seller_offer) - increase[b]
        if offer > opening_price:
            print(f"\n>>>>>>>>>> Buyer {b} has a deal with price {offer}")
            con = False
            stop_event.set()
        time.sleep(sleep[b])



if __name__ == "__main__":
    stop_event = multiprocessing.Event()
    buyers = ["Buyer_1", "Buyer_2"]

    processes = []
    for buyer in buyers:
        process = Process(target=negotiate_price, args=(buyer, stop_event,))
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

