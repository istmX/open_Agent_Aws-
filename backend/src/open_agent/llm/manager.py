"""Multi-agent manager."""

from open_agent.agents.base import Agent


class AgentManager:
    """Manages multiple agents."""

    def __init__(self, agents: list[Agent] | None = None) -> None:
        """Initialize the agent manager."""

        self.agents = agents or []

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the manager."""

        if any(existing.agent_id == agent.agent_id for existing in self.agents):
            raise ValueError(
                f"Agent with ID {agent.agent_id} already exists."
            )

        self.agents.append(agent)

    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Retrieve an agent by its ID."""

        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent

        raise ValueError(f"Agent with ID {agent_id} not found.")

    def remove_agent_by_id(self, agent_id: str) -> None:
        """Remove an agent by its ID."""

        for index, agent in enumerate(self.agents):
            if agent.agent_id == agent_id:
                self.agents.pop(index)
                return

        raise ValueError(f"Agent with ID {agent_id} not found.")

    def list_agents(self) -> list[Agent]:
        """Return all registered agents."""

        return self.agents.copy()


# Test agents
agent1 = Agent(
    agent_id="1",
    name="Agent One",
    role="Role One",
    llm=None,
    tools=[],
)

agent2 = Agent(
    agent_id="2",
    name="Agent Two",
    role="Role Two",
    llm=None,
    tools=[],
)

agent3 = Agent(
    agent_id="3",
    name="Agent Three",
    role="Role Three",
    llm=None,
    tools=[],
)


# Create manager
manager = AgentManager()

# Add agents
manager.add_agent(agent1)
manager.add_agent(agent2)
manager.add_agent(agent3)



for agent in manager.list_agents():
    print(
        agent.agent_id,
        agent.name,
        agent.role,
        agent.llm,
        agent.tools,
    )




agent = manager.get_agent_by_id("2")

print(
    agent.agent_id,
    agent.name,
    agent.role,
)


print("\n=== REMOVE AGENT ===")

manager.remove_agent_by_id("2")

for agent in manager.list_agents():
    print(agent.agent_id, agent.name)