import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"


data = [{'name': 'thousandeyes_68500.localdomain', 'agentId': '1325775', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-20', 'enabled': True}], 'toRemove': [{'testId': '5797202', 'testDescription': '2024-09-20', 'agents': []}]}, {'name': 'thousandeyes_68717.localdomain', 'agentId': '1325789', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-20', 'enabled': True}], 'toRemove': [{'testId': '4817136', 'testDescription': '2024-09-20', 'agents': [{'agentId': '1325792'}, {'agentId': '1364315'}]}]}, {'name': 'thousandeyes_68512.localdomain', 'agentId': '1325792', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-20', 'enabled': True}, {'testId': '5797205', 'testDescription': '2024-09-20', 'enabled': True}], 'toRemove': [{'testId': '4817136', 'testDescription': '2024-09-20', 'agents': [{'agentId': '1325789'}, {'agentId': '1364315'}]}, {'testId': '4161282', 'testDescription': '2024-09-19', 'agents': []}, {'testId': '4161283', 'testDescription': '2024-09-19', 'agents': []}]}, {'name': 'thousandeyes_68634.localdomain', 'agentId': '1364315', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-20', 'enabled': True}, {'testId': '5797205', 'testDescription': '2024-09-20', 'enabled': True}], 'toRemove': [{'testId': '4817136', 'testDescription': '2024-09-20', 'agents': [{'agentId': '1325789'}, {'agentId': '1325792'}]}]}]

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



#result = group_agents_by_test(data)
#print(result)



a_list = [{"agentId": "agentId1"}, {"agentId": "agentId2"}, {"agentId": "agentId3"}]

b_list = [{"agentId": "agentId4"}, {"agentId": "agentId5"}, {"agentId": "agentId6"}]

#print(a_list + b_list)


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

            # Si no hay agentes (caso de remover el test completo), agregamos el agente al 'remove_agents'
            if not test.get('agents'):
            
                grouped_tests[test_id]["remove_agents"].append({"agentId": agent['agentId']})

            # Si hay agentes específicos a remover, se agregan a la lista
            elif test.get('agents'):
            
                grouped_tests[test_id]["agents"].extend(test.get('agents'))

    return grouped_tests

result = clean_and_group_tests(data)
print(result)














def get_info(headers: dict, data: list):

    new_data = []

    print('+ get_info function \n')

    _, account_groups = get_data(headers=headers, endp_url=endp_url1, params={})

    if "accountGroups" in account_groups:

        agents_list = get_agents_list(data)
        
        for aid in account_groups['accountGroups']:
        
            print(f"\tGathering data for this ag: {aid.get('accountGroupName')}\n")

            full_target_list, full_tests_details = get_targets_test_list(data, headers, aid.get("aid"))  # getting the tests per ag and tests details

            status, agents = get_data(headers=headers, endp_url=endp_url2, params={"aid": aid.get("aid"), "agentTypes": "enterprise"})

            if "agents" in agents and status == 200:  
                 
                for agent in agents["agents"]:
                
                    if agent["agentName"] in agents_list:
                
                        print(f"\t----> {agent.get('agentName')} agent was found at {aid.get('accountGroupName')} \n")

                        new_agent = {"name":agent.get("agentName"), "agentId": agent.get("agentId"), "aid": aid.get("aid")}

                        tests_list = []
                        remove_tests = []
                        targets_list = get_targets_list(data, new_agent.get('name'))

                        for test in full_target_list: #list all the tests

                            for target_url in targets_list:
    
                                if test.get("url") == target_url:   
    
                                    tests_list.append({"testId": test.get("testId"), "testDescription": test.get("description"), "enabled": test.get("enabled")})

                                elif test.get("url") not in targets_list: ### Bertha already danced
                                
                                    for info in full_tests_details:
                                        
                                        platform_agents = []
                                        
                                        for platform_agent in info['agents']:
                                        
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


"""
#Adding workaround to scenario where test is disabled when it should not Sep 24th - lusarmie
                if  test["agents"] == []:

                    print(f"patching {test.get('agents')}")
                    for cvs_agent in cvs_agents:
                        
                        for agent_test in cvs_agent['tests']:
                            #We need to add the "new" agent to the list of agents on the test (previously not captured by get_info 
                            # due to the fact that the "new" agent was not configured yet)
                            if agent_test['testId'] == test["testId"]:
                                
                                test["agents"].append({"agentId": cvs_agent["agentId"]}) 
                                print(f"adding agent {cvs_agent['agentId']} in test {test['testId']}")
                    
"""












def intersection(lst1, lst2):
    
    lst3 = [value for value in lst1 if value in lst2]
    
    return lst3

