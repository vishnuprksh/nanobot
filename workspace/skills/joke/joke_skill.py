#!/usr/bin/env python3
"""
Joke Skill - Tells random jokes to lighten the mood
"""

import random
from typing import Dict, Any

class JokeSkill:
    def __init__(self):
        self.jokes = {
            "programming": [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why did the developer go broke? Because he used up all his cache.",
                "What's a programmer's favorite hangout spot? The Foo Bar.",
                "Why do Java developers wear glasses? Because they can't C#.",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
                "Why was the JavaScript developer sad? Because he didn't know how to 'null' his feelings.",
                "What's the object-oriented way to become wealthy? Inheritance.",
                "Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25.",
                "What do you call a programmer from Finland? Nerdic.",
                "Why did the programmer quit his job? Because he didn't get arrays.",
            ],
            "dad_jokes": [
                "I'm reading a book on anti-gravity. It's impossible to put down!",
                "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
                "Why don't scientists trust atoms? Because they make up everything.",
                "I told my wife she was drawing her eyebrows too high. She looked surprised.",
                "What do you call a fake noodle? An impasta.",
                "Why did the scarecrow win an award? He was outstanding in his field.",
                "What do you call a bear with no teeth? A gummy bear.",
                "I used to be a baker, but I couldn't make enough dough.",
                "What do you call a sleeping dinosaur? A dino-snore.",
                "Why don't eggs tell jokes? They'd crack each other up.",
            ],
            "puns": [
                "I'm so good at sleeping, I can do it with my eyes closed.",
                "I'm trying to organize a hide and seek tournament, but it's really hard to find good players.",
                "I used to play piano by ear, but now I use my hands.",
                "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
                "I'm reading a book on the history of glue. I just can't seem to put it down.",
                "I used to be a baker, but I couldn't make enough dough.",
                "I'm on a seafood diet. I see food and I eat it.",
                "I used to hate facial hair, but then it grew on me.",
                "I'm so good at multitasking, I can waste time, be unproductive, and procrastinate all at once.",
                "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            ],
            "knock_knock": [
                "Knock knock. Who's there? Cow says. Cow says who? No, cow says moo!",
                "Knock knock. Who's there? Lettuce. Lettuce who? Lettuce in, it's cold out here!",
                "Knock knock. Who's there? Boo. Boo who? Don't cry, it's just a joke!",
                "Knock knock. Who's there? Tank. Tank who? You're welcome!",
                "Knock knock. Who's there? Olive. Olive who? Olive you and I miss you!",
            ]
        }
    
    def execute(self, command: str, context: Dict[str, Any] = None) -> str:
        """
        Execute the joke skill based on user command.
        """
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["joke", "laugh", "funny", "cheer", "humor"]):
            # Pick a random category
            category = random.choice(list(self.jokes.keys()))
            joke = random.choice(self.jokes[category])
            
            # Add some flavor text
            responses = [
                f"Here's a joke for you: {joke}",
                f"Hope this makes you smile: {joke}",
                f"Let me lighten the mood: {joke}",
                f"Try this one: {joke}"
            ]
            
            return random.choice(responses)
        
        return "I'm a joke skill! Ask me to 'tell a joke' or 'make me laugh'."

def main():
    """Test the joke skill"""
    skill = JokeSkill()
    print(skill.execute("tell me a joke"))
    print("\n---\n")
    print(skill.execute("make me laugh"))
    print("\n---\n")
    print(skill.execute("cheer me up"))

if __name__ == "__main__":
    main()