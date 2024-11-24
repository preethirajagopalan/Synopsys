import yaml

def yaml_loader(filepath):
    #loads a yaml file
    with open(filepath, "r") as file_descriptor:
        data = yaml.load(file_descriptor)
    return data
def yaml_dump(filepath, data):
    #dumps data to yaml file
    with open(filepath, "w") as file_descriptor:
        yaml.dump(data)

if __name__ == "__main__":
    file_path = "test.yaml"
    data = yaml_loader(filepath)
    print(data)
