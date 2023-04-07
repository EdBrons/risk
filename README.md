# Abstract

Our project involves using reinforcement learning to create a some sort of agent that learns how to play the strategy boardgame Risk. In order to achieve our goals, we first implement a suitable environment that simulates the game and then we proceed to define the following components: the state space, action space, and a reward function so we train our agent with a reinforcement learning algorithm. To evaluate our success we could test our agent against different sorts of players, for instance testing it against a random player could serve as a baseline and we could later implement smarter players based on some basic strategies. Our ultimate goal is to have an agent that improves over time and is able to learn which strategies lead to victorious scenarios. 

# Motivation and Question

We were interested in diving deep into reinforcement learning as it truly resembles the way we actually learn: we act accordingly to stimuli we receive from our environment. Moreover, given that Risk is a non-deterministic game, that is, there is some element of randomness involved, we thought it would be interesting to see to what extent our agent is able to learn what are the "best strategies" of the game. Our main question is then, how well can a reinforcement learning algorithm work in Risk? 

# Planned Deliverables 

We will create the following: 
- An environment Python module that simulates the game of risk 
- A Python module to train the agent. 
- A Jupyter notebook showcasing our results 

We would also like to find a way to visualize the game (see the moves, the board, etc) so we can get a better sense of how the strategy works. However, we will attempt this only if we have time after training our agent and obtaining some results.

# Resources Required 

We will most likely need computing power to traing our models as it will involve neural networks. Therefore, we might require access to use Middlebury's HPC. 

# Learning Outcomes 

Eduardo: My main goal for the project is not only being able to implement and work on similar projects in the future, but also to understand the theory behind reinforcement learning. 

Ian: I would like to learn about creating environments for reinforcement learning as well as implmenting reinforcement learning algorithms.

# Risk Statement

There are some factors that could potentially stop us from achieving our goals, including implementing the algorithm wrongly, realizing that the problem is significantly harder than it seems or simply not having access to the required computing power. 

# Ethics Statement 

We are working on a harmless project that involves exploring reinforcement learning and how effective it could be in creating an aget that learns different strategies in a non-deterministic environment. The are no immediate effects on completing this project, it would just be a proof of concept that it is actually possible to achieve these things with reinforcement learning. 

# Tentative Timeline 

Before the first check we are planning to have some sort of reinforcement learning algorithm with some sort of strategy (probably not the best one). By Week 9-10 we hope to be in the process of improving and debugging our algorithm. 