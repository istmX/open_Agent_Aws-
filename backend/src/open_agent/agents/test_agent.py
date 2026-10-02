from open_agent.agents.base import Agent

def test_agent_initialization() -> None:
    """Test the initialization of the Agent class."""
    agent_id = "test_agent"
    name = "Test Agent"
    role = "Test Role"
    llm_provider = None  

    agent = Agent(agent_id=agent_id, name=name, role=role, llm=llm_provider)

    assert agent.agent_id == agent_id
    assert agent.name == name
    assert agent.role == role
    assert agent.llm == llm_provider
    print("All tests passed for Agent class initialization.")
    print("Agent ID:", agent.agent_id)
    print("Agent Name:", agent.name)
    print("Agent Role:", agent.role)

test_agent_initialization()

