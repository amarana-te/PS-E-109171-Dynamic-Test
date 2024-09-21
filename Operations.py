import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"


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


def get_agents_list(data:list):

    agent_list = []
    for agent in data:

        if agent.get("name") not in agent_list:
        
            agent_list.append(agent.get("name"))

    return agent_list


def get_targets_list(data:list, agent):

    for target in data:

        if target.get('name') == agent:
        
            return target.get('urls')
        

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
                            targets_list = get_targets_list(data, new_agent.get('name'))

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


def group_agents_by_test(data):
    target_urls = {}

    for agent in data:

        agent_id = agent['agentId']
        aid = agent['aid']
        
        # Proceso de pruebas habilitadas o deshabilitadas, omitiendo 'toRemove'
        for test in agent['tests']:
            
            test_id = test['testId']
            enabled = test['enabled']

            # Si el testId no existe, inicializamos
            if test_id not in target_urls:
                
                target_urls[test_id] = {"enabled": enabled, "agents": []}


            eas = {"agentId": agent_id}

            if eas not in target_urls[test_id]['agents']:
                
                
                target_urls[test_id]['agents'].append(eas)

    # Convertimos a la estructura requerida
    result = {
        "targetUrls": [
            {
                "testId": test_id,
                "aid": aid,
                "enabled": test_data['enabled'],
                "agents": test_data['agents']
            }
            for test_id, test_data in target_urls.items()
        ]
    }

    return result


def bulk_update(cvs_agents:list, headers:dict):

    todays_date = datetime.now().strftime("%Y-%m-%d")    
    print(f'+ update_tests function {todays_date} \n')

    tests_info =  group_agents_by_test(data=cvs_agents)

    for test in tests_info.get("targetUrls"):

        if not test.get("enabled"):

            url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={test.get('aid')}"
            payload = {"agents": test.get("agents"), "enabled": True, "description": todays_date}
                
            status, provision = put_data(headers, url, json.dumps(payload))

            if status == 200 or status == 201:

                print(f"\tTest {test['testId']} was enabled successfully and agents {len(test.get('agents'))} were assigned.")
        
            else:
        
                print(f"\tTest {test['testId']} failed to be enabled and agent {status} not assigned. Reason: {provision}")


        elif test.get("enabled"):

            url = f'{endp_url3}/{test.get("testId")}'    
            status, get_test_details = get_data(headers, url, params={"aid": test.get("aid"), "expand": "agent"})


            if status == 200 and "agents" in get_test_details:

                url = f'{endp_url3}/{test.get("testId")}?aid={test.get("aid")}'
                
                new_agents = []

                for agent in get_test_details.get("agents"):
        
                    new_agents.append({"agentId": agent.get("agentId")})

                new_agents = new_agents + test.get("agents")    
                payload = {"agents": new_agents, "enabled": True, "description": todays_date}
                status, provision = put_data(headers=headers, endp_url=url, payload=json.dumps(payload))


                if status == 200 or status == 201:
        
                    print(f"\tTest {test['testId']} updated successfully, {len(test.get('agents'))} agents were added.")
        
                else:
        
                    print(f"\tTest {test['testId']} couldn't be updated, no agent added to it. Reason: {provision}")


    return cvs_agents


def clean_and_group_tests(cvs_agents: list):
    
    # Diccionario para agrupar las pruebas por testId
    grouped_tests = {}

    for agent in cvs_agents:

        aid = agent.get('aid')
        
        for test in agent.get("toRemove", []):
            
            test_id = test.get('testId')

            # Inicializamos la agrupación si no existe
            if test_id not in grouped_tests:
            
                grouped_tests[test_id] = {
                    "aid": aid,
                    "agents": [],
                    "remove_agents": []
                }

            # Si hay agentes asociados al test, los agregamos a la lista
            if test.get("agents"):

                for agent_info in test.get("agents"):

                    if agent_info not in grouped_tests[test_id]["agents"]:

                        grouped_tests[test_id]["agents"].append(agent_info)
    

    return grouped_tests



