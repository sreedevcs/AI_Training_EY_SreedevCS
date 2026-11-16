from app.tools import tools
for tool in tools:
    print("Tool name: ",tool.name)
    print("Tool description: ",tool.description)
    print("Arguments: ",tool.args)
    print("-"*40)