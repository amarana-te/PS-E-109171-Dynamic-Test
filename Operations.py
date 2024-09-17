import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"


def get_info(headers: dict, data: dict):

    found_flag = False

    print('+ get_info function \n')

    _, account_groups = get_data(headers=headers, endp_url=endp_url1, params={})

    if "accountGroups" in account_groups:
        
        for aid in account_groups['accountGroups']:
        
            print(f"    Gathering data for this ag: {aid.get('accountGroupName')}\n")

            status, agents = get_data(headers=headers, endp_url=endp_url2, params={"aid": aid.get("aid"), "agentTypes": "enterprise,enterprise-cluster"})

            if "agents" in agents and status == 200:
                
                for agent in agents["agents"]:
                
                    if agent["agentName"] == data.get("name"):
                
                        print(f"    ----> {data.get('name')} agent was found at {aid.get('accountGroupName')} \n")

                        data.update({"agentId": agent.get("agentId"), "aid": aid.get("aid")})

                        status, tests = get_data(headers, endp_url3, params={"aid": aid.get("aid")})

                        if status == 200:
                            tests_list = []
                            remove_tests = []

                            for test in tests["tests"]:
        
                                if test.get("url") in data.get("urls") and data:
        
                                    tests_list.append({"testId": test.get("testId"), "testDescription": test.get("description"), "enabled": test.get("enabled")})

                                    found_flag = True

                                elif test.get("url") not in data.get("urls") and data:
        
                                    details_endp = f'{BASE_URL}tests/http-server/{test.get("testId")}'
                                    params = {'aid': aid.get("aid"), 'expand': 'agent'}
        
                                    status, test_details = get_data(headers=headers, endp_url=details_endp, params=params)

                                    if status == 200:
        
                                        platform_agents = []

                                        if "agents" in test_details:
                                            
                                            for platform_agent in test_details['agents']:
                                            
                                                platform_agents.append(platform_agent['agentId'])

                                            if agent.get("agentId") in platform_agents and len(platform_agents) == 1:
                                            
                                                remove_tests.append({"testId": test.get("testId"), "testDescription": test.get("description"), "agents": []})

                                            if agent.get("agentId") in platform_agents and len(platform_agents) > 1:
                                            
                                                platform_agents.remove(agent.get("agentId"))

                                                new_agents = []
                                            
                                                for ag in platform_agents:
                                            
                                                    new_agents.append({"agentId": ag})

                                                remove_tests.append({"testId": test.get("testId"), "testDescription": test.get("description"), "agents": new_agents})

                            data.update({"tests": tests_list, "toRemove": remove_tests})
                            break

                    elif agent["agentName"] != data.get("name"):

                        pass
                
                    else:
        
                        print(f'Status code {status} test agents: {agent} \n ')

            if found_flag:
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


# Function to read all JSON files in a folder
def read_files_newer_only(directory_path: str) -> dict:
    
    today = time.strftime('%Y-%m-%d')

    for filename in os.listdir(directory_path):
        
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)

            mod_time = os.path.getmtime(file_path)
            mod_time_str = time.strftime('%Y-%m-%d', time.localtime(mod_time))

            if mod_time_str == today:
        
                with open(file_path, 'r') as file:
        
                    data = json.load(file)
        
                return data
        
            else:
        
                return {}

    print("No JSON files found or none modified today.")
    return {}


# NEW function to update the tests configuration
def update_tests(cvs_agents: dict, headers: dict):
    
    print('+ update_tests function \n')

    todays_date = datetime.now().strftime("%Y-%m-%d")

    for test in cvs_agents.get("tests"):
        
        if not test.get("enabled"):
        
            url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={cvs_agents.get('aid')}"
            payload = {"agents": [{"agentId": cvs_agents.get("agentId")}], "enabled": True, "description": todays_date}

            status, provision = put_data(headers, url, json.dumps(payload))

            if status == 200 or status == 201:
        
                print(f"    Test {test['testId']} was enabled successfully and agent {cvs_agents['name']} was assigned.")
        
            else:
        
                print(f"    Test {test['testId']} failed to be enabled and agent {cvs_agents['name']} not assigned. Reason: {provision}")


        elif test.get("enabled"):
        
            url = f'{endp_url3}/{test.get("testId")}'
            status, get_test_details = get_data(headers, url, params={"aid": cvs_agents.get("aid"), "expand": "agent"})


            if status == 200 and "agents" in get_test_details:

                url = f'{endp_url3}/{test.get("testId")}?aid={cvs_agents.get("aid")}'
        
                new_agents = []
                new_agents.append({"agentId": cvs_agents.get("agentId")})

                for agent in get_test_details.get("agents"):
        
                    new_agents.append({"agentId": agent.get("agentId")})

                payload = {"agents": new_agents, "enabled": True, "description": todays_date}

                status, provision = put_data(headers=headers, endp_url=url, payload=json.dumps(payload))


                if status == 200 or status == 201:
        
                    print(f"    Test {test['testId']} updated successfully, agent {cvs_agents['name']} was added.")
        
                else:
        
                    print(f"    Test {test['testId']} couldn't be updated, no agent added to it. Reason: {provision}")

    return cvs_agents



def disable_tests(cvs_agents:dict, headers:dict):

    print('+ disable_tests function \n')

    if "toRemove" in cvs_agents:

        for test in cvs_agents.get("toRemove"):

            if not test.get('agents'):

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={cvs_agents.get('aid')}"
                payload = {"enabled": False}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

                    print(f"    Test {test['testId']} was disabled, agent {cvs_agents['name']} 'removed'.")
                
                else:

                    print(f"    Test {test['testId']} couln'd be disabled. Reason: {provision}")
            
            elif test.get('agents'):

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={cvs_agents.get('aid')}"
                payload = {"enabled": True, "agents":test.get('agents')}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

                    print(f"    Test {test['testId']} was updated, agent {cvs_agents['name']} totally removed from the test.")

                else:

                    print(f"    Test {test['testId']} could't be updated, agent {cvs_agents['name']} still lives there. Reason: {provision}")