def bulk_disable(cvs_agents:list, headers:dict):
    
    print('+ disable_tests function \n')

    grouped_tests = clean_and_group_tests(cvs_agents)
    
    for test_id, details in grouped_tests.items():
    
        url = f"{BASE_URL}tests/http-server/{test_id}?aid={details['aid']}"

        # Si hay agentes que remover, enviamos una actualización con los agentes a remover
        if not details['agents']:

            payload = {"enabled": False}
            status, provision = put_data(headers, url, json.dumps(payload))

            if status == 200 or status == 201:

                print(f"\tTest {test_id} was disabled. {provision}")
            
            else:

                print(f"\n\nTest {test_id} couldn't be disabled. Reason: {provision}")

        # Si hay agentes a actualizar, mandamos la lista de agentes
        if details['agents']:

            payload = {"enabled": True, "agents": details['agents']}
            
            status, provision = put_data(headers, url, json.dumps(payload))

            if status == 200 or status == 201:

                print(f"\tTest {test_id} was updated, {len(details['agents'])} agent(s) were unassigned from the Test.")

            else:

                print(f"\n\nTest {test_id} couldn't be updated. Reason: {provision}")





def disable_tests(cvs_agents:list, headers:dict):

    print('+ disable_tests function \n')

    for agent in cvs_agents:

        for test in agent.get("toRemove"):

            if not test.get('agents'):

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={agent.get('aid')}"
                payload = {"enabled": False}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

                    print(f"\tTest {test['testId']} was disabled, agent {agent.get('name')} 'removed' {provision}.")
                
                else:

                    print(f"\n\nTest {test['testId']} couln'd be disabled. Reason: {provision}")

            
            elif test.get('agents'):

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={agent.get('aid')}"
                payload = {"enabled": True, "agents":test.get('agents')}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

                    print(f"\tTest {test['testId']} was updated, {len(agent.get('name'))} agents totally removed from the test.")

                else:

                    print(f"\n\nTest {test['testId']} could't be updated, agent {agent('name')} still lives there. Reason: {provision}")





########Deprecated################################

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


def update_tests(cvs_agents: list, headers: dict):

    todays_date = datetime.now().strftime("%Y-%m-%d")    
    print(f'+ update_tests function {todays_date} \n')

    for info in cvs_agents:

        for test in info.get("tests"):

            if not test.get("enabled"):

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={info.get('aid')}"
                payload = {"agents": [{"agentId": info.get("agentId")}], "enabled": True, "description": todays_date}
                
                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:

        
                    print(f"\tTest {test['testId']} was enabled successfully and agent {info.get('name')} was assigned.")
        
                else:
        
                    print(f"\tTest {test['testId']} failed to be enabled and agent {status} not assigned. Reason: {provision}")


            elif test.get("enabled"):
        
                url = f'{endp_url3}/{test.get("testId")}'
                
                status, get_test_details = get_data(headers, url, params={"aid": info.get("aid"), "expand": "agent"})


                if status == 200 and "agents" in get_test_details:

                    url = f'{endp_url3}/{test.get("testId")}?aid={info.get("aid")}'
                
                    new_agents = []
                    new_agents.append({"agentId": info.get("agentId")})

                    for agent in get_test_details.get("agents"):
        
                        new_agents.append({"agentId": agent.get("agentId")})

                    
                    payload = {"agents": new_agents, "enabled": True, "description": todays_date}
                    status, provision = put_data(headers=headers, endp_url=url, payload=json.dumps(payload))


                    if status == 200 or status == 201:
        
                        print(f"\tTest {test['testId']} updated successfully, agent {info.get('name')} was added.")
        
                    else:
        
                        print(f"\tTest {test['testId']} couldn't be updated, no agent added to it. Reason: {provision}")

    return cvs_agents


