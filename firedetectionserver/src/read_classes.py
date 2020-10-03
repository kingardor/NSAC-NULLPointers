def get_class_details():
    try:
        f = open('./classes.txt', 'r')
        classes_list = f.read().split('\n')
        num_classes = len(classes_list)
        class_names = classes_list
        return num_classes, class_names
    except FileNotFoundError:
        print('Place classes.txt in CenternetROOT/src directory.')
