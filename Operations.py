import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"

def get_info(headers:dict, data:dict):

    print('+ get_info function \n')
    
    _, account_groups = get_data(headers, endp_url1, params={})

    if "accountGroups" in account_groups:

        for aid in account_groups['accountGroups']:

            print(f"    Gathering data for this ag: {aid.get('accountGroupName')}\n")

        #print("AID: ", aid.get("aid"))
            status, agents = get_data(headers, endp_url2, params={"aid":aid.get("aid"), "agentTypes":"enterprise,enterprise-cluster"})

            if "agents" in agents and status == 200:

                for agent in agents["agents"]:

                    if agent["agentName"] == data.get("name"):

                        print(f"    ----> {data.get('name')} agent was found at {aid.get('accountGroupName')} \n")

                        data.update({"agentId":agent.get("agentId"), "aid":aid.get("aid")})

                        status, tests = get_data(headers, endp_url3, params={"aid":aid.get("aid")})

                        if status == 200:

                            tests_list = []
                            remove_tests = []

                            for test in tests["tests"]:
                    
                                if test.get("url") in data.get("urls") and data:


                                    tests_list.append({"testId":test.get("testId"), "testDescription": test.get("description"),"enabled":test.get("enabled")})

                                elif test.get("url") not in data.get("urls") and data:


                                    #consultar los gentes --- el agente por asignar, vive en este tests?
                                    details_endp = f'{BASE_URL}tests/http-server/{test.get("testId")}'
                                    params = {'aid':aid.get("aid"), 'expand':'agent'}
                                    status, test_details = get_data(headers=headers, endp_url=details_endp, params=params)


                                    if status == 200:

                                        platform_agents = []

                                        for platform_agent in test_details['agents']:

                                            platform_agents.append(platform_agent['agentId'])

                                        # si el agente vive en ese test:
                                        if agent.get("agentId") in platform_agents and len(platform_agents) == 1:

                                            #   Es el unico agente ahi? -- si si, tenemos que dejarlo y deshabilitar ese test
                                            remove_tests.append({"testId":test.get("testId"), "testDescription": test.get("description"), "agents": []}) ## validacion mas abajo: si no hay agentes, solo apaga el test

                                        if agent.get("agentId") in platform_agents and len(platform_agents) > 1:

                                            platform_agents.remove(agent.get("agentId"))
                                            
                                            new_agents = []

                                            for ag in platform_agents:
                                                
                                                new_agents.append({"agentId": ag})
                                            
                                            #   Si no es el unico agente, tenemos que updatear el test -- agents = agents - current_agent
                                            remove_tests.append({"testId":test.get("testId"), "testDescription": test.get("description"), "agents": new_agents})
                                            

                            data.update({"tests": tests_list, "toRemove": remove_tests})

                            break

                    elif agent["agentName"] != data.get("name"):

                        print(f'Agent Name from the .json file: {data.get("name")} was not found {agent["agentName"]} status {status} \n ')
                        print("===========================================================")

                    else:

                        print(f'Status code {status} test agents: {agent} \n ')
                        print("===========================================================")
                
    return data



# Function to read all JSON files in a folder
def read_files(directory_path: str) -> dict:

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        
        if filename.endswith('.json'):
            
            file_path = os.path.join(directory_path, filename)

            # Read and load the JSON data
            with open(file_path, 'r') as file:
                
                data = json.load(file)
                
            return data
        
        else:

            return {}


# Function to read all JSON files in a folder
def read_files_newer_only(directory_path: str) -> dict:
    # Get today's date in YYYY-MM-DD format
    today = time.strftime('%Y-%m-%d')

    for filename in os.listdir(directory_path):
        
        if filename.endswith('.json'):
            
            file_path = os.path.join(directory_path, filename)

            # Get the last modification time of the file
            mod_time = os.path.getmtime(file_path)
            mod_time_str = time.strftime('%Y-%m-%d', time.localtime(mod_time))
            
            # Check if the file was modified today
            if mod_time_str == today:
                # Read and return the JSON data
                with open(file_path, 'r') as file:
                
                    data = json.load(file)
                
                return data
            
            else:
                # File was modified on a different date
                return {}
    
    # If no JSON files are found or none are modified today, return an empty dictionary
    print("No JSON files found or none modified today.")
    return {}






# NEW function to update the tests configuration
def update_tests(cvs_agents:dict, headers:dict):

    print('+ update_tests function \n')

    todays_date = datetime.now().strftime("%Y-%m-%d")

    for test in cvs_agents.get("tests"):

        ## Si esta disable el test al que llegamos -- el unico agente que vivira ahi sera el de mi json
        if not test.get("enabled"):

            url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={cvs_agents.get('aid')}"
            payload = {"agents": [{"agentId": cvs_agents.get("agentId")}], "enabled": True, "description": todays_date}

            status, provision = put_data(headers, url, json.dumps(payload))

            if status == 200 or status == 201:

                print(f"    Test {test['testId']} was enabled successfully and agent {cvs_agents['name']} was assigned.")
            
            else:

                print(f"    Test {test['testId']} failed to be enabled and agent {cvs_agents['name']} not assigned. Reason: {provision}")


        # si el test esta enabled -- significa que los agentes de ahi son validos entonces me agrego
        elif test.get("enabled"):

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







################################
#           OLD FUNCTIONS 
################################

# OLD function to update the tests config 
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

