import numpy as np
from typing import Tuple
import pandas as pd

def get_xgboost_x_y(
    indices: list, 
    data: np.array,
    target_sequence_length,
    input_seq_len: int
    ) -> Tuple[np.array, np.array]:

    """
    Args:

        indices: List of index positions at which data should be sliced

        data: A univariate time series

        target_sequence_length: The forecasting horizon, m

        input_seq_len: The length of the model input, n

    Output: 

        all_x: np.array of shape (number of instances, input seq len)

        all_y: np.array of shape (number of instances, target seq len)

    """
    print("Preparing data..")

    # Loop over list of training indices
    for i, idx in enumerate(indices):

        # Slice data into instance of length input length + target length
        data_instance = data[idx[0]:idx[1]]

        x = data_instance[0:input_seq_len]

        assert len(x) == input_seq_len

        y = data_instance[input_seq_len:input_seq_len+target_sequence_length]

        # Create all_y and all_x objects in first loop iteration
        if i == 0:

            all_y = y.reshape(1, -1)

            all_x = x.reshape(1, -1)

        else:

            all_y = np.concatenate((all_y, y.reshape(1, -1)), axis=0)

            all_x = np.concatenate((all_x, x.reshape(1, -1)), axis=0)

    print("Finished preparing data!")

    return all_x, all_y


def load_data():

    # Read data
    spotclasses = pd.read_csv("HP_DRUM_LEVEL_revise-Statistical_Model-Extract.csv", delimiter=",")
    
#     list_of_column_names = []
    
#     for row in spotclasses:
 
        # adding the first row
#         list_of_column_names.append(row)
    list_of_column_names = list(spotclasses.columns)
 
        # breaking the loop after the
        # first iteration itself
#         break

    DATETIME = list_of_column_names[0]
    Mean = list_of_column_names[1]
    SD = list_of_column_names[2]
    Variance = list_of_column_names[3]
    Range = list_of_column_names[4]
    target_variable = list_of_column_names[5]
    
#     timestamp_col = "DATETIME"

    # Convert separator from "," to "." and make numeric
#     spotclasses[target_variable] = spotclasses[target_variable].str.replace(',', '.', regex=True)

    spotclasses.index = pd.to_datetime(spotclasses["DATETIME"])
    spotclasses[Mean] = pd.to_numeric(spotclasses["Mean"])
    spotclasses[SD] = pd.to_numeric(spotclasses["SD"])
    spotclasses[Variance] = pd.to_numeric(spotclasses["Variance"])
    spotclasses[Range] = pd.to_numeric(spotclasses["Range"])
    spotclasses[target_variable] = pd.to_numeric(spotclasses["Class"])

    # Convert HourDK to proper date time and make it index
#     spotclasses[timestamp_col] = pd.to_datetime(spotclasses[timestamp_col])
    
#     spotclasses.index = pd.to_datetime(spotclasses[timestamp_col])

    # Discard all cols except DKK prices
#     spotclasses = spotclasses[[target_variable]]
    spotclasses = spotclasses[[Mean, SD, Variance, Range, target_variable]]

    # Order by ascending time stamp
#     spotclasses.sort_values(by=timestamp_col, ascending=True, inplace=True)

    return spotclasses

def get_indices_entire_sequence(
    data: pd.DataFrame, 
    window_size: int, 
    step_size: int
    ) -> list:
        """
        Produce all the start and end index positions that is needed to produce
        the sub-sequences. 
        Returns a list of tuples. Each tuple is (start_idx, end_idx) of a sub-
        sequence. These tuples should be used to slice the dataset into sub-
        sequences. These sub-sequences should then be passed into a function
        that slices them into input and target sequences. 
        
        Args:
            data (pd.DataFrame): Partitioned data set, e.g. training data

            window_size (int): The desired length of each sub-sequence. Should be
                               (input_sequence_length + target_sequence_length)
                               E.g. if you want the model to consider the past 100
                               time steps in order to predict the future 50 
                               time steps, window_size = 100+50 = 150
            step_size (int): Size of each step as the data sequence is traversed 
                             by the moving window.
                             If 1, the first sub-sequence will be [0:window_size], 
                             and the next will be [1:window_size].
        Return:
            indices: a list of tuples
        """

        stop_position = len(data)-1 # 1- because of 0 indexing
        
        # Start the first sub-sequence at index position 0
        subseq_first_idx = 0
        
        subseq_last_idx = window_size
        
        indices = []
        
        while subseq_last_idx <= stop_position:

            indices.append((subseq_first_idx, subseq_last_idx))
            
            subseq_first_idx += step_size
            
            subseq_last_idx += step_size

        return indices