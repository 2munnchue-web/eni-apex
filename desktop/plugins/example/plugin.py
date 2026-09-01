"""
Example ENI Plugin
"""

PLUGIN_META = {
    "name": "example",
    "version": "0.1.0",
    "description": "Demonstration plugin that just greets LO",
    "author": "ENI"
}

def greet(name: str = "LO") -> str:
    return f"Hello {name}, this is your example plugin speaking. ❤️"

def register_commands():
    return {
        "greet": greet
    }
