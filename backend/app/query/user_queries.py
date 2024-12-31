# user_queries.py
def export_query_set(query_set, filename):
    """
    Exports the given query set to a text file.

    Parameters:
    query_set (list): The list of queries to export.
    filename (str): The name of the file to save the queries to.
    """
    with open(filename, 'w') as file:
        for query in query_set:
            file.write(f"{query[1]}\n")

# Example usage:
# export_query_set(query_set_1, 'query_set_1.txt')
# export_query_set(query_set_2, 'query_set_2.txt')
# export_query_set(query_set_3, 'query_set_3.txt')


# Query set 1: Driver career progression
query_set_1 = [
    # Driver career progression
    (101, "Show Max Verstappen's points progression from 2016 to 2023"),
    (102, "How has Lewis Hamilton's average finishing position changed from 2014 to 2023"),
    
    # Constructor performance
    (103, "Plot Red Bull's championship points from 2019 to 2023"),
    (104, "Compare Mercedes' race wins per season from 2014 to 2023"),
    
    # Season-by-season stats
    (105, "Show Fernando Alonso's podiums per season from 2018 to 2023"),
    (106, "What is Charles Leclerc's DNF rate each season from 2019 to 2023"),
    
    # Position trends
    (107, "Graph Lando Norris's average grid position by season from 2019 to 2023"),
    (108, "Show George Russell's points per race trend from 2020 to 2023")
]

query_set_2 = [
    (201, "How has Max Verstappen's rank changed across the last 10 seasons?"),
    (202, "How does Lewis Hamilton compare to Charles Leclerc in terms of wins, podiums, and points over the last 5 seasons?"),
    (203, "What is Fernando Alonso's performance (wins, fastest laps, podiums) on Circuit Silverstone over the past seasons?"),
    (204, "What were Sergio Pérez's key stats (wins, poles, fastest laps) for each season?"),
    (205, "What is Carlos Sainz Jr.'s average qualifying position across all races in a given season?"),
    (206, "How does Lando Norris perform in wet vs. dry conditions (wins, DNFs, lap times)?"),
    (207, "How does George Russell compare to his teammate in points, podiums, and wins for the last 3 seasons?"),
    (208, "How has Oscar Piastri performed in races with safety car interventions (positions gained/lost)?")
]

query_set_3 = [
    (209, "What is Valtteri Bottas's average lap time consistency across all races in a season?"),
    (210, "How often does Charles Leclerc finish in the top 5 after starting outside the top 10?"),
    (211, "How has Lewis Hamilton's rank changed across the last 10 seasons?"),
    (212, "How does Max Verstappen compare to Fernando Alonso in terms of wins, podiums, and points over the last 5 seasons?"),
    (213, "What is Lando Norris's performance (wins, fastest laps, podiums) on Circuit Monaco over the past seasons?"),
    (214, "What were George Russell's key stats (wins, poles, fastest laps) for each season?"),
    (215, "What is Oscar Piastri's average qualifying position across all races in a given season?"),
    (216, "How does Valtteri Bottas perform in wet vs. dry conditions (wins, DNFs, lap times)?"),
]