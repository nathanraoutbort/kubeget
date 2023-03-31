from yaml.loader import SafeLoader
from kubernetes import client, config
from tabulate import tabulate
import argparse
import sys

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
    if namespace is not None and node_name is not None:
        ret = v1.list_pod_for_all_namespaces(watch=False, field_selector=f'spec.nodeName={node_name},metadata.namespace={namespace}')
    elif namespace:
        ret = v1.list_pod_for_all_namespaces(watch=False, field_selector=f'metadata.namespace={namespace}')
    elif node_name:
        ret = v1.list_pod_for_all_namespaces(watch=False, field_selector=f'spec.nodeName={node_name}')
    elif node_name is None and namespace is None:
        ret = v1.list_pod_for_all_namespaces(watch=False)
    result = []
    for i in ret.items:
        if i.metadata.labels is None:
            labels = 0
        else:
            labels = len(i.metadata.labels)
        t = [i.metadata.name, labels, i.spec.node_name, i.metadata.namespace]
        result.append(t)
    print(tabulate(result , headers=['POD NAME', 'Number of Labels', 'Node Name', 'NAMESPACE']))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--node", help = "list all pods on specified node")
    parser.add_argument("-ns", "--namespace", help = "list all pods on specified namespace")
    args = parser.parse_args()

    try:
        config.list_kube_config_contexts()[1]
    except:
        print("It seems no contex is currently set")

    config.load_kube_config()
    v1 = client.CoreV1Api()

    if args.node is not None and args.namespace is not None:
        check_namespace_exists(args.namespace)
        check_node_exists(args.node)
        list_all_namespaces_pods(node_name=args.node,namespace=args.namespace)
    elif args.node:
        check_node_exists(args.node)
        list_all_namespaces_pods(node_name=args.node)
    elif args.namespace:
        check_node_exists(args.node)
        list_all_namespaces_pods(namespace=args.namespace)
    elif args.node is None and args.namespace is None:
        list_all_namespaces_pods()


