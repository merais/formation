import airbyte as ab

res = ab.get_available_connectors()
print(res)