import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def process_data(type_filter):
    df = pd.read_excel("responses.xlsx")
    # solo le righe della modalità desiderata
    df = df[df["Type"] == type_filter]
    # solo le colonne PSI
    df = df.iloc[:, 6:22]
    # reverse SOC
    df["Questo robot: [non ha capacità sociali]"] = 6 - df["Questo robot: [non ha capacità sociali]"]
    # reverse AC
    df["Questo robot: [ignora ciò che le persone pensano]"] = 6 - df["Questo robot: [ignora ciò che le persone pensano]"]
    # prendo le colonne SOC, AC, ...
    colonne_da_sommare = [(0, 4), (4, 8), (8, 12), (12, 16)]
    # somma le diverse scale
    for col in colonne_da_sommare:
        df[f'somma_{col[0]+1}_{col[1]}'] = df.iloc[:, col[0]:col[1]].sum(axis=1)
    # prendo solo le PSI
    colonne_nuove = df.filter(regex='somma_')
    colonne_nuove = colonne_nuove.div(4)
    # rinomina le colonne
    colonne_nuove.rename(columns={'somma_1_4': 'SOC', 'somma_5_8': 'AC', 'somma_9_12': 'PC', 'somma_13_16': 'RC'}, inplace=True)
    colonne_nuove['robot_type'] = type_filter

    return colonne_nuove

# per ogni modalità apre il file, somma le varie scale e fa la media
tom = process_data('Theory of Mind')
no_tom = process_data('No Theory of Mind')
deception = process_data('Deception')

# concatena le modalità per salvarle su file
data = pd.concat([tom, no_tom, deception])

# variabili PSI
variables = ['SOC', 'AC', 'PC', 'RC']

for variable in variables:
    # Plot
    fig, ax = plt.subplots()
    sns.violinplot(x='robot_type', y=variable, data=data)
    ax.set_xlabel("Condition")
    ax.set_ylabel("Value")
    plt.title(variable)
    fig.savefig("violin_" + variable + ".pdf")
    plt.close(fig)

# scrivo su file i risultati
with pd.ExcelWriter('PSI_results.xlsx') as writer:  
    data.to_excel(writer, sheet_name='PSI_scales')
    