import random


class ThompsonSampling:
    def __init__(self, arms):
        """
        TS Constructor
        :param arms: list, list of arms
        """
        self.arms = arms

    def choose_arm(self):
        """
        Choose and arm base on alpha and bate values
        :return dict, selected arm as a dictionary
        """
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
            reward = self.arms[ad]

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
        #  return chosen_arm, ranked_arms

    def update_reward(self, chosen_arm, reward):
        """
        Update reward in arm
        :param chosen_arm: int, index of arm
        :param reward: int, reward increment or decrement
        :return void
        """
        self.arms[chosen_arm]['rw'] += reward
