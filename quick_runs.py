import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"


data = [{'name': 'thousandeyes_68500.localdomain', 'agentId': '1325775', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797202', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '4817136', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797205', 'testDescription': '2024-09-19', 'enabled': True}], 'toRemove': [{'testId': '4161281', 'testDescription': '2024-09-19', 'agents': [{'agentId': '1325765'}, {'agentId': '1325767'}, {'agentId': '1362636'}]}, {'testId': '4161287', 'testDescription': '2024-09-19', 'agents': [{'agentId': '1325768'}]}]}, {'name': 'thousandeyes_68512.localdomain', 'agentId': '1325792', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797202', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '4817136', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797205', 'testDescription': '2024-09-19', 'enabled': True}], 'toRemove': [{'testId': '4161282', 'testDescription': '2024-09-19', 'agents': []}, {'testId': '4161283', 'testDescription': '2024-09-19', 'agents': []}]}, {'name': 'thousandeyes_68634.localdomain', 'agentId': '1364315', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797202', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '4817136', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797205', 'testDescription': '2024-09-19', 'enabled': True}], 'toRemove': []}]



def update_tests(cvs_agents: list, headers: dict):

    todays_date = datetime.now().strftime("%Y-%m-%d")    
    print(f'+ update_tests function {todays_date}\n')

    for agent in cvs_agents:

        for test in agent.get("tests"):

            if not test.get("enabled"):

                url = f"{BASE_URL}tests/http-server/{test.get('testId')}?aid={agent.get('aid')}"
                payload = {"agents": [{"agentId": agent.get("agentId")}], "enabled": True, "description": todays_date}

                status, provision = put_data(headers, url, json.dumps(payload))

                if status == 200 or status == 201:
        
                    print(f"\tTest {test['testId']} was enabled successfully and agent {agent.get('name')} was assigned.")
        
                else:
        
                    print(f"\tTest {test['testId']} failed to be enabled and agent {agent.get('name')} not assigned. Reason: {provision}")


            elif test.get("enabled"):
        
                url = f'{endp_url3}/{test.get("testId")}'
                
                status, get_test_details = get_data(headers, url, params={"aid": agent.get("aid"), "expand": "agent"})


                if status == 200 and "agents" in get_test_details:

                    url = f'{endp_url3}/{test.get("testId")}?aid={agent.get("aid")}'
                
                    new_agents = []
                    new_agents.append({"agentId": agent.get("agentId")})

                    for agent in get_test_details.get("agents"):
        
                        new_agents.append({"agentId": agent.get("agentId")})

                    
                    payload = {"agents": new_agents, "enabled": True, "description": todays_date}
                    status, provision = put_data(headers=headers, endp_url=url, payload=json.dumps(payload))


                    if status == 200 or status == 201:
        
                        print(f"\tTest {test['testId']} updated successfully, agent {agent.get('name')} was added.")
        
                    else:
        
                        print(f"\tTest {test['testId']} couldn't be updated, no agent added to it. Reason: {provision}")



print(update_tests(cvs_agents=data, headers={}))



"""if not test.get("enabled"):
        
            

        elif test.get("enabled"):
        
            url = f'{endp_url3}/{test.get("testId")}'
            print("tesit ", url)
            status, get_test_details = get_data(headers, url, params={"aid": cvs_agents.get("aid"), "expand": "agent"})


            if status == 200 and "agents" in get_test_details:

                url = f'{endp_url3}/{test.get("testId")}?aid={test.get("aid")}'
                
                new_agents = []
                new_agents.append({"agentId": test.get("agentId")})

                for agent in get_test_details.get("agents"):
        
                    new_agents.append({"agentId": agent.get("agentId")})

                payload = {"agents": new_agents, "enabled": True, "description": todays_date}

                status, provision = put_data(headers=headers, endp_url=url, payload=json.dumps(payload))


                if status == 200 or status == 201:
        
                    print(f"    Test {test['testId']} updated successfully, agent {test.get('agentName')} was added.")
        
                else:
        
                    print(f"    Test {test['testId']} couldn't be updated, no agent added to it. Reason: {provision}")

    return cvs_agents"""