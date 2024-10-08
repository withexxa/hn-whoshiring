from typing import List, Tuple
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from datetime import timedelta
from matplotlib.colors import LinearSegmentedColormap

from model import HNJobPosting



def analyze_seniority_levels(data: pd.DataFrame, force_normalize=False):

    def extract_seniority(seniority_str):
        if isinstance(seniority_str, str):
            return [level.strip() for level in seniority_str.strip('[]').replace("'", "").split(',')]
        return []


    # Apply the function to create a new column with lists of seniority levels
    data['seniority_list'] = data['seniority_level'].apply(extract_seniority)
    
    
    # Explode the dataframe so each seniority level gets its own row
    df_exploded = data.explode('seniority_list')
    # Remove "Unknown" from seniority levels
    df_exploded = df_exploded[df_exploded['seniority_list'] != 'Unknown']
    df_exploded = df_exploded[df_exploded['seniority_list'].notna()]

    categories = ["Junior", "Mid-level", "Senior", "Lead", "Manager", "Executive"]

    # Group by year and seniority level, then calculate proportions
    seniority_counts = df_exploded.groupby(['year', 'seniority_list']).size().unstack(fill_value=0).reindex(columns=categories, fill_value=0)
    seniority_proportions = seniority_counts.div(data.groupby('year').size(), axis=0)

    # Convert index to datetime for proper sorting
    try:
        seniority_proportions.index = pd.to_datetime(seniority_proportions.index + '-01')
    except:
        # trends.index = pd.to_datetime(trends.index + '-01-01')
        pass
    seniority_proportions = seniority_proportions.sort_index()
    
    if force_normalize:
        # Force normalization to ensure each row sums to 1
        row_sums = seniority_proportions.sum(axis=1)
        seniority_proportions = seniority_proportions.div(row_sums, axis=0).fillna(0)
    
    #color for each seniority level
    custom_colors = {
        'Junior': '#73d6ee',
        'Mid-level': '#0d3b66',
        'Senior': '#b8ffc6',
        'Lead': '#2dc48d',
        'Manager': '#1b7b3d',
        'Executive': 'black',
    }

    # Plot cumulative (stacked) area graph
    plt.figure(figsize=(12, 6))
    ax = seniority_proportions.plot.area(stacked=True, figsize=(12, 6), color=[custom_colors[cat] for cat in seniority_proportions.columns])
    normalized = "_normalized" if force_normalize else ""
    normalized_title = " Normalized" if force_normalize else ""
    
    # Format y-axis to show percentages
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

    plt.title(f'Cumulative Seniority Level Trend (2011-2024){normalized_title}')
    plt.xlabel('Date')
    plt.ylabel('Percentage of Seniority Levels')
    plt.legend(title='Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"seniority_levels_trend{normalized}.png")
    plt.close()


    # Print the first few rows of trends to understand its structure
    print(f"\nFirst few rows of seniority_levels_trends:")
    print(seniority_proportions.head())





def analyze_trends(monthly_data, column, categories, title, filename, force_normalize=False):
    # Calculate percentages for each category
    trends = monthly_data[column].apply(lambda x: x.value_counts(normalize=True, dropna=False))
    
    # Ensure all categories are present, fill missing with 0
    trends = trends.unstack(fill_value=0).reindex(columns=categories, fill_value=0)
    
    # Convert index to datetime for proper sorting
    try:
        trends.index = pd.to_datetime(trends.index + '-01')
    except:
        # trends.index = pd.to_datetime(trends.index + '-01-01')
        pass
    trends = trends.sort_index()
    
    if force_normalize:
        # Force normalization to ensure each row sums to 1
        row_sums = trends.sum(axis=1)
        trends = trends.div(row_sums, axis=0).fillna(0)

    #define custom colors for each category
    custom_colors = {
        'Unknown': '#D3D3D3',
        'Remote': '#0d3b66',
        'Hybrid': '#73d6ee',
        'In Person': '#b8ffc6',
        'full-time': 'purple',
        'part-time': 'orange',
        'contract': 'pink',
        'intern': '#1a67a5',
        'Junior': '#73d6ee',
        'Mid-level': '#0d3b66',
        'Senior': '#b8ffc6',
        'Lead': '#2dc48d',
        'Manager': '#1b7b3d',
        'Executive': 'black',
        'Bootstrapped': '#b8ffc6',
        'Pre-Seed': '#06dfc8',
        'Seed': '#0bbfbc',
        'Series A': '#119fb0',
        'Series B': '#213f8b',
        'Series C': '#271f7f',
        'Small': 'orange',
        'Medium': 'pink',
        'Large': 'brown',
        '$0-100k': '#b8ffc6',
        '$100k-120k': '#06dfc8',
        '$120k-140k': '#0bbfbc',
        '$140k-160k': '#119fb0',
        '$160k-180k': '#167fa3',
        '$180k-200k': '#1c5f97',
        '$200k-220k': '#213f8b',
        '$220k+': '#271f7f',
        'job-demand': 'red',
        'job-offer': 'blue'
    }
    
    # Plot cumulative (stacked) area graph
    plt.figure(figsize=(12, 6))
    ax = trends.plot.area(stacked=True, figsize=(12, 6), color=[custom_colors[cat] for cat in trends.columns])
    normalized = "_normalized" if force_normalize else ""
    normalized_title = " Normalized" if force_normalize else ""

    # Format y-axis to show percentages
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    
    plt.title(f'Cumulative {title} Trend (2011-2024){normalized_title}')
    plt.xlabel('Date')
    plt.ylabel('Percentage of Jobs Offers')
    plt.legend(title='Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{filename}_cumulative_trend{normalized}.png")
    plt.close()

    print(f"{title} categories: {', '.join(categories)}")

    # Print the first few rows of trends to understand its structure
    print(f"\nFirst few rows of {title.lower()}_trends:")
    print(trends.head())

    if force_normalize:
        print("\nForced normalization was applied.")

def analyze_remote_trends(monthly_data):
    categories = ['Remote', 'Hybrid', 'In Person', 'Unknown']
    analyze_trends(monthly_data, 'remote', categories, 'Remote Work', 'remote_work')

def analyze_compensation_trends(data):
    # Calculate average compensation for each group
    categories = ['$0-100k', '$100k-120k', '$120k-140k', '$140k-160k',
        '$160k-180k', '$180k-200k', '$200k-220k', '$220k+']
    data = data[data['year'] != 2011]
    yearly_data = data.groupby("year")
    
    analyze_trends(yearly_data, 'salary_category', categories, 'Salary Ranges', 'salary_ranges', force_normalize=False)

def analyze_job_demand_offer_trends(monthly_data):
    categories = ['job-demand', 'job-offer']
    analyze_trends(monthly_data, 'comment_status', categories, 'Job Demand vs Offer', 'job_demand_offer')

def analyze_visa_sponsoring(monthly_data):
    visa_trend = monthly_data['visa_sponsoring'].mean()
    plot_trend(list(visa_trend.items()), 'Visa Sponsoring Trend (2011-2024)', 'Percentage of Jobs Offering Visa Sponsorship', 'line')

def analyze_job_types(monthly_data):
    job_types = ['full-time', 'part-time', 'contract', 'intern']
    analyze_trends(monthly_data, 'job_type', job_types, 'Job Types', 'job_types')

def analyze_fundraising_round(data):
    yearly_data = data.groupby("year")
    fundraising_round = ['Bootstrapped', 'Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C']
    analyze_trends(yearly_data, 'fundraising_round', fundraising_round, 'Fundraising Round', 'fundraising_round')
    recent_data = data[data['year'] >= 2020]
    
    # Count total job offers
    total_offers = len(recent_data)

    # Count job offers for each fundraising round
    fundraising_counts = recent_data['fundraising_round'].value_counts()

    # Calculate percentages
    fundraising_percentages = (fundraising_counts / total_offers * 100).round(2)

    # Sort percentages in descending order
    fundraising_percentages_sorted = fundraising_percentages.sort_values(ascending=False)

    print("Percentage of job offers for each fundraising category since 2020:")
    for category, percentage in fundraising_percentages_sorted.items():
        print(f"{category}: {percentage}%")

def analyze_compensation(monthly_data):
    comp_min_trend = monthly_data['compensation_min'].apply(lambda x: x[x <= 1000].mean())
    comp_max_trend = monthly_data['compensation_max'].apply(lambda x: x[x <= 1000].mean())
    plot_trend(list(comp_min_trend.items()), 'Minimum Compensation Trend', 'Average Minimum Compensation (in thousands USD)','area ')
    plot_trend(list(comp_max_trend.items()), 'Maximum Compensation Trend', 'Average Maximum Compensation (in thousands USD)','area')

def analyze_company_sizes(monthly_data):
    sizes = ['Small', 'Medium', 'Large', 'Unknown']
    analyze_trends(monthly_data, 'company_size', sizes, 'Company Sizes', 'company_sizes')


def normalize_tech(tech):
        tech = tech.lower().strip()
        replacements = {
            'javascript': 'js', 'javascript (es6)': 'js', 'es6 javascript': 'js','vanilla javascript': 'js',
            'javascript/es6': 'js', 'javascript es6': 'js','frontend javascript': 'js',

            'typescript': 'ts', 'typescript 3.5': 'ts', 'typescript 3.6': 'ts', 'typescript 3.7': 'ts', 'typescript 3.8': 'ts',
            'typescript2': 'ts',
            
            'react.js': 'react','reactjs': 'react','react native': 'react','react-native': 'react',
            'react/redux': 'react','reactnative': 'react','react js': 'react','javascript/react': 'react',
            'react.js/flux':'react','react.js/redux':'react','react/react-native':'react','js/react':'react',
            'react/flux':'react','react 0.17':'react',

            'angularjs': 'angular','angular.js': 'angular','angular 2': 'angular','angular js': 'angular',
            'angular 2+': 'angular','angular2': 'angular','angular 1': 'angular','angular 8': 'angular',
            'angular 6': 'angular','angular 7': 'angular','angular 9': 'angular','angular 10': 'angular',
            'angular 4': 'angular','angular 5': 'angular','angular 1.x': 'angular','angular material': 'angular',
            'angular 2.0': 'angular','angular 2.x': 'angular','angular 6+': 'angular','angular 7+': 'angular',
            'angular 11': 'angular','angular 1.6': 'angular','angular 1.7': 'angular','angular 1.8': 'angular',

            'vue.js': 'vue','vuejs': 'vue','vue js': 'vue','vuex': 'vue','vue 3': 'vue','vue 2': 'vue',
            'vue3': 'vue','vue 1': 'vue','vue 0': 'vue','vue 1.x': 'vue','vue 2.x': 'vue',
            'vue/js': 'vue','vue2': 'vue','vue.js 3': 'vue','vue.js 2': 'vue','vue.js 1': 'vue',
            
            'sveltekit':'svelte','svelte 3':'svelte','svelte 2':'svelte','svelte 1':'svelte','svelte':'svelte',
            'svelte js':'svelte','svelte.js':'svelte','svelte.js 3':'svelte','svelte.js 2':'svelte','svelte.js 1':'svelte',
            
            'node.js': 'node','nodejs': 'node',

            'postgresql': 'postgres', 'postgressql': 'postgres', 'postgres rds': 'postgres',
            'postgres db': 'postgres', 'postgresdb': 'postgres', 'postgres/mysql': 'postgres',
            'rds postgres': 'postgres', 'postgre': 'postgres', 'postgres sql': 'postgres',
            'rds / postgresql': 'postgres', 'postgresql 9.4': 'postgres', 'postgresql 9.6': 'postgres',
            'postgresql 10': 'postgres', 'postgresql 11': 'postgres', 'postgresql 12': 'postgres',
            'postgresql 13': 'postgres', 'postgresql 14': 'postgres', 'postgresql 15': 'postgres',

            'mongo': 'mongodb', 'mongo db': 'mongodb','mongodb atlas': 'mongodb',
            'redis failover': 'redis', 'redis labs': 'redis',
            'golang': 'go',
            'ruby on rails': 'rails',

            'docker compose': 'docker', 'docker swarm': 'docker', 'docker/ecs': 'docker', 'docker-compose': 'docker',
            'docker/docker swarm': 'docker',

            'kubernetes': 'kubernetes', 'kubernets': 'kubernetes',

            'saltstack/terraform': 'terraform', 'terraform cdk': 'terraform', 'hashicorp stack (terraform': 'terraform',
            'hashicorp terraform': 'terraform',

            'jenkins ci': 'jenkins', 'ci/jenkins': 'jenkins', 'jenkins continuous integration': 'jenkins',
            'circle ci': 'circleci', 'circleci/mocha': 'circleci', 'circle-ci': 'circleci',

            'amazon web services': 'aws','aws lambda': 'aws','amazon aws': 'aws',
            'aws services': 'aws','aws ec2': 'aws','aws ecs': 'aws','amazon web services (aws)': 'aws',
            'aws cloud': 'aws','aws batch': 'aws','aws cloud services': 'aws','aws lambdas': 'aws',
            'aws serverless': 'aws','cloud iaas (aws)': 'aws','aws sagemaker': 'aws','aws sqs': 'aws','aws-serverless': 'aws',
            
            'azure devops': 'azure', 'microsoft azure': 'azure', 'azure cloud services': 'azure',
            'ms azure': 'azure', 'azure functions': 'azure','azuredevops': 'azure','azure devops': 'azure',
            'windows azure': 'azure','microsoft azure iaas': 'azure','microsoft azure paas': 'azure',

            'google cloud': 'gcp','google cloud platform': 'gcp','google cloud platform (gcp)': 'gcp',
            'google cloud functions': 'gcp','google cloud services': 'gcp','google cloud ml': 'gcp',
            'google cloud storage': 'gcp','google cloud/container engine': 'gcp',

            'cloudformation': 'aws cloudformation',
            'gitlab': 'gitlab ci',
            'travis': 'travis ci',
            'circle': 'circleci',

            'elasticsearch': 'elastic search', 'elastic': 'elastic search', 'elastic stack': 'elastic search',

            'algolia search': 'algolia',

            'html5': 'html',
            'css3': 'css', 
            
            'python3': 'python', 'python 3': 'python', 'python/django': 'python', 'python 3.6': 'python', 'python 2.7': 'python',
            'ipython': 'python', 'serverless python': 'python', 'python 3.9': 'python', 'python 3.8': 'python', 'python 3.7': 'python',
            'django/python': 'python',
            
            'tensorflow/caffe': 'tensorflow', 'tensorflow probability': 'tensorflow','tensorflow': 'tensorflow', 
            'tensorflow.js': 'tensorflow','smile/tensorflow': 'tensorflow','tensorflow & keras': 'tensorflow', 
            'tensorflow lite': 'tensorflow','tensorflow gpu': 'tensorflow','python/tensorflow': 'tensorflow',
            'tensorflow ii': 'tensorflow',
            
            'pytorch lightning': 'pytorch','python/pytorch': 'pytorch','pytorch geometric': 'pytorch',
            'torch/pytorch': 'pytorch'
        }
        return replacements.get(tech, tech)



def analyze_top_tech_stack(data, normalize_func=normalize_tech):

    yearly_data = data.groupby("year")

    #filter out 2024 data
    data_2024 = data[data['year'] == 2024]

    # Count NA values and empty lists
    na_count = sum(group['tech_stack'].isna().sum() for _, group in yearly_data)
    empty_list_count = sum((group['tech_stack'] == '[]').sum() for _, group in yearly_data)

    print(f"Number of NA values in tech_stack: {na_count}")
    print(f"Number of empty lists in tech_stack: {empty_list_count}")

    # Flatten and normalize all tech stacks
    #all_techs = [normalize_tech(tech.strip()) 
    #             for _, group in yearly_data
    #             for techs in group['tech_stack'].dropna() 
    #             for tech in techs.split(',') if tech.strip()]
    
    # Flatten and normalize tech stacks for 2024
    all_techs_2024 = [normalize_func(tech.strip()) 
                      for techs in data_2024['tech_stack'].dropna() 
                      for tech in techs.split(',') if tech.strip()]

    # Count occurrences and get top 20 technologies for 2024
    tech_counts_2024 = Counter(all_techs_2024)
    top_techs_2024 = [tech for tech, _ in tech_counts_2024.most_common(15)]

    # Prepare data for cumulative graph
    tech_trends = {tech: [] for tech in top_techs_2024}
    dates = []

    for date, group in yearly_data:
        # dates.append(pd.to_datetime(date + '-01'))
        dates.append(date)
        techs = group['tech_stack'].dropna().str.split(',').explode().apply(normalize_func)
        tech_counts = techs.value_counts()
        group_size = len(group)  # Number of entries in the group
        
        for tech in top_techs_2024:
            tech_trends[tech].append(tech_counts.get(tech, 0) / group_size)

     #color for each technology
    custom_colors = {
        'react': '#167288',
        'python': '#8cdaec',
        'ts': '#b45248',
        'postgres': '#d48c84',
        'aws': '#f58231',
        'go': '#d6cfa2',
        'node': '#3cb464',
        'kubernetes': '#9bddb1',
        'terraform': '#aaf0d1',
        'rust': '#643c6a',
        'js': '#836394',
        'java': '#a89a49',
        'docker': '#bfef45',
        'ruby': '#3cb44b',
        'django': '#4363d8',
        'redis': '#911eb4',
        'rails': '#f032e6',
        'c++': '#a9a9a9',
        'mysql': '#fabed4',
        'ruby on rails': '#fffac8',
        'linux': '#aaffc3',
        'php': '#dcbeff',
        'gcp': 'green',
        'azure': 'blue',
        'angular': 'red',
        'vue': 'green',
        'svelte': 'yellow',
    }

    # Plot cumulative (stacked) area graph
    plt.figure(figsize=(12, 6))
    
    # Convert tech_trends to a DataFrame for easier manipulation
    df_trends = pd.DataFrame(tech_trends, index=dates)
    
    # Create the stacked area plot
    ax = df_trends.plot.area(stacked=True, figsize=(12, 6), color=[custom_colors[cat] for cat in df_trends.columns])

    # Format y-axis to show percentages
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    
    plt.title('Cumulative 2024 Top 15 Technologies Trend')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Percentage of Jobs Mentioning Technologies')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("2024_top_15_technologies_cumulative_trend.png")
    plt.close()

    print(f"2024 top 15 technologies: {', '.join(top_techs_2024)}")


def analyze_tech_stack(data, tech_list, title, normalize_func=normalize_tech):

    yearly_data = data.groupby("year")

    # Prepare data for cumulative graph
    tech_trends = {tech: [] for tech in tech_list}
    dates = []

    for date, group in yearly_data:
        dates.append(date)
        techs = group['tech_stack'].dropna().str.split(',').explode().apply(normalize_func)
        tech_counts = techs.value_counts()
        group_size = len(group)  # Number of entries in the group
        
        for tech in tech_list:
            tech_trends[tech].append(tech_counts.get(tech, 0) / group_size)

    # Custom colors for DevOps technologies
    custom_colors = {
        'kubernetes': '#9bddb1','terraform': '#aaf0d1','docker': '#bfef45',
        'ansible': '#EE0000', 'chef': '#F09820', 'puppet': '#FFAE1A', 
        'jenkins': '#D33833', 'circleci': '#343434', 'gitlab ci': '#FCA121', 
        'travis ci': '#3EAAAF', 'aws cloudformation': '#FF9900', 'vagrant': '#1563FF',
        'hashicorp vault': '#000000', 'consul': '#F24C53', 'prometheus': '#E6522C', 
        'grafana': '#F46800', 'helm': '#0F1689',
        'aws': '#f58231', 'azure': 'blue', 'gcp': 'green',
        'react': '#167288', 'angular': 'red', 'vue': 'green', 'svelte': 'yellow'
    }

    # Plot cumulative (stacked) area graph
    plt.figure(figsize=(12, 6))
    
    # Convert tech_trends to a DataFrame for easier manipulation
    df_trends = pd.DataFrame(tech_trends, index=dates)

    # Plot cumulative (stacked) area graph
    ax = df_trends.plot.area(stacked=True, figsize=(12, 6), color=[custom_colors.get(cat, '#333333') for cat in df_trends.columns])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.title(f'Cumulative {title} Trend (2011-2024)')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Percentage of Jobs Mentioning Technologies')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{title}_cumulative_trend.png")
    plt.close()

    print(f"{title} technologies analyzed: {', '.join(tech_list)}")

    # Plot 100% stacked area graph
    plt.figure(figsize=(12, 6))
    df_percentage = df_trends.div(df_trends.sum(axis=1), axis=0)
    ax = df_percentage.plot.area(stacked=True, figsize=(12, 6), color=[custom_colors.get(cat, '#333333') for cat in df_percentage.columns])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    plt.title(f'Relative {title} Trend (100% Stacked)')
    plt.xlabel('Date')
    plt.ylabel('Relative Percentage of Jobs Mentioning Technologies')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{title}_technologies_relative_trend.png")
    plt.close()


def analyze_tech_monthly_trends(data, tech_list, title, normalize_func=normalize_tech):

    # Create a year-month column for easier grouping
    data['year_month'] = data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)

    # Sort by year-month
    data = data.sort_values('year_month')
    
    # Group by year-month
    monthly_data = data.groupby('year_month')
    
    # Prepare data for graph
    tech_trends = {tech: [] for tech in tech_list}
    dates = []

    for date, group in monthly_data:
        dates.append(pd.to_datetime(date + '-01'))
        techs = group['tech_stack'].dropna().str.split(',').explode().apply(normalize_func)
        tech_counts = techs.value_counts()
        group_size = len(group)  # Number of entries in the group
        
        for tech in tech_list:
            tech_trends[tech].append(tech_counts.get(tech, 0) / group_size)

    # Convert tech_trends to a DataFrame for easier manipulation
    df_trends = pd.DataFrame(tech_trends, index=dates)
    

    # Custom colors for technologies
    custom_colors = {
        'pytorch': '#0db7ed', 'tensorflow': '#326ce5',
        'aws': '#f58231','azure': 'blue','gcp': 'green',
        'react': '#167288', 'angular': 'red', 'vue': 'green', 'svelte': 'yellow',
        'postgre': 'blue', 'mongodb': 'green', 'redis': 'red', 
        'elastic search': 'purple', 'algolia': 'pink', 
        'kubernetes': '#9bddb1','terraform': '#aaf0d1','docker': '#bfef45',
    }

    # Plot line graph
    plt.figure(figsize=(12, 6))
    for tech in tech_list:
        plt.plot(dates, df_trends[tech], label=tech, color=custom_colors.get(tech, '#333333'), linewidth=2)
    
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Percentage of Jobs Mentioning Technology')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.tight_layout()

    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gcf().autofmt_xdate()  # Rotation
    
    plt.tight_layout()
    
    # Generate filename from title
    filename = title.lower().replace(' ', '_') + '_trend.png'
    plt.savefig(filename)
    plt.close()

    print(f"Plot saved as {filename}")


def analyze_tech_trends(data, tech_list, title, normalize_func=normalize_tech):

    yearly_data = data.groupby("year")
    
    # Prepare data for graph
    tech_trends = {tech: [] for tech in tech_list}
    dates = []

    for date, group in yearly_data:
        dates.append(date)
        techs = group['tech_stack'].dropna().str.split(',').explode().apply(normalize_func)
        tech_counts = techs.value_counts()
        group_size = len(group)  # Number of entries in the group
        
        for tech in tech_list:
            tech_trends[tech].append(tech_counts.get(tech, 0) / group_size)

    # Convert tech_trends to a DataFrame for easier manipulation
    df_trends = pd.DataFrame(tech_trends, index=dates)
    

    # Custom colors for technologies
    custom_colors = {
        'pytorch': '#0db7ed', 'tensorflow': '#326ce5',
        'aws': '#f58231','azure': 'blue','gcp': 'green',
        'react': '#167288', 'angular': 'red', 'vue': 'green', 'svelte': 'yellow',
        'postgres': '#d48c84', 'mongodb': '#4DB33D', 'redis': '#DC382D',
        'elastic search': 'purple', 'algolia': 'pink', 
        'kubernetes': '#9bddb1','terraform': '#aaf0d1','docker': '#bfef45', 
    }

    # Plot line graph
    plt.figure(figsize=(12, 6))
    for tech in tech_list:
        plt.plot(dates, df_trends[tech], 'o-', label=tech, color=custom_colors.get(tech, '#333333'), markersize=4, linewidth=2)

    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel('Percentage of Jobs Mentioning Technology')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.tight_layout()
    
    # Generate filename from title
    filename = title.lower().replace(' ', '_') + '_trend.png'
    plt.savefig(filename)
    plt.close()

    print(f"Plot saved as {filename}")

def analyze_all_tech_stack(csv_path: str = "HN_case_study_expanded.csv"):
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Helper function to normalize tech names
    def normalize_tech(tech):
        return tech.lower().strip()

    # Flatten and normalize all tech stacks
    all_techs = [normalize_tech(tech)
                 for techs in df['tech_stack'].dropna()
                 for tech in techs.split(',') if tech.strip()]

    # Count occurrences
    tech_counts = Counter(all_techs)

    # Create a DataFrame from the counter
    tech_df = pd.DataFrame.from_dict(tech_counts, orient='index', columns=['count'])
    tech_df.index.name = 'technology'
    tech_df = tech_df.sort_values(by='count', ascending=False)

    # Save to CSV
    tech_df.to_csv("all_technologies_count.csv")
    print("All technologies and their counts have been saved to all_technologies_count.csv")


def temporal_analysis(csv_path: str = "HN_case_study_expanded.csv"):
    # Read the CSV file
    df = pd.read_csv(csv_path)
        
    # Create a year-month column for easier grouping
    df['year_month'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    
    # Sort by year-month
    df = df.sort_values('year_month')


    df["average_compensation"] = (df["compensation_min"] + df["compensation_max"]) / 2
    # Define salary ranges
    salary_ranges = [
        (0, 100), (100, 120), (120, 140), (140, 160),
        (160, 180), (180, 200), (200, 220), (220, float('inf'))
    ]
    range_labels = [
        '$0-100k', '$100k-120k', '$120k-140k', '$140k-160k',
        '$160k-180k', '$180k-200k', '$200k-220k', '$220k+'
    ]

    # Categorize salaries
    def categorize_salary(avg_comp):
        for i, (lower, upper) in enumerate(salary_ranges):
            if lower <= avg_comp < upper:
                return range_labels[i]
        # return range_labels[-1]  # For salaries 220k+
    df["salary_category"] = df["average_compensation"].apply(categorize_salary)

    # Filter for job-offer comments only
    df_job_offers = df[df['comment_status'] == 'job-offer']
    # Remove entries for 2024-09 (not a complete month)
    df_job_offers = df_job_offers[df_job_offers['year_month'] != '2024-09']
    
    # Group by year-month
    monthly_data = df_job_offers.groupby('year_month')
    # Filter out months with less than 10 entries
    monthly_data = monthly_data.filter(lambda x: len(x) >= 10).groupby('year_month')

    # Only usefull if the job-offer filtering is not done in the previous step:
    analyze_job_demand_offer_trends(monthly_data)

    #Analyze different aspects
    analyze_top_countries(df_job_offers)
    analyze_remote_trends(monthly_data)
    analyze_job_types(monthly_data)  # Not very usefull, only fulltime
    analyze_seniority_levels(df_job_offers)
    analyze_fundraising_round(df_job_offers)
    analyze_visa_sponsoring(monthly_data)
    analyze_compensation_trends(df_job_offers)
    analyze_company_sizes(monthly_data)
    analyze_top_tech_stack(df_job_offers)
    plot_trend(list(monthly_data.size().items()), 'Job Postings Trend (2011-2024)', 'Number of Job Postings', 'line')

    # List of DevOps technologies to track
    devops_techs = [
        'docker', 'kubernetes', 'terraform', 'ansible', 'chef', 'puppet', 'jenkins',
        'circleci', 'gitlab ci', 'travis ci', 'aws cloudformation', 'vagrant',
        'hashicorp vault', 'consul', 'prometheus', 'grafana', 'helm'
    ]
    analyze_tech_stack(df_job_offers, devops_techs, "DevOps")

    # Pytorch vs. Tensorflow analysis
    ML_techs = ['pytorch', 'tensorflow']    
    analyze_tech_trends(df_job_offers, ML_techs, "Machine Learning Frameworks")
    #analyze_tech_monthly_trends(df_job_offers, ML_techs, "ML Frameworks")

    #Cloud providers analysis
    Cloud_techs = ['aws', 'azure', 'gcp']
    analyze_tech_stack(df_job_offers, Cloud_techs, "Cloud Providers")
    analyze_tech_trends(df_job_offers, Cloud_techs, "Cloud Providers")

    # Frontend frameworks analysis
    frontend_techs = ['react', 'angular', 'vue', 'svelte']
    analyze_tech_stack(df_job_offers, frontend_techs, "Frontend Frameworks")
    analyze_tech_trends(df_job_offers, frontend_techs, "Frontend Frameworks")

    # Database analysis
    database_tech = ['postgres', 'mongodb', 'redis']
    analyze_tech_trends(df_job_offers, database_tech, "Database")

    #search analysis
    search_tech = ['elastic search', 'algolia']
    analyze_tech_trends(df_job_offers, search_tech, "Search")

    #DevOps tools battle
    devops_tools = ['kubernetes', 'terraform', 'docker']
    analyze_tech_trends(df_job_offers, devops_tools, "DevOps Tools")

    # Calculate the number of job postings per year
    numerical_analysis(df_job_offers)


 
 
def numerical_analysis(df_job_offers: pd.DataFrame):

    job_postings_per_year = df_job_offers.groupby('year').size().reset_index(name='count')
    print("Number of Job Postings per Year:")
    for _, row in job_postings_per_year.iterrows():
        print(f"{row['year']}: {row['count']}")
    

    visa_proportion_per_year = df_job_offers[['visa_sponsoring', 'year']].groupby('year').mean()
    mean_2011_2019 = visa_proportion_per_year.loc[2011:2019, 'visa_sponsoring'].mean()
    mean_2021_2024 = visa_proportion_per_year.loc[2021:2024, 'visa_sponsoring'].mean()
    print(f"Mean visa proportion from 2011 to 2019: {mean_2011_2019}")
    print(f"Mean visa proportion from 2021 to 2024: {mean_2021_2024}")

    remote_per_year = df_job_offers[['remote', 'year']].groupby('year').value_counts(normalize=True)
    print(remote_per_year)
    remote_2023_2024 = remote_per_year.loc[2023:2024]
    total_remote_2023_2024 = remote_2023_2024.sum()
    remote_and_hybrid_2023_2024 = remote_2023_2024.xs('Remote', level="remote") + remote_2023_2024.xs('Hybrid', level="remote")
    proportion_remote_2023_2024 = remote_and_hybrid_2023_2024.sum() / total_remote_2023_2024.sum()
    print(f"Proportion of remote jobs in 2023-2024: {proportion_remote_2023_2024}")

    def extract_seniority(seniority_str):
        if isinstance(seniority_str, str):
            return [level.strip() for level in seniority_str.strip('[]').replace("'", "").split(',')]
        return []

    # Apply the function to create a new column with lists of seniority levels
    df_job_offers['seniority_list'] = df_job_offers['seniority_level'].apply(extract_seniority)

    # Explode the dataframe so each seniority level gets its own row
    df_exploded = df_job_offers.explode('seniority_list')

    # Group by year and seniority level, then calculate proportions
    seniority_counts = df_exploded.groupby(['year', 'seniority_list']).size().unstack(fill_value=0)
    seniority_proportions = seniority_counts.div(df_job_offers.groupby('year').size(), axis=0)
    
    print("Seniority Level Counts per Year:")
    print(seniority_counts)
    print("Seniority Level Proportions per Year:")
    print(seniority_proportions)

    # Calculate average compensation
    df_job_offers['average_compensation'] = (df_job_offers['compensation_min'] + df_job_offers['compensation_max']) / 2

    # Filter out rows where average_compensation is NaN
    df_job_offers_with_comp = df_job_offers.dropna(subset=['average_compensation'])
    # Remove values above 1000
    df_job_offers_with_comp = df_job_offers_with_comp[df_job_offers_with_comp['average_compensation'] <= 1000]

    # Calculate and print the overall average compensation
    overall_avg_comp = df_job_offers_with_comp['average_compensation'].mean()
    print(f"Overall average compensation: ${overall_avg_comp:.2f}")

    # Calculate and print the average compensation per year
    yearly_avg_comp = df_job_offers_with_comp.groupby('year')['average_compensation'].mean()
    print("\nAverage compensation per year:")
    for year, avg_comp in yearly_avg_comp.items():
        print(f"{year}: ${avg_comp:.2f}")

    fundraising_round_yearly = df_job_offers.groupby(['year', 'fundraising_round']).size().unstack(fill_value=0)
    fundraising_round_yearly_proportions = fundraising_round_yearly.div(df_job_offers.groupby('year').size(), axis=0)
    print(fundraising_round_yearly_proportions)


def analyze_top_countries(df: pd.DataFrame):
    def parse_countries(countries):
        if isinstance(countries, str):
            # Split by comma and strip whitespace
            return [country.strip() for country in countries.split(',')]
        elif isinstance(countries, list):
            return countries
        else:
            return []  # Return empty list for unexpected types

    def normalize_country_code(country):
        # Normalize UK to GB
        return 'UK' if country == 'GB' else country

    # Flatten the countries list and normalize
    all_countries = [
        normalize_country_code(country)
        for countries in df['countries'].dropna() 
        for country in parse_countries(countries)
    ]
    
    # Count occurrences
    country_counts = Counter(all_countries)
    
    # Get the top 10 countries
    top_10_countries = country_counts.most_common(10)
    
    # Create a DataFrame
    top_countries_df = pd.DataFrame(top_10_countries, columns=['Country', 'Count'])
    
    # Sort by count in descending order
    top_countries_df = top_countries_df.sort_values('Count', ascending=False)
    
    # Save to CSV
    top_countries_df.to_csv("top_10_countries.csv", index=False)
    print("Top 10 countries have been saved to top_10_countries.csv")
    
    # Create a bar plot
    plt.figure(figsize=(12, 6))
    plt.bar(top_countries_df['Country'], top_countries_df['Count'])
    plt.title('Top 10 Countries in Job Postings (2011-2024)')
    plt.xlabel('Country')
    plt.ylabel('Number of Job Postings')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("top_10_countries_plot.png")
    plt.close()
    print("Bar plot of top 10 countries has been saved to top_10_countries_plot.png")


def plot_trend(data: List[Tuple[str, float]], title: str, ylabel: str, plot_type: str):
    dates = [pd.to_datetime(date + '-01') for date, _ in data]
    values = [value for _, value in data]
    
    plt.figure(figsize=(12, 6))
    
    # Create the filled area plot
    #plt.fill_between(dates, values, alpha=0.7)  # alpha controls the transparency
    
    if plot_type == "area":
        plt.fill_between(dates, values, alpha=0.7)  # alpha controls the transparency
    elif plot_type == "line":
        # Create a simple line plot with dots
        plt.plot(dates, values, 'o-', color='purple', markersize=4, linewidth=1.5)
    
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Format y-axis as percentage
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    
    # Add a subtle line on top of the filled area for better visibility
    plt.plot(dates, values, color='black', linewidth=0.5)
    
    plt.savefig(f"{title.lower().replace(' ', '_')}.png")
    plt.close()


def plot_trend_chartbar(data: List[Tuple[str, float]], title: str, ylabel: str):

    dates = [pd.to_datetime(date + '-01') for date, _ in data]
    values = [value for _, value in data]
    
    plt.figure(figsize=(12, 6))
    
    # Calculate the average time delta between dates
    time_deltas = [dates[i+1] - dates[i] for i in range(len(dates)-1)]
    avg_delta = sum(time_deltas, timedelta()) / len(time_deltas)
    width = avg_delta.days  # Width in days

    # Create the bar chart with calculated width
    plt.bar(dates, values, width=width, align='center')
    
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    
    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.tight_layout()
    
    plt.savefig(f"{title.lower().replace(' ', '_')}_bar.png")
    plt.close()


if __name__ == "__main__":
    temporal_analysis()
    analyze_all_tech_stack()
