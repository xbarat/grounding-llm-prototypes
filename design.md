# high level design

## query processor 
""" it will take the user query and decompose it
            - data requirements
            - analysis requirements
"""
INPUT: user query (string)
OUTPUT: data requirements (endpoint, params), analysis requirements (dict)


## data pipeline ETL
""" it will take the data requirements and fetch the data from the source
            - data storage
            - data processing
            - data transformation
"""

## analysis engine
""" it will take the analysis requirements and generate the analysis code
            - analysis code generation
            - analysis code execution
"""

