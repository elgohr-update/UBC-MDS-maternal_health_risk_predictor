# author: Lennon Au-Yeung
# date: 2022-11-25


""" Export eda from training data.
Usage: src/eda_script.py --data_location=<data_location> --output_location=<output_location>
Options:
--data_location=<data_location>    Location of the data to be used for eda
output_location=<output_location>  Location to output the visulisations
"""

from docopt import docopt
import altair as alt
import pandas as pd
import os
from altair_saver import save
import vl_convert as vlc
from sklearn.model_selection import train_test_split

opt = docopt(__doc__)

def main(data_location, output_location):

    maternal_risk_df = pd.read_csv(data_location)

    train_df, test_df = train_test_split(maternal_risk_df, test_size=0.2, random_state=123) 
    
    class_distribution = alt.Chart(train_df).mark_bar().encode(
        x = 'count()',
        y = 'RiskLevel',
        color = 'RiskLevel'
    ).properties(title = 'Distribution of Risk Level')


    def display(i):
        graph = alt.Chart(train_df).transform_density(
        i,groupby=['RiskLevel'],
        as_=[ i, 'density']).mark_area(fill = None, strokeWidth=2).encode(
        x = (i),
        y='density:Q',stroke='RiskLevel').properties(width=200,height=200)
        return graph + graph.mark_area(opacity = 0.3).encode(color = alt.Color('RiskLevel',legend=None))

    Age = display('Age')
    SystolicBP = display('SystolicBP')
    DiastolicBP = display('DiastolicBP')
    BS = display('BS')
    BodyTemp = display('BodyTemp')
    HeartRate = display('HeartRate')

    X_density = ((Age | SystolicBP | DiastolicBP) & (BS | BodyTemp | HeartRate)).properties(title='Distribution of Predictors for Each Risk Level')
    
    def boxplot(i):
        box = alt.Chart(train_df).mark_boxplot().encode(
        x = i,
        y = 'RiskLevel',
        color = 'RiskLevel'
    )
        return box
    
    Age = boxplot('Age')
    SystolicBP = boxplot('SystolicBP')
    DiastolicBP = boxplot('DiastolicBP')
    BS = boxplot('BS')
    BodyTemp = boxplot('BodyTemp')
    HeartRate = boxplot('HeartRate')
    
    X_box = (Age & SystolicBP & DiastolicBP & BS & BodyTemp & HeartRate).properties(title='Boxplots of Different Features')

    combined = (class_distribution & X_density & X_box).configure_title(
        fontSize=18, anchor='middle')

    X_corr = alt.Chart(train_df).mark_point(opacity=0.3, size=10).encode(
        alt.X(alt.repeat('row'), type='quantitative'),
        alt.Y(alt.repeat('column'), type='quantitative')
        ).properties(
            width=100,
            height=100
        ).repeat(
            column=['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate'],
            row=['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate'])
    
    def save_chart(chart, filename, scale_factor=1):
        if filename.split('.')[-1] == 'svg':
            with open(filename, "w") as f:
                f.write(vlc.vegalite_to_svg(chart.to_dict()))
        elif filename.split('.')[-1] == 'png':
            with open(filename, "wb") as f:
                f.write(vlc.vegalite_to_png(chart.to_dict(), scale=scale_factor))
        else:
            raise ValueError("Only svg and png formats are supported")
            
    try: 
        save_chart(combined, output_location+'EDA.png',1)
    except:
        os.makedirs(os.path.dirname(output_location+'EDA.png'))
        save_chart(combined, output_location+'EDA.png',1)
    
    save_chart(X_density, output_location+'density_plot.png',1)
    save_chart(X_box, output_location+'box_plot.png',1)
    save_chart(class_distribution, output_location+'class_distribution.png',1)
    save_chart(X_corr, output_location+'output_32_0.png',1)
        
    assert os.path.isfile(output_location+'EDA.png'), "EDA is not in the src/maternal_risk_eda_figures directory." 
    
if __name__ == "__main__":
  main(opt["--data_location"], opt["--output_location"])

#python src/eda_script.py --data_location='data/raw/maternal_risk.csv' --output_location='src/maternal_risk_eda_figures/'

#save_chart function reference from Joel Ostblom