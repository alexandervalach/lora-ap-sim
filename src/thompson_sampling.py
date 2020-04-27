import random
import lora

# Based on https://github.com/alison-carrera/mabalgs

class ThompsomSampling:
    def __init__(self, arms):
        self.arms = arms

    def choose_arm(self):
        N = 10000
        d = 10
        ads_selected = []
        numbers_of_reward_1 = [0] * d
        numbers_of_reward_0 = [0] * d
        total_reward = 0

        for n in range(0, len(self.arms)):
            ad = 0
            max_random = 0

            for i in range(0, d):
                random_beta = random.betavariate(numbers_of_reward_1[i] + 1, numbers_of_reward_0[i] + 1)
                if random_beta > max_random:
                    max_random = random_beta
                    ad = i

            ads_selected.append(ad)
            reward = dataset.values[n, ad]

            if reward == 1:
                numbers_of_reward_1[ad] = numbers_of_reward_1[ad] + 1
            else:
                numbers_of_reward_0[ad] = numbers_of_reward_0[ad] + 1

            total_reward = total_reward + reward

        # rewards_0 = self.n_impressions - self.rewards
        # rewards_0[rewards_0 <= 0] = 1
        # theta_value = np.random.beta(self.rewards, rewards_0)
        # ranked_arms = np.flip(np.argsort(theta_value), axis=0)
        # chosen_arm = ranked_arms[0]
        # self.n_impressions[chosen_arm] += 1
        # return chosen_arm, ranked_arms

    def update_reward(self, chosen_arm, reward):
        self.arms[chosen_arm]['reward'] += reward
