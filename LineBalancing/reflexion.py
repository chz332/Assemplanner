from .linebalancing import LineBalancingAgent

class ReflexionWrapper:
    def __init__(self, model="gpt-4.1"):
        self.agent = LineBalancingAgent(model)

    def reflect(self, question, previous_answer) -> str:
        prompt = (
            "You just attempted to solve the following problem but your answer was incorrect.\n\n"
            f"[Question]\n{question}\n\n"
            f"[Your Answer]\n{previous_answer}\n\n"
            "Please briefly reflect on the reasons for failure and suggest strategies for improvement next time."
        )
        return self.agent.solve(prompt)