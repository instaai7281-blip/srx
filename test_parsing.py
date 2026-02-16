import re

def test_parse(msg_link):
    # Simulate get_msg sanitization
    msg_link = msg_link.split("?")[0].rstrip("/")
    
    parts = msg_link.split("/")
    chat = None
    msg_id = None
    
    if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
        if 't.me/b/' in msg_link:
            chat = parts[-2]
            msg_id = int(parts[-1])
        else:
            try:
                c_index = parts.index('c')
                chat_raw = parts[c_index + 1]
                chat = int('-100' + chat_raw)
                msg_id = int(parts[-1])
            except (ValueError, IndexError) as e:
                return f"Error parsing private link: {e}"
    else:
        # Public link logic from get_msg else block
        try:
            chat = msg_link.split("t.me/")[1].split("/")[0]
            msg_id = int(msg_link.split("/")[-1])
        except (ValueError, IndexError) as e:
            return f"Error parsing public link: {e}"
            
    return f"Chat: {chat}, Msg ID: {msg_id}"

links = [
    "https://t.me/c/2242454156/495/521",
    "https://t.me/c/2242454156/521",
    "https://t.me/publicgroup/495/521",
    "https://t.me/publicgroup/521",
    "https://t.me/c/2242454156/495/521/",
    "https://t.me/c/2242454156/495/521?thread=495",
    "t.me/c/2242454156/495/521"
]

for l in links:
    print(f"Testing: {l}")
    print(f"Result: {test_parse(l)}")
    print("-" * 20)
