from Operations import read_files, get_info, agents2Tests, provision_agents, json_targets_func


def main(directory_path):

    print('GETTING JSON INFO ')
    cvs_agents, unassign_agents = read_files(directory_path)

    #func intermedia para get targets
    print('')
    print('GETTING JSON TARGETS ')
    json_targets = json_targets_func(cvs_agents)

    print('')
    print('GETTING ACCOUNTS INFO ')
    te_agents, te_tests = get_info(OAUTH="56f1454a-fc71-4245-a5a0-68bc93da1aaf", json_targets=json_targets, unassign_agents=unassign_agents) ## TOKEN
    

    print('')
    print('GETTING AGENTS AND TESTS RELATION ')
    te_tests = agents2Tests(te_tests, te_agents, cvs_agents)
    print("AGENTS2TESTS RELATION", te_tests)
    

    print('')
    print('PROVISION AGENTS STARTING')
    provisioning = provision_agents(te_tests, OAUTH="56f1454a-fc71-4245-a5a0-68bc93da1aaf")## TOKEN

    #return provisioning


print(main(directory_path="cvs_folder/"))


