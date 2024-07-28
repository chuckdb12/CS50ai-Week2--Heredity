from heredity import *

def main():
    people = {
    'Harry': {'name': 'Harry', 'mother': 'Lily', 'father': 'James', 'trait': None},
    'James': {'name': 'James', 'mother': None, 'father': None, 'trait': True},
    'Lily': {'name': 'Lily', 'mother': None, 'father': None, 'trait': False}
    }
    print(joint_probability(people, {"Harry"}, {"James"}, {"James"}))

if __name__ == "__main__":
    main()