# Full Code for LangChain Agent with Memory and Modular Design

from langchain.chat_models import ChatOpenAI
from langchain.agents import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor
from langchain.tools.render import format_tool_to_openai_function

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from typing import List, Dict, Any


def load_llm():
    """Load the LLM model."""
    return ChatOpenAI(temperature=0)

# Demo tools
@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


@tool
def add_numbers(nums: list) -> int:
    """Adds a list of numbers"""
    return sum(nums)


@tool
def well_arch_tool(query: str) -> Dict[str, Any]:
    """Returns text from AWS Well-Architected Framework releated to the query"""
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local("local_index", embeddings)
    docs = vectorstore.similarity_search(query)

    resp_json = {"docs": docs}

    return resp_json


tools = [well_arch_tool]


def create_agent_prompt():
    """Create the agent prompt with memory (chat_history) and return it."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You will always reference the AWS Well-Architected Framework when customers ask questions on building on AWS.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


def setup_agent(llm, tools, prompt):
    """Set up and return the agent with chat_history."""

    # Bind tools to LLM
    llm_with_tools = llm.bind(
        functions=[format_tool_to_openai_function(t) for t in tools]
    )

    # Create the agent with chat_history
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


def interact_with_agent(agent_executor, input_query, chat_history):
    """Interact with the agent and store chat history. Return the response."""
    # Get result from agent

    result = agent_executor.invoke({"input": input_query, "chat_history": chat_history})
    # Store the interaction in chat history
    chat_history.append(HumanMessage(content=input_query))
    chat_history.append(AIMessage(content=result["output"]))
    return result


def main():
    """Main function to run the tests."""

    # Setup
    llm = load_llm()
    prompt = create_agent_prompt()
    agent = setup_agent(llm, tools, prompt)
    chat_history = []

    # Test the agent with memory
    input1 = "How can I deploy secure VPCs?"
    response1 = interact_with_agent(agent, input1, chat_history)
    # print(response1)

    # Follow-up test referencing prior context
    # response2 = interact_with_agent(agent, "Whare are some sources to learn more?", chat_history)
    # print(response2)


# Run the main function
if __name__ == "__main__":
    main()
