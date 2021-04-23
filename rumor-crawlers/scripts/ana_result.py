import sys
import os

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_path, '../app'))


if __name__ == "__main__":
    from models.aws.ddb.rumor_model import RumorModel

    rumors = dict()
    for s in ["cdc", "mofa", "fda", "mygopen", "tfc"]:
        for rumor in RumorModel.scan(RumorModel.source.startswith(s)):
            if rumor.source not in rumors:
                rumors[rumor.source] = 1
            else:
                rumors[rumor.source] += 1

    print(rumors)

    # for s in ["cdc"]:
    #   for rumor in RumorModel.scan(RumorModel.source.startswith(s)):
    #       rumor.delete()

    rumors = list()
    for rumor in RumorModel.scan(RumorModel.rumors == [""]):
        rumors.append(rumor)

    for rumor in rumors:
        print(rumor.id, rumor.link, rumor.tags)
