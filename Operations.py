import os
import json
from Connector import get_data, post_data


def get_info(OAUTH):

    headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }

    endp_url1 = "https://api.thousandeyes.com/v6/account-groups.json"
    endp_url2 = "https://api.thousandeyes.com/v6/agents.json"
    endp_url3 = "https://api.thousandeyes.com/v6/tests/http-server.json"
    

    
    account_groups = get_data(headers, endp_url1, params={})

    te_agents = {}
    te_tests = {}

    for aid in account_groups['accountGroups']:

        #print("AID: ", aid.get("aid"))
        agents = get_data(headers, endp_url2, params={"aid":aid.get("aid"), "agentTypes":"ENTERPRISE_CLUSTER,ENTERPRISE"})

        if "agents" in agents:

            for agent in agents["agents"]:

                te_agents.update({agent.get("agentName"):[aid.get("aid"), agent.get("agentId")]})

        tests = get_data(headers, endp_url3, params={"aid":aid.get("aid")})

        if "test" in tests:

            for test in tests["test"]:

                endp_url4 = "https://api.thousandeyes.com/v6/tests/%s.json" % test.get("testId")
                test_details = get_data(headers, endp_url4, params={"aid":aid.get("aid")})

                # "Test URL" : [ testId, aid,[old agents],[agents para test]]
                te_tests.update({test.get("url"):[aid.get("aid"), test.get("testId"),[]]})

    #print(te_agents)
    #print(te_tests)

    return te_agents, te_tests




# Function to read all JSON files in a folder
def read_files(directory_path: str) -> list:

    agents = []

    for filename in os.listdir(directory_path):

        if filename.endswith('.json'):

            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'r') as file:
                
                data = json.load(file)
                agents.append(data)

    return agents


def agents2Tests(te_tests, te_agents, cvs_agents):

    for cvs_data in cvs_agents:

        for url in cvs_data["urls"]:

            if url not in te_tests:
                continue

            if cvs_data["name"] not in te_agents:
                continue

            te_tests[url][2].append(te_agents[cvs_data["name"]][1])


    return te_tests


def provision_agents(te_tests, OAUTH):

    headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }

    for i in te_tests.values():

        url = "https://api.thousandeyes.com/v6/tests/http-server/%s/update.json?aid=%s" % (i[1], i[0]) 

        agents = i[2]

        new_agents = []

        if agents:

            for agent in agents:

                new_agents.append({"agentId": agent})

            payload = {"agents": new_agents, "enabled": 1} #asgin agents and enable test
            
            print(post_data(headers, endp_url=url, payload=json.dumps(payload)))
        
        #if the test does not have any agents assigned to it
        else:
            
            payload = {"agents": [], "enabled": 0} #just disable the test
            
            print(post_data(headers, endp_url=url, payload=json.dumps(payload)))



