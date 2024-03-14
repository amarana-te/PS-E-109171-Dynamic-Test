import os
import json
from Connector import get_data, post_data


def get_info(OAUTH, json_targets, unassign_agents, json_agents):

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
    remove_agents = {}



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
                        
                        #This condition is to unassign agents from another tests that had them assigned before the current run
                        if "/RxConnectRxP/" in test_details["test"][0]["url"] and agent.get("agentName") in json_agents:                    

                            if agent.get("agentId") in remove_agents:
                                remove_agents[agent.get("agentId")].insert(0, test_details["test"][0]["testId"])
                            else: 
                                remove_agents[agent.get("agentId")] = [test_details["test"][0]["testId"]]

                            if aid.get("aid") not in remove_agents[agent.get("agentId")]:
                                remove_agents[agent.get("agentId")].append(aid.get("aid"))
                            



                        # This conditions will unassign an agent from all the tests that contains an agent when the json looks like: {"name": "s02011app.stores.cvs.com","urls": [""]}
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

    return te_agents, te_tests, remove_agents




# Function to read all JSON files in a folder
def read_files(directory_path: str) -> list:

    json_data = []
    json_agents = []
    unassign_agents = []


    for filename in os.listdir(directory_path):

        if filename.endswith('.json'):
            print('Reading JSON file: ', filename)
            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'r') as file:
                
                data = json.load(file)

                if data["name"]:
                    json_data.append(data)
                    json_agents.append(data["name"])

                    if len(data["urls"]) == 1 and data["urls"][0] == "":
                        unassign_agents.append(data["name"])
                    
                    

                else:
                    print("This file does not have agents, it won't be considered. "+ filename)

                
    return json_data, json_agents, unassign_agents


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


def provision_agents(te_tests, remove_agents,OAUTH):

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

                    if agent in remove_agents:

                        for testid in remove_agents[agent]:

                            if testid == i[1]:

                                remove_agents[agent].remove(i[1]) ##lo quitamos de remove_agents porque no queremos que a ese test se le quite este agente

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

    return remove_agents


def clear_previous(remove_agents,OAUTH="56f1454a-fc71-4245-a5a0-68bc93da1aaf"):

    headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }


    for key, tests_list in remove_agents.items():
        
        for testid in tests_list[:-1]:

            unassign_flag = 0
            update_agents = []

            #delete that agent from that test
            #1. get details to see what are the agents it has assign
            endp_url4 = "https://api.thousandeyes.com/v6/tests/%s.json" % testid
            test_details = get_data(headers, endp_url4, params={"aid":tests_list[-1]})

            if "agents" in test_details["test"][0]:
                for agent in test_details["test"][0]["agents"]:

                    #if the agent is not the agent to unassign, then cosider it to push it back                        
                    if agent["agentId"] != key:
                        update_agents.append({"agentId": agent.get("agentId")})
                                
                    else:
                        print("Will unassign an agent ", agent.get("agentId"))
                        unassign_flag = 1
                            
                if unassign_flag == 1 and len(update_agents) > 0:

                    #update the agents
                    url = "https://api.thousandeyes.com/v6/tests/http-server/%s/update.json?aid=%s" % (testid, tests_list[-1])

                    payload = {"agents": update_agents, "enabled":1} #asgin agents and enable test                            
                    status_code = post_data(headers, endp_url=url, payload=json.dumps(payload))
                    print("For this test " + str(testid) + " An agent will be unassigned, not needed anymore. Account: "+ str(tests_list[-1]) +" Status code: "+ str(status_code))


                elif unassign_flag == 1 and len(update_agents) == 0:

                    #turnoff the test
                    url = "https://api.thousandeyes.com/v6/tests/http-server/%s/update.json?aid=%s" % (testid, tests_list[-1])

                    payload = {"enabled":0} #asgin agents and enable test                            
                    status_code = post_data(headers, endp_url=url, payload=json.dumps(payload))
                    print("Test disable, agents from previous run not required " + str(testid) + " Account group: "+ str(tests_list[-1]) + " Status code: "+ str(status_code))
        