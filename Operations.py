import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"


def get_agents_list(data:list):

    agent_list = []
    for agent in data:

        if agent.get("name") not in agent_list:
        
            agent_list.append(agent.get("name"))

    return agent_list


def get_targets_list(data:list):

    target_list = []
    for target in data:

        urls = target.get("urls", [])

        for url in urls:
        
            if url not in target_list:
        
                target_list.append(url)

    return target_list



def get_info(headers: dict, data: list):

    new_data = []

    print('+ get_info function \n')

    _, account_groups = get_data(headers=headers, endp_url=endp_url1, params={})

    if "accountGroups" in account_groups:

        agents_list = get_agents_list(data)
        
        for aid in account_groups['accountGroups']:
        
            print(f"\tGathering data for this ag: {aid.get('accountGroupName')}\n")

            status, agents = get_data(headers=headers, endp_url=endp_url2, params={"aid": aid.get("aid"), "agentTypes": "enterprise"})

            if "agents" in agents and status == 200:      
                
                for agent in agents["agents"]:
                
                    if agent["agentName"] in agents_list:
                
                        print(f"\t----> {agent.get('agentName')} agent was found at {aid.get('accountGroupName')} \n")

                        new_agent = {"name":agent.get("agentName"), "agentId": agent.get("agentId"), "aid": aid.get("aid")}

                        status, tests = get_data(headers, endp_url3, params={"aid": aid.get("aid")})

                        if status == 200:

                            tests_list = []
                            remove_tests = []
                            targets_list = get_targets_list(data)

                            for test in tests["tests"]: #list all the tests
        
                                if test.get("url") in targets_list:
        
                                    tests_list.append({"testId": test.get("testId"), "testDescription": test.get("description"), "enabled": test.get("enabled")})

                                elif test.get("url") not in tests_list:
        
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

                            new_agent.update({"tests": tests_list, "toRemove": remove_tests})
                            new_data.append(new_agent)
                            #break

                
                    else:
                        continue
                        #print(f'Status code {status} test agents: {agent.get("agentName")} is not on the agents list \n ')

    return new_data


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


# Function to read all JSON files in a folder and return data from those modified today
def read_files_newer_only(directory_path: str) -> list:

    today = time.strftime('%Y-%m-%d')
    data_list = []  # List to store data from all files modified today

    for filename in os.listdir(directory_path):
    
        if filename.endswith('.json'):
    
            file_path = os.path.join(directory_path, filename)

            mod_time = os.path.getmtime(file_path)
            mod_time_str = time.strftime('%Y-%m-%d', time.localtime(mod_time))

            if mod_time_str == today:
    
                with open(file_path, 'r') as file:
    
                    data = json.load(file)
                    data_list.append(data)  # Add the data to the list

    if not data_list:
    
        print("No JSON files found or none modified today.")

    return data_list  # Return the list of data


def update_test_status(test_id: str, aid: str, agents: list, enabled: bool, headers: dict, description: str) -> tuple:
    """
    Helper function to update a test's status and agents.
    """
    url = f"{BASE_URL}tests/http-server/{test_id}?aid={aid}"
    payload = {
        "agents": agents,
        "enabled": enabled,
        "description": description
    }

    status, provision = put_data(headers, url, json.dumps(payload))

    if status == 200 or status == 201:
        action = "enabled" if enabled else "disabled"
        print(f"Test {test_id} was {action} successfully.")
    else:
        print(f"Test {test_id} could not be updated. Reason: {provision}")

    return status, provision



# NEW function to update the tests configuration
def update_tests(cvs_agents: list, headers: dict):
    """
    Function to enable tests and assign agents.
    """
    print('+ update_tests function \n')
    todays_date = datetime.now().strftime("%Y-%m-%d")

    for agent_data in cvs_agents:
        agent_id = agent_data.get("agentId")
        aid = agent_data.get("aid")
        agent_name = agent_data.get("name")

        for test in agent_data.get("tests", []):
            if not test.get("enabled"):
                # Enable the test and assign the agent
                agents = [{"agentId": agent_id}]
                status, provision = update_test_status(
                    test_id=test.get("testId"),
                    aid=aid,
                    agents=agents,
                    enabled=True,
                    headers=headers,
                    description=todays_date
                )

                if status == 200 or 201:
                    print(f"Test {test['testId']} enabled successfully and agent {agent_name} was assigned.")
                else:
                    print(f"Test {test['testId']} failed to enable. Reason: {provision}")
            else:
                print(f"Test {test['testId']} is already enabled for agent {agent_name}.")
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





