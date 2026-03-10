# class Agent:
#     def __init__(self, system=""):
#         self.system = system
#         self.messages = []

#     def __call__(self, message):
#         # Προσθήκη του μηνύματος χρήστη στη λίστα
#         self.messages.append({"role": "user", "parts": [{"text": message}]})
#         result = self.execute()
#         # Προσθήκη της απάντησης του μοντέλου στη λίστα (για να θυμάται το context)
#         self.messages.append({"role": "model", "parts": [{"text": result}]})
#         return result

#     def execute(self):
#         # Ρύθμιση του μοντέλου με το system prompt και το temperature
#         config = types.GenerateContentConfig(
#             temperature=0.0,
#             system_instruction=self.system
#         )
        
#         completion = client.models.generate_content(
#             model="gemini-2.0-flash", # ή gemini-1.5-flash
#             contents=self.messages,
#             config=config
#         )
#         return completion.text

# def calculate(what):
#     return eval(what)

# def average_dog_weight(name):
#     if "Scottish Terrier" in name: 
#         return "Scottish Terriers average 20 lbs"
#     elif "Border Collie" in name:
#         return "a Border Collies average weight is 37 lbs"
#     elif "Toy Poodle" in name:
#         return "a toy poodles average weight is 7 lbs"
#     else:
#         return "An average dog weights 50 lbs"

# known_actions = {
#     "calculate": calculate,
#     "average_dog_weight": average_dog_weight
# }

# # Δοκιμή του Agent
# agent = Agent(system=prompt)
# result = agent("How much does a toy poodle weigh?")
# print(result)