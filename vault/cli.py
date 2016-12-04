from vault import Vault
import argparse

def main():
    parser = argparse.ArgumentParser(description="Store and lookup locally encrypted data stored in S3")
    parser.add_argument('name')
    parser.add_argument('value')
    parser.add_argument('-f', '--file')
    parser.add_argument('-p', '--prefix')
    parser.add_argument('-i', '--init')
    parser.add_argument('-b', '--bucket')
    parser.add_argument('-k', '--key-arn')
    print parser.parse()
