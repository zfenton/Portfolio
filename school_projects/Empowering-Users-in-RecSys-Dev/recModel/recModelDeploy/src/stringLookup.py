import json

def string_lookup(input_json):
    """_summary_

    Args:
        input_json (_type_): _description_
    """
    #print("Input JSON:", input_json)
    data = json.loads(input_json)
    
    HT = {}
    
    for i, val in enumerate(data['vocabulary']):
        HT[val] = i + 1
    
    # Perform string lookup
    # vocab_layer = tf.keras.layers.StringLookup(vocabulary=data['vocabulary'], oov_token=data['oov_token'])
    # output = vocab_layer()
    
    return HT
