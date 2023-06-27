import os
import json
from typing import Dict, List
import pprint
from services import LABELS

out_dir = './aws_files'
# Create folders if they do not exist

def create_dirs(*dir_names: str) -> None:
    # create the parent folder if it does not exist starting being json_assets the base path
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for dir in dir_names:
        complete_path = f'{out_dir}/{dir}'
        if not os.path.exists(complete_path):
            os.makedirs(complete_path)


def parse_data_to_json(data: str):
    create_dirs('entities', 'relationships')
    _split_data_to_dicts(data)


def _split_data_to_dicts(data: str) -> Dict:

    """
    Dicts to store nodes and relationships. The format used is as follows:
    the label is the key and the value is list of entities for that specific label. same for rels.
    nodes : {
        'S3Bucket': [
            {}, {}, 
        ]
    }
    """
    nodes: Dict = {}
    rels: Dict = {}

    # the data is of type str where each json object is on a single line
    splitted_list = data.split('\n')

    # looping over the list of json objects in string and converting them to dict
    for item in splitted_list:
        dict_item = json.loads(item)

        # get the type of the node [relationship or node]
        type: str = dict_item.get('type', None)
        if type is not None:
            # if the object type is node, call parse node function
            if type == 'node':
                _parse_node(dict_item, nodes)
            # if the object type is relationship, call parse relationship function
            if type == 'relationship':
                _parse_relationship(dict_item, rels)

    # write relationships and nodes to json files
    write_parsed_dict_to_json(nodes, 'entities')
    write_parsed_dict_to_json(rels, 'relationships')


def _parse_node(dict_item: Dict, nodes: Dict) -> None:
    # get the list of labels from node object
    labels_list = dict_item.get('labels', None)

    # if there are no labels, skip the node
    if labels_list is None or len(labels_list) == 0: 
        return

    # get the list of directories in entities folder to look for a matching label
    entity_dirs = os.listdir(f'{out_dir}/entities/')

    # set the label as key for the node dict which will also be the folder name in entities
    key_label = ''
    for label in labels_list:
        if label in entity_dirs:
            key_label = label
            break
        else:
            key_label = labels_list[0]
    
    # get the parsed node dict 
    parsed_node = _generated_node_dict(dict_item)

    # create a list for the key in dict if not already present
    nodes.setdefault(key_label, [])

    # append the node to the node dict
    nodes[key_label].append(parsed_node)


def _generated_node_dict(unparsed_node: Dict) -> Dict:
    # create a new dict for the parsed node
    parsed_node = {
        'type': unparsed_node['type'],
        'id': unparsed_node['id'],
        'labels': unparsed_node['labels']
    }

    # if the node has properties then update the node 
    properties = unparsed_node.get('properties', None)
    if properties is None:
        return parsed_node
    
    parsed_node.update(properties)
    return parsed_node


def _parse_relationship(dict_item: Dict, rels: Dict) -> None:
    
    # get the parsed relationship dict 
    parsed_rel = _generate_rel_dict(dict_item)

    # get the relationships directory list 
    rel_dirs = os.listdir(f'{out_dir}/relationships/')

    # TODO: Sort relationships by which
    # get the label list from parsed relationship start
    labels_list = parsed_rel['start_labels'] if len(parsed_rel['start_labels']) > 0 else parsed_rel['end_labels']

    # if the end labels are empty as well, skip
    if len(labels_list) == 0:
        return 
    
    # get the key label 
    key_label = ''
    for label in labels_list:
        if label in rel_dirs:
            key_label = label
            break
        else:
            key_label = labels_list[0]
        
    # append the relationship to that key
    rels.setdefault(key_label, [])
    rels[key_label].append(parsed_rel)


def _generate_rel_dict(unparsed_rel: Dict) -> Dict:

    # some relationships do not have either firstseen or lastupdated...
    properties = unparsed_rel.get('properties', None)
    if properties is not None:
        firstseen = properties.get('firstseen', '')
        lastupdated = properties.get('lastupdated', '')
    else:
        firstseen = ''
        lastupdated = ''

    parsed = {
        'type': 'relationship',
        'id': unparsed_rel['id'],
        'label': unparsed_rel['label'],
        'firstseen': firstseen, 
        'lastupdated': lastupdated,
        'start_id': unparsed_rel['start']['id'],
        'start_labels': unparsed_rel['start']['labels'] if unparsed_rel['start'].get('labels') is not None else [],
        'end_id': unparsed_rel['end']['id'],
        'end_labels': unparsed_rel['end']['labels'] if unparsed_rel['end'].get('labels') is not None else []
    }

    return parsed

            
def write_parsed_dict_to_json(data: Dict, type: str) -> None:
    for key, value in data.items():
        
        # create a dict 
        out_dict = {
            type: value
        }
        
        # convert to json dump object
        json_dump = json.dumps(out_dict, indent=4)

        # create folder and filename
        if type == 'entities':
            create_dirs(f'{type}/{key}')
            filename = f'{out_dir}/{type}/{key}/{key}.json'
        else:
            create_dirs(f'{type}/{key}relations')
            filename = f'{out_dir}/{type}/{key}relations/relations.json'

        # write to json file
        with open(filename, 'w+') as f:
            f.write(json_dump)
        f.close()