from Operations import read_files, get_info, agents2Tests, provision_agents


def main(directory_path):

    cvs_agents = read_files(directory_path)
    print('AGENTS ',cvs_agents)

    te_agents, te_tests = get_info(OAUTH="")

    te_tests = agents2Tests(te_tests, te_agents, cvs_agents)

    print('TEST LIST AT THE END',te_tests)

    provisioning = provision_agents(te_tests, OAUTH="")

    return provisioning


print(main(directory_path="cvs_folder/"))
