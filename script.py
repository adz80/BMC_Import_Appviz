#   /bin/python3

# Description:
#   This script is used to import a BMC extract and convert it into an AppViz import format.
#   



import sys          # used to write to CSV file.
import argparse     # for parsing command line arguments.
import pandas as pd # used to parse CSV file.
import numpy as np  # used to perform csv manipulations.
from re import search # Used to allow regex to be used in Pandas dataframe.



def args_parser():
    parser = argparse.ArgumentParser(description='This script was made for Harry. Enjoy!!! ')
    parser.add_argument('-f', '--file', help='The file to be parsed.', required=True)
    parser.add_argument('-o', '--output', help='The output file.', required=True)
    parser.add_argument('-a', '--application_name', help='the application name to be converted to Appviz', required=True)
    args = parser.parse_args()
    return args

def main():
    args = args_parser()
    data = pd.read_csv(args.file)
    header = data.columns


    # load csv data into Pandas dataframe.
    df = pd.DataFrame(data, columns=header)
    
    # format table headers to lowercase and spaces to underscores.
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]

    # Remove loopback ip address from dataframe.
    df = df[df["local_ip"].str.contains("^127", regex=True)==False]
    df = df[df["remote_ip"].str.contains("^127", regex=True)==False]

    # remove all rows that have the same ip address as the source and destination ip address.
    df = df[df["local_ip"] != df["remote_ip"]]
    
    # Remove all ipv6 loopback addresses.
    df = df[df["local_ip"].str.contains("^::1", regex=True)==False]

    # if the dataframe fields of souurce port and destination port are reversed, reverse them as well as IP.

    df.local_port, df.remote_port, df.local_ip, df.remote_ip = np.where(df.local_port < df.remote_port, 
        [df.remote_port, df.local_port, df.remote_ip, df.local_ip], 
        [df.local_port, df.remote_port, df.local_ip, df.remote_ip]
    )

    # create a new column called "application_name" and name it from the CLI Arg -n.
    df.insert(0, "application_name", args.application_name)

    # Select only the fields that are needed.
    df = df[['application_name', 'local_ip', 'remote_ip', 'remote_port']]

    # rename the header of the dataframe to match the format of the Appviz application.
    df.rename(columns={
        'application_name': 'Application name',
        'local_ip': 'Source IP',
        'remote_ip': 'Destination IP',
        'remote_port': 'Service'
        }, 
    inplace=True
    )

    # write CSV file to disk.
    print (df)   
    df.to_csv(args.output, index=False)    


if __name__ == "__main__":
    main()
    sys.exit(0)

