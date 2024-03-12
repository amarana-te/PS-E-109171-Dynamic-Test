import os
import json
import time
from Connector import get_data, post_data

def get_info(OAUTH):
    headers = {
        'Authorization': 'Bearer ' + OAUTH,
        'Content-Type': 'application/json'
    }

    endp_url1 = "https://api.thousandeyes.com/v6/account-groups.json"
    endp_url2 = "https://api.thousandeyes.com/v6/agents.json"
    endp_url3 = "https://api.thousandeyes.com/v6/tests/http-server.json"

    account_groups = get_data(headers, endp_url1, params={})

    te_agents = {}
    te_tests = {}

    for aid in account_groups['accountGroups']:
        agents = get_data(headers, endp_url2, params={"aid": aid.get("aid"), "agentTypes": "ENTERPRISE_CLUSTER,ENTERPRISE"})

        if "agents" in agents:
            for agent in agents["agents"]:
                te_agents.update({agent.get("agentName"): [aid.get("aid"), agent.get("agentId")]})

        tests = get_data(headers, endp_url3, params={"aid": aid.get("aid")})

        if "test" in tests:
            for test in tests["test"]:
                endp_url4 = "https://api.thousandeyes.com/v6/tests/%s.json" % test.get("testId")
                test_details = get_data(headers, endp_url4, params={"aid": aid.get("aid")})
                te_tests.update({test.get("url"): [aid.get("aid"), test.get("testId"), []]})

    return te_agents, te_tests

def read_files(directory_path: str) -> list:
    agents = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                agents.append(data)
    return agents

def removeAgentFromTests(te_tests, te_agents, agent_to_remove):
    if agent_to_remove in te_agents:
        agent_id_to_remove = te_agents[agent_to_remove][1]
        for test_url, test_details in te_tests.items():
            if agent_id_to_remove in test_details[2]:
                test_details[2].remove(agent_id_to_remove)
    return te_tests

def provision_agents(te_tests, OAUTH):
    headers = {
        'Authorization': 'Bearer ' + OAUTH,
        'Content-Type': 'application/json'
    }

    for test_details in te_tests.values():
        test_id, account_id, agents = test_details[:3]

        url = f"https://api.thousandeyes.com/v6/tests/http-server/{test_id}/update.json?aid={account_id}"
        new_agents = [{"agentId": agent} for agent in agents] if agents else []

        payload = {"agents": new_agents, "enabled": bool(agents)}
        print(payload)
        response = post_data(headers, url, json.dumps(payload))


# Example usage, ensuring you replace 'OAUTH' with your actual OAuth token
# and adjust the directory path to your JSON files as needed.
if __name__ == "__main__":
    OAUTH = "56f1454a-fc71-4245-a5a0-68bc93da1aaf"
    directory_path = "cvs_folder/"

    te_agents, te_tests = get_info(OAUTH)
    cvs_agents = read_files(directory_path)
    agent_to_remove = "s00045app.stores.cvs.com"
    te_tests = removeAgentFromTests(te_tests, te_agents, agent_to_remove)
    provision_agents(te_tests, OAUTH)
