import json
import time
import traceback
from Operations import read_files_newer_only, get_info, bulk_update, bulk_disable, disable_tests

# Read the token from token.txt
with open('token.txt', 'r') as file:

    OAUTH = file.read().strip()  # Use strip() to remove any surrounding whitespace or newline characters

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/hal+json',
  'Authorization': 'Bearer ' + OAUTH
}

def main(directory_path):

    start_time = time.time()  # Record the start time
    
    try:
        cvs_agents = read_files_newer_only(directory_path)

        if not cvs_agents:

            print(f"No data found in the provided directory: {directory_path}. Please check if the directory contains valid JSON files.")
            return

        print(f'\n\tData gathered from {len(cvs_agents)} .json files')
        print("\n==========================================================")

        print('Parsing information New config will be pushed... \n')
        cvs_agents = get_info(headers, data=cvs_agents)
        
        if cvs_agents is None:
            
            print("Failed to retrieve information from the ThousandEyes API. Please check your connection and API credentials.")
            
            return

        print("===========================================================")
        print(f'This is the assignment information  \n\n{cvs_agents} \n')
        print("===========================================================\n")

        #cvs_agents = bulk_update(cvs_agents, headers)
        
        if cvs_agents:
            
            print("\nUpdated tests.")
        
        print("\n===========================================================")
        print('\n Unassign agents from previous run...\n')
        
        bulk_disable(cvs_agents, headers)

        print("\n===========================================================")

    except FileNotFoundError as e:
        
        print(f"Error: The directory or file was not found: {e}. Please provide a valid directory path.")
    
    except json.JSONDecodeError as e:
       
        print(f"Error: Failed to decode JSON data. Please check the input files for valid JSON format. Details: {e}")
    
    except TypeError as e:
        
        print(f"Error: An unexpected data type was encountered: {e}. Please check the data returned from the API and ensure it's in the expected format.")
    
    except Exception as e:
        
        print(f"An unexpected error occurred: {e}. Please check the logs for more details.")
        traceback.print_exc()

    finally:
        
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the total execution time
        
        print(f"Execution time: {execution_time:.2f} seconds")  # Print the execution time


if __name__ == "__main__":

    main(directory_path="cvs_folder/")
