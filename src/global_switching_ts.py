class GlobalSwitchingTS:
    def __init__(self, arms):
        self.arms = arms
        print("Global Switching Thompson Sampling with Bayesian Aggregation")

    def choose_arm(self):
        """
            This method selects the best arm chosen by Thompsom Sampling.
            :return: Return selected arm number.
                    Arm number returned is (n_arm - 1).
                    Returns a list of arms by importance.
                    The chosen arm is the index 0 of this list.
        """
        rewards_0 = self.n_impressions - self.rewards
        rewards_0[rewards_0 <= 0] = 1
        theta_value = np.random.beta(self.rewards, rewards_0)
        ranked_arms = np.flip(np.argsort(theta_value), axis=0)
        chosen_arm = ranked_arms[0]
        self.n_impressions[chosen_arm] += 1

        return chosen_arm, ranked_arms

    def update_reward(self, chosen_arm):
        """
            This method gives a reward for a given arm.
            :param chosen_arm: Value returned from select().
        """
        self.rewards[chosen_arm] += 1
