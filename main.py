print("Sentron Firewall System Loading...")

def check_security(message):
    if "hack" in message.lower():
        return "BLOCK: Malicious intent detected!"
    else:
        return "ALLOW: Message is safe."

user_input = input("Enter AI Agent Message: ")
print(check_security(user_input))
