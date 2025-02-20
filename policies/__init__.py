import gin

from policies import transformer_conditional_policy_pointer_rubik, vanilla_policy_rubik
from policies import transformer_conditional_policy_pointer_rush, vanilla_policy_rush
from policies.int import transformer_conditional_policy_pointer, vanilla_policy
from policies.sokoban.policy_baseline import SokobanPolicyBaseline


def configure_policy(policy_class):
    return gin.external_configurable(
        policy_class, module='policies'
    )


ConditionalPolicyINT = configure_policy(transformer_conditional_policy_pointer.ConditionalPolicyINT)
VanillaPolicyINT = configure_policy(vanilla_policy.VanillaPolicyINT)

ConditionalPolicyRubik = configure_policy(transformer_conditional_policy_pointer_rubik.ConditionalPolicyRubik)
VanillaPolicyRubik = configure_policy(vanilla_policy_rubik.VanillaPolicyRubik)

ConditionalPolicyRush = configure_policy(transformer_conditional_policy_pointer_rush.ConditionalPolicyRush)
VanillaPolicyRush = configure_policy(vanilla_policy_rush.VanillaPolicyRush)

SokobanPolicyBaseline = configure_policy(SokobanPolicyBaseline)
