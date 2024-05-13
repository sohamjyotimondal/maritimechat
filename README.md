# MaritimeChat Workflow

MaritimeChat is an innovative application designed to provide maritime insights through a GraphQL endpoint. Its workflow is meticulously crafted to ensure a seamless and efficient user experience. Below is a detailed breakdown of the MaritimeChat workflow:

## User Query Processing

1. **Spelling Correction**: Upon receiving a user's query, the system first checks for spelling errors and automatically corrects them to enhance the accuracy of the query.

2. **Decomposition**: The corrected query is then decomposed into subparts. Each subpart represents a distinct request to be made to a specific endpoint. This decomposition process involves identifying:
   - The specific endpoint to query.
   - Any arguments required for the payload.
   - Relations to other subparts, if applicable.

## Data Gathering and JSON Structure

1. **JSON Structure**: A JSON structure is utilized to organize the plan for data gathering and processing. This structure serves as a blueprint for the system to follow.

2. **Data Availability Check**: The LangChain agent is responsible for checking whether all the required data for making requests is available within the JSON structure.

3. **User Prompt**: If any data is missing, the system intelligently prompts the user to provide the missing information. Once provided, this data is stored within the JSON structure, ensuring that all necessary components are in place for the next steps.

## Making Requests and Displaying Data

1. **Request Execution**: With the JSON structure now containing all necessary arguments and questions, the system proceeds to make requests to the specified endpoints.

2. **Data Compilation**: The compiled data from these requests is then processed and formatted into a user-friendly display.

This workflow ensures that MaritimeChat provides accurate, timely, and relevant maritime insights to its users, leveraging the power of GraphQL and intelligent data handling.
