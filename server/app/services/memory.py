from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    input_key="human_input",
    k=3,
)


def clear_memory():
    memory.clear()
