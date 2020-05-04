import math


class UpperConfidenceBound:
    def __init__(self, net_data):
        """
            UCB constructor
            :param net_data: list of all arms
        """
        self.arms_selected = []
        self.net_data = net_data
        self.num_of_arms = len(net_data)
        self.num_of_selections = [0] * self.num_of_arms
        self.sums_of_rewards = [0] * self.num_of_arms
        self.total_reward = 0
        self.num_tries = 0

    def choose_arm(self):
        """
            Selects the best arm from net_data.
            :return: Returns selected arm
        """
        arm = 0
        max_upper_bound = 0

        for i in range(0, self.num_of_arms):
            if self.num_of_selections[i] > 0:
                avg_reward = self.sums_of_rewards
                upper_bound = self._factor_importance_each_arm(self.num_of_selections[i], avg_reward)
            else:
                upper_bound = 1e400

            if upper_bound > max_upper_bound:
                max_upper_bound = upper_bound
                arm = i
        self.num_tries += 1
        self.arms_selected.append(arm)
        self.num_of_selections[arm] += 1
        chosen_arm = self.net_data[arm]
        reward = chosen_arm['rw']
        self.sums_of_rewards[arm] += reward
        self.total_reward += reward
        return chosen_arm

    def _factor_importance_each_arm(self, num_selections, avg_reward):
        """
            This method represents the core of the UCB algorithm.
            :param num_selections: number of selections for given arms
            :param avg_reward: average reward calculated from all previous rewards
            :return: An array with the importance of all arms.
        """
        exploration_factor = math.sqrt(2 * math.log(self.num_tries + 1) / num_selections)
        return avg_reward + exploration_factor

    def update_reward(self, sf, pw, rw):
        """
            This method updates a reward for a given arm.
        """
        i = 0
        for data in self.net_data:
            if data.sf == sf and data.pw == pw:
                self.net_data[i]['rw'] += rw
            i += 1

    def update_arms(self, net_data):
        self.net_data = net_data