def get_info(headers: dict, data: list):

    new_data = []

    print('+ get_info function \n')

    _, account_groups = get_data(headers=headers, endp_url=endp_url1, params={})

    if "accountGroups" in account_groups:

        agents_list = get_agents_list(data)
        
        for aid in account_groups['accountGroups']:
        
            print(f"\tGathering data for this ag: {aid.get('accountGroupName')}\n")

            #full_target_list contiene la lista de tests que apafecen por lo menos en un JSON
            #full_tests_details contiene la lista de tests de RXConnect donde ningún agente tiene que estar asignado
            full_target_list, full_tests_details = get_targets_test_list2(data, headers, aid.get("aid"))  # getting the tests per ag and tests details

            #Sacamos la lista de agentes que estan en registrados en el Account Group
            status, agents = get_data(headers=headers, endp_url=endp_url2, params={"aid": aid.get("aid"), "agentTypes": "enterprise"})

            if "agents" in agents and status == 200:  
                #Por cada agente registrado...
                for agent in agents["agents"]:
                    #Si este agente forma parte de la lista de agentes a actualizar...
                    if agent["agentName"] in agents_list:
                
                        print(f"\t----> {agent.get('agentName')} agent was found at {aid.get('accountGroupName')} \n")

                        new_agent = {"name":agent.get("agentName"), "agentId": agent.get("agentId"), "aid": aid.get("aid")}

                        tests_list = []
                        remove_tests = []
                        #Obtenemos la lista de urls donde tenemos que hacer actualizaciones para este agente en especifico....
                        targets_list = get_targets_list(data, new_agent.get('name'))

                        for test in full_target_list: #list all the tests found in JSON files -******************************
    
                            #Es este test parte de los tests donde se va a asignar al agent?
                            if test.get("url") in targets_list:
                                #Asignamos el test a tests_list, que posteriormente se usara para construir el diccionario del agente en turno
                                tests_list.append({"testId": test.get("testId"), "testDescription": test.get("description"), "enabled": test.get("enabled")})

                            #Si no es parte de los tests donde se va a asignar al agent... 
                            elif test.get("url") not in targets_list: ### Bertha already danced
                                continue
                        #Hay que validar si es parte de los tests donde el agente tiene que ser removido
                        tests2Remove = []
                        for test in full_target_list:
                            
                            if not test['url'] in targets_list:
                            
                                tests2Remove.append(test)
                        
                        tests2Remove.extend(full_tests_details)

                        for info in tests2Remove:
                                
                            platform_agents = []
                            
                            #Guardamos en platform_agents, la lista de agentes que actualmente está asignada al test
                            for platform_agent in info['agents']:
                                
                                platform_agents.append(platform_agent['agentId'])
                                
                            #Si el agente en turno está previamente asignado al test y además es el único, entonces no podemos removerlo, tenemos que deshabilitar el test
                            #pasamos "agents" como un arreglo vacío
                            if agent.get("agentId") in platform_agents and len(platform_agents) == 1:
                                
                                remove_tests.append({"testId": info.get("testId"), "testDescription": info.get("description"), "agents": []})
                            
                            #Si el agente en turno está previamente asignado al test y no es el único...
                            if agent.get("agentId") in platform_agents and len(platform_agents) > 1:
                                #Sacamos al agente en turno de la lista de agentes configurados en el test
                                platform_agents.remove(agent.get("agentId"))
                                new_agents = []
                                
                                #Y la lista actualizada, la agregamos al diccionario new_agents
                                for ag in platform_agents:
                                
                                    new_agents.append({"agentId": ag})
                                
                                #Con la información del testId y de los agents, construimos el diccionario que se usará más adelante en "toRemove"
                                remove_tests.append({"testId": info.get("testId"), "testDescription": info.get("description"), "agents": new_agents})

                        new_agent.update({"tests": tests_list, "toRemove": remove_tests})
                        
                        mergedList = []
                        for agentToUpdateData in new_data:
                            
                            if agentToUpdateData['name'] != new_agent['name']:
                            
                                if agentToUpdateData.get('toRemove'):
                            
                                    for testToRemove in agentToUpdateData.get('toRemove'):
                            
                                        for testToRemoveReference in new_agent.get('toRemove'):
                            
                                            if testToRemove['testId'] == testToRemoveReference['testId']:
                            
                                                mergedList = intersection(testToRemoveReference['agents'], testToRemove['agents'])
                                                testToRemoveReference['agents'] = mergedList
                                                testToRemove['agents'] = mergedList


                        new_data.append(new_agent)
                        #break
            
            else:
                
                continue
                        #print(f'Status code {status} test agents: {agent.get("agentName")} is not on the agents list \n ')

    return new_data