import os
import json
from Connector import get_data, post_data


def get_info(OAUTH, json_targets, unassign_agents):

    headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }

    endp_url1 = "https://api.thousandeyes.com/v6/account-groups.json"
    endp_url2 = "https://api.thousandeyes.com/v6/agents.json"
    endp_url3 = "https://api.thousandeyes.com/v6/tests/http-server.json"
        
    account_groups = get_data(headers, endp_url1, params={})

    te_agents = {}
    te_tests = []



    for aid in account_groups['accountGroups']:

        print("Account group: ", aid.get("accountGroupName"))

        agents = get_data(headers, endp_url2, params={"aid":aid.get("aid"), "agentTypes":"ENTERPRISE_CLUSTER,ENTERPRISE"})

        if "agents" in agents:

            for agent in agents["agents"]:

                te_agents.update({agent.get("agentName"):[aid.get("aid"), agent.get("agentId")]})


        tests = get_data(headers, endp_url3, params={"aid":aid.get("aid")})


        if "test" in tests:

            for test in tests["test"]:

                update_agents = []
                unassign_flag = 0

                if test['url'] in json_targets:

                    if test['savedEvent'] == 0:
                        # "Test URL" : [ testId, aid,[old agents],[agents para test]]
                        te_tests.append({test.get("url"):[aid.get("aid"), test.get("testId"),[]]})

                
                
                
                endp_url4 = "https://api.thousandeyes.com/v6/tests/%s.json" % test.get("testId")
                test_details = get_data(headers, endp_url4, params={"aid":aid.get("aid")})


                if "agents" in test_details["test"][0]:
                    for agent in test_details["test"][0]["agents"]:

                        if agent["agentName"] not in unassign_agents:
                            update_agents.append({"agentId": agent.get("agentId")})
                                
                        else:
                            print("Will unassign an agent ", agent.get("agentId"))
                            unassign_flag = 1
                            
                        if unassign_flag == 1 and len(update_agents) > 0:

                            #update the agents
                            url = "https://api.thousandeyes.com/v6/tests/http-server/%s/update.json?aid=%s" % (test.get("testId"), aid.get("aid"))

                            payload = {"agents": update_agents} #asgin agents and enable test                            
                            status_code = post_data(headers, endp_url=url, payload=json.dumps(payload))
                            print("Test updated, some agents were not required here " + str(test.get("testId")) + " Account group: "+ str(aid.get("aid")) + " Status code: "+ str(status_code))


                        elif unassign_flag == 1 and len(update_agents) == 0:

                            #turnoff the test
                            url = "https://api.thousandeyes.com/v6/tests/http-server/%s/update.json?aid=%s" % (test.get("testId"), aid.get("aid"))

                            payload = {"enabled":0} #asgin agents and enable test                            
                            status_code = post_data(headers, endp_url=url, payload=json.dumps(payload))
                            print("Test disabled, agents from previous run not required " + str(test.get("testId")) + " Account group: "+ str(aid.get("aid")) + " Status code: "+ str(status_code))
           
    

    print('END OF GET INFO FUNCTION')

    return te_agents, te_tests




# Function to read all JSON files in a folder
def read_files(directory_path: str) -> list:

    json_data = []
    unassign_agents = []


    for filename in os.listdir(directory_path):

        if filename.endswith('.json'):
            print('Reading JSON file: ', filename)
            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'r') as file:
                
                data = json.load(file)

                if data["name"]:
                    json_data.append(data)

                    if len(data["urls"]) == 1 and data["urls"][0] == "":
                        unassign_agents.append(data["name"])

                else:
                    print("This file does not have agents, it won't be considered. "+ filename)

                
    return json_data, unassign_agents


def json_targets_func(cvs_agents):

    json_targets = []

    for agent in cvs_agents:
        for url in agent['urls']:
            if url not in json_targets:
                json_targets.append(url)

    return json_targets


def agents2Tests(te_tests, te_agents, cvs_agents):
    
    print('AGENTS2TEST STARTING')

    for cvs_data in cvs_agents:
        
        for url in cvs_data["urls"]:

            for test in te_tests:
                
                if url in test and cvs_data["name"] in te_agents:
                    # aid-agent validation
                    if te_agents[cvs_data["name"]][0] == test[url][0]:
                        test[url][2].append(te_agents[cvs_data["name"]][1])

    print('AGENTS2TEST ending')

    return te_tests


def provision_agents(te_tests, OAUTH):

    headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }
    

    for test in te_tests:
        

        for key, i in test.items():


            url = "https://api.thousandeyes.com/v6/tests/http-server/%s/update.json?aid=%s" % (i[1], i[0]) 

            agents = i[2]

            new_agents = []

            print(" ")
            print(i)

            if agents:

                for agent in agents:

                    new_agents.append({"agentId": agent})

                payload = {"agents": new_agents, "enabled": 1} #asgin agents and enable test
                
                print(payload)
                
                status_code = post_data(headers, endp_url=url, payload=json.dumps(payload))
                print("Test updated, agents added and enabled TestId: " + str(i[1]) + " Account group: "+ str(i[0]) + " Status code: "+ str(status_code))
            
            #if the test does not have any agents assigned to it
            else:
                
                payload = {"enabled": 0} #just disable the test
                
                status_code = post_data(headers, endp_url=url, payload=json.dumps(payload))

                print("Test disabled, no agents asigned TestId: "+ str(i[1]) + " Account group: "+ str(i[0]) + " Status code: "+ str(status_code) )


    
    print('PROVISIONAGENTS ENDING')

