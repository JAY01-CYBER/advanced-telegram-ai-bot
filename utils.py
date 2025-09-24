memory = {}

def save_message(chat_id, role, text):
    if chat_id not in memory:
        memory[chat_id] = []
    memory[chat_id].append({"role": role, "text": text})
    memory[chat_id] = memory[chat_id][-15:]  # Keep last 15 messages

def get_last_messages(chat_id):
    return memory.get(chat_id, [])
