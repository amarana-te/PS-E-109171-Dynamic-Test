from Operations import read_files, get_info, agents2Tests, provision_agents, json_targets_func, clear_previous


def main(directory_path, OAUTH):

    print('GETTING JSON INFO ')
    cvs_agents, json_agents ,unassign_agents = read_files(directory_path)

    #func intermedia para get targets
    print('')
    print('GETTING JSON TARGETS ')
    json_targets = json_targets_func(cvs_agents)

    print('')
    print('GETTING ACCOUNTS INFO ')
    te_agents, te_tests, remove_agents = get_info(OAUTH=OAUTH, json_targets=json_targets, unassign_agents=unassign_agents, json_agents = json_agents) ## TOKEN


    print('')
    print('GETTING AGENTS AND TESTS RELATION ')
    te_tests = agents2Tests(te_tests, te_agents, cvs_agents)
    

    print('')
    print('PROVISION AGENTS STARTING')
    remove_agents = provision_agents(te_tests, remove_agents,OAUTH=OAUTH)## TOKEN


    print('')
    print('UNASSIGN AGENTS FROM PREVIOS RUN')
    remove_agents = clear_previous(remove_agents,OAUTH=OAUTH)## TOKEN




main(directory_path="cvs_folder/", OAUTH="56f1454a-fc71-4245-a5a0-68bc93da1aaf")


