import os
import json
from datetime import datetime
from Connector import get_data, post_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"

def get_info(headers:dict, data:dict):

    print('Get Info function')
    
    _, account_groups = get_data(headers, endp_url1, params={})

    if "accountGroups" in account_groups:

        for aid in account_groups['accountGroups']:

        #print("AID: ", aid.get("aid"))
            status, agents = get_data(headers, endp_url2, params={"aid":aid.get("aid"), "agentTypes":"enterprise,enterprise-cluster"})

            if "agents" in agents and status ==200:

                for agent in agents["agents"]:

                    if agent["agentName"] == data.get("name"):

                        data.update({"agentId":agent.get("agentId"), "aid":aid.get("aid")})

                        _, tests = get_data(headers, endp_url3, params={"aid":aid.get("aid")})

                        if "tests" in tests:

                            tests_list = []
                            remove_tests = []
                            for test in tests["tests"]:
                    
                                if test.get("url") in data.get("urls") and data.get:

                                    tests_list.append({"testId":test.get("testId"), "testDescription": test.get("description")})

                                elif test.get("url") not in data.get("urls") and data.get:

                                    remove_tests.append({"testId":test.get("testId"), "testDescription": test.get("description")})

                            data.update({"tests": tests_list, "toRemove": remove_tests})

                            break
                
    return data




# Function to read all JSON files in a folder
def read_files(directory_path: str) -> dict:

    for filename in os.listdir(directory_path):

        if filename.endswith('.json'):

            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'r') as file:
                
                data = json.load(file)
                
            return data
        
        else:

            return {}




def provision_agents(cvs_agents:dict, headers:dict):

    todays_date = datetime.now().strftime("%Y-%m-%d")

    for test in cvs_agents.get("tests"):

        ## si la fecha es none puede ser un nuevo test
        if not test.get("testDescription") or test.get("testDescription") != todays_date:

            url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={cvs_agents.get('aid')}"
            payload = {"agents": [{"agentId": cvs_agents.get("agentId")}], "enabled": True, "description": todays_date}

            status, provision = put_data(headers, url, json.dumps(payload))

            if status == 200 or status == 201:

                print(provision)


        elif test.get("testDescription") and test.get("testDescription") == todays_date:

            url = f'{endp_url3}/{test.get("testId")}' 
            status, get_test_details = get_data(headers, url, params={"aid":cvs_agents.get("aid"), "expand": "agent"})

            if status == 200 and "agents" in get_test_details:

                new_agents = []
                new_agents.append({"agentId": cvs_agents.get("agentId")})

                for agent in get_test_details.get("agents"):

                    new_agents.append({"agentId": agent.get("agentId")})

                payload = {"agents": new_agents, "enabled": True, "description": todays_date}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

                    print(todays_date, provision)


    return cvs_agents



def turn_off_tests(cvs_agents:dict, headers:dict):

    todays_date = datetime.now().strftime("%Y-%m-%d")

    if "toRemove" in cvs_agents:

        for test in cvs_agents.get("toRemove"):

            if not test.get("testDescription") or test.get("testDescription") != todays_date:

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={cvs_agents.get('aid')}"
                payload = {"enabled": False}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

                    print(provision)

