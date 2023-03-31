import argparse
import sys
from kubernetes import client, config
from tabulate import tabulate

def check_node_exists(node_name):
    field_selector = 'metadata.name='+node_name
    ret = v1.list_node(watch=False, field_selector=field_selector)
    if not ret.items:
        print(f"Node {node_name} does not exists")
        return sys.exit(1)

def check_namespace_exists(namespace):
    field_selector = 'metadata.name='+namespace
    ret = v1.list_namespace(watch=False, field_selector=field_selector)
    if not ret.items:
        print(f"Namespace {namespace} does not exists")
        return sys.exit(1)

def list_all_namespaces_pods(node_name=None,namespace=None):
    field_selector = ""
    if node_name:
        field_selector += f'spec.nodeName={node_name},'
    if namespace:
        field_selector += f'metadata.namespace={namespace}'

    ret = v1.list_pod_for_all_namespaces(watch=False,field_selector=field_selector)
    result = []
    for json_result in ret.items:
        if json_result.metadata.labels is None:
            labels = 0
        else:
            labels = len(json_result.metadata.labels)
        data = [json_result.metadata.name, labels, json_result.spec.node_name, json_result.metadata.namespace]
        result.append(data)
    print(tabulate(result , headers=['POD NAME', 'Number of Labels', 'Node Name', 'NAMESPACE']))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--node", help = "list all pods on specified  node")
    parser.add_argument("-ns", "--namespace", help = "list all pods on specified  namespace")
    args = parser.parse_args()

    try:
        config.list_kube_config_contexts()[1]
    except:
        print("It seems that current context is not set, please check your settings")
        sys.exit(1)

    config.load_kube_config()
    v1 = client.CoreV1Api()

    if args.node:
        check_node_exists(args.node)
    if args.namespace:
        check_namespace_exists(args.namespace)

    list_all_namespaces_pods(node_name=args.node,namespace=args.namespace)
