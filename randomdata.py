import string
import secrets

# Generate random content
random_content = "".join(secrets.SystemRandom().choices(string.ascii_letters + string.digits, k=100))

# Write to a file
with open("example.txt", "w", encoding="utf-8") as file:
    file.write(random_content)
